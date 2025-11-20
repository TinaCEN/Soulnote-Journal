"""
OpenAI Realtime API Client - 实时语音交互
支持实时语音输入、处理和响应
"""

import asyncio
import websockets
import json
import base64
import os
from typing import Dict, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class OpenAIRealtimeClient:
    """OpenAI Realtime API客户端"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.ws_url = "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-10-01"
        self.websocket = None
        self.session_config = {
            "modalities": ["text", "audio"],
            "instructions": """你是一个情感分析专家和哲学思考者。
            分析用户的语音输入，识别情感，并提供深刻的哲学思考。
            用温暖、理解的语气回应，并提供情感洞察。""",
            "voice": "alloy",
            "input_audio_format": "pcm16",
            "output_audio_format": "pcm16",
            "input_audio_transcription": {
                "model": "whisper-1"
            },
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 200
            },
            "tools": [
                {
                    "type": "function",
                    "name": "analyze_emotions",
                    "description": "分析文本中的情感",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string"},
                            "primary_emotion": {"type": "string"},
                            "emotions": {
                                "type": "object",
                                "additionalProperties": {"type": "number"}
                            },
                            "intensity": {"type": "string"},
                            "philosophical_note": {"type": "string"}
                        },
                        "required": ["text", "primary_emotion", "emotions", "philosophical_note"]
                    }
                }
            ]
        }
        
        # 事件回调
        self.on_audio_received: Optional[Callable] = None
        self.on_transcript_received: Optional[Callable] = None
        self.on_emotion_analysis: Optional[Callable] = None
        
    async def connect(self):
        """连接到OpenAI Realtime API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "OpenAI-Beta": "realtime=v1"
        }
        
        try:
            self.websocket = await websockets.connect(
                self.ws_url,
                extra_headers=headers
            )
            
            # 发送会话配置
            await self.send_session_update()
            
            # 启动消息监听
            asyncio.create_task(self.listen_for_messages())
            
            logger.info("已连接到OpenAI Realtime API")
            return True
            
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return False
    
    async def disconnect(self):
        """断开连接"""
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
    
    async def send_session_update(self):
        """发送会话配置更新"""
        message = {
            "type": "session.update",
            "session": self.session_config
        }
        await self.websocket.send(json.dumps(message))
    
    async def send_audio_data(self, audio_data: bytes):
        """发送音频数据"""
        # 将音频数据编码为base64
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        message = {
            "type": "input_audio_buffer.append",
            "audio": audio_base64
        }
        await self.websocket.send(json.dumps(message))
    
    async def commit_audio_buffer(self):
        """提交音频缓冲区"""
        message = {"type": "input_audio_buffer.commit"}
        await self.websocket.send(json.dumps(message))
    
    async def send_text_message(self, text: str):
        """发送文本消息"""
        message = {
            "type": "conversation.item.create",
            "item": {
                "type": "message",
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": text
                    }
                ]
            }
        }
        await self.websocket.send(json.dumps(message))
        
        # 创建响应
        response_message = {
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"],
                "instructions": "分析用户的情感并提供哲学思考"
            }
        }
        await self.websocket.send(json.dumps(response_message))
    
    async def listen_for_messages(self):
        """监听来自API的消息"""
        try:
            async for message_str in self.websocket:
                message = json.loads(message_str)
                await self.handle_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info("WebSocket连接已关闭")
        except Exception as e:
            logger.error(f"消息监听错误: {e}")
    
    async def handle_message(self, message: Dict):
        """处理来自API的消息"""
        message_type = message.get("type")
        
        if message_type == "session.created":
            logger.info("会话已创建")
            
        elif message_type == "session.updated":
            logger.info("会话已更新")
            
        elif message_type == "input_audio_buffer.speech_started":
            logger.info("检测到语音开始")
            
        elif message_type == "input_audio_buffer.speech_stopped":
            logger.info("检测到语音停止")
            
        elif message_type == "conversation.item.input_audio_transcription.completed":
            # 语音转录完成
            transcript = message.get("transcript", "")
            if self.on_transcript_received:
                await self.on_transcript_received(transcript)
                
        elif message_type == "response.audio.delta":
            # 接收到音频响应
            audio_data = message.get("delta", "")
            if audio_data and self.on_audio_received:
                await self.on_audio_received(base64.b64decode(audio_data))
                
        elif message_type == "response.function_call_arguments.done":
            # 函数调用完成
            arguments = message.get("arguments", "")
            try:
                args_data = json.loads(arguments)
                if self.on_emotion_analysis:
                    await self.on_emotion_analysis(args_data)
            except json.JSONDecodeError:
                logger.error("无法解析函数参数")
                
        elif message_type == "error":
            logger.error(f"API错误: {message}")
            
    def set_audio_callback(self, callback: Callable):
        """设置音频接收回调"""
        self.on_audio_received = callback
        
    def set_transcript_callback(self, callback: Callable):
        """设置转录回调"""
        self.on_transcript_received = callback
        
    def set_emotion_callback(self, callback: Callable):
        """设置情感分析回调"""
        self.on_emotion_analysis = callback


class RealtimeAudioProcessor:
    """实时音频处理器"""
    
    def __init__(self):
        self.sample_rate = 24000  # OpenAI Realtime API要求的采样率
        self.chunk_size = 1024
        
    def convert_to_pcm16(self, audio_data: bytes) -> bytes:
        """转换音频数据为PCM16格式"""
        # 这里需要根据输入音频格式进行转换
        # 简化实现，假设输入已经是正确格式
        return audio_data
        
    def process_microphone_data(self, audio_chunk: bytes) -> bytes:
        """处理麦克风数据"""
        # 转换为API要求的格式
        return self.convert_to_pcm16(audio_chunk)


async def create_realtime_session(api_key: str) -> OpenAIRealtimeClient:
    """创建实时API会话"""
    client = OpenAIRealtimeClient(api_key)
    
    if await client.connect():
        return client
    else:
        raise Exception("无法连接到OpenAI Realtime API")


# 情感分析增强版本
class RealtimeEmotionAnalyzer:
    """基于Realtime API的情感分析器"""
    
    def __init__(self, api_key: str):
        self.client = OpenAIRealtimeClient(api_key)
        self.current_emotions = {}
        self.transcript_buffer = ""
        
    async def start_analysis_session(self):
        """开始分析会话"""
        await self.client.connect()
        
        # 设置回调
        self.client.set_transcript_callback(self.handle_transcript)
        self.client.set_emotion_callback(self.handle_emotion_analysis)
        
    async def handle_transcript(self, transcript: str):
        """处理转录文本"""
        self.transcript_buffer += transcript + " "
        logger.info(f"转录: {transcript}")
        
    async def handle_emotion_analysis(self, analysis_data: Dict):
        """处理情感分析结果"""
        self.current_emotions = analysis_data
        logger.info(f"情感分析: {analysis_data}")
        
    async def analyze_voice_realtime(self, audio_data: bytes):
        """实时分析语音"""
        await self.client.send_audio_data(audio_data)
        
    async def get_analysis_result(self) -> Dict:
        """获取分析结果"""
        return {
            "transcript": self.transcript_buffer.strip(),
            "emotions": self.current_emotions,
            "timestamp": "2025-11-04T16:00:00"
        }
        
    async def close(self):
        """关闭会话"""
        await self.client.disconnect()
