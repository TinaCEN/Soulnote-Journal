"""
Audio Processor - Handle voice recording and waveform generation
"""

import speech_recognition as sr
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

# Try to import librosa, but don't fail if it's not available
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("Warning: librosa not available. Waveform features will be limited.")


class AudioProcessor:
    """Process audio files for speech-to-text and waveform visualization"""
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    def speech_to_text(self, audio_path: Path) -> str:
        """
        Convert speech audio to text with improved format handling
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Transcribed text
        """
        try:
            print(f"🔍 Checking audio file: {audio_path}")
            print(f"   File exists: {audio_path.exists()}")
            if audio_path.exists():
                print(f"   File size: {audio_path.stat().st_size} bytes")
            
            # Method 1: Try direct recognition first
            try:
                print("🎤 Attempting direct speech recognition...")
                with sr.AudioFile(str(audio_path)) as source:
                    audio_data = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio_data, language='zh-CN')
                    print(f"✅ Direct transcription successful: '{text}'")
                    return text
            except Exception as direct_error:
                print(f"⚠️ Direct recognition failed: {direct_error}")
            
            # Method 2: Try FFmpeg subprocess conversion (most reliable)
            converted_path = None
            try:
                print("� Attempting FFmpeg conversion...")
                import subprocess
                import os
                
                converted_path = audio_path.with_suffix('.processed.wav')
                
                # Try ffmpeg conversion
                cmd = [
                    'ffmpeg', '-i', str(audio_path),
                    '-ar', '16000',  # 16kHz sample rate
                    '-ac', '1',      # Mono
                    '-f', 'wav',     # WAV format
                    '-y',            # Overwrite existing
                    str(converted_path)
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and converted_path.exists():
                    print("✅ FFmpeg conversion successful")
                    with sr.AudioFile(str(converted_path)) as source:
                        audio_data = self.recognizer.record(source)
                        text = self.recognizer.recognize_google(audio_data, language='zh-CN')
                        print(f"✅ FFmpeg transcription successful: '{text}'")
                        converted_path.unlink()  # Clean up
                        return text
                else:
                    print(f"⚠️ FFmpeg failed: {result.stderr}")
                    
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as ffmpeg_error:
                print(f"⚠️ FFmpeg not available or failed: {ffmpeg_error}")
                if converted_path and converted_path.exists():
                    converted_path.unlink()
            
            # Method 3: Try pydub conversion
            try:
                print("🔄 Trying pydub conversion...")
                from pydub import AudioSegment
                import io
                
                # Load the audio file (handles various formats)
                print("🎵 Loading audio file with pydub...")
                audio = AudioSegment.from_file(str(audio_path))
                
                # Convert to proper format
                audio = audio.set_frame_rate(16000).set_channels(1)
                
                # Export as WAV format in memory
                wav_io = io.BytesIO()
                audio.export(wav_io, format='wav')
                wav_io.seek(0)
                
                print("🎤 Converting speech to text...")
                with sr.AudioFile(wav_io) as source:
                    audio_data = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio_data, language='zh-CN')
                    print(f"✅ Pydub transcription successful: '{text}'")
                    return text
                    
            except Exception as pydub_error:
                print(f"❌ Pydub conversion failed: {pydub_error}")
            
            # Method 4: Try without language specification
            try:
                print("🌐 Trying recognition without language specification...")
                with sr.AudioFile(str(audio_path)) as source:
                    audio_data = self.recognizer.record(source)
                    text = self.recognizer.recognize_google(audio_data)
                    print(f"✅ Generic transcription successful: '{text}'")
                    return text
            except Exception as generic_error:
                print(f"⚠️ Generic recognition failed: {generic_error}")
            
            print("❌ All transcription methods failed")
            return "抱歉，无法识别音频内容。请尝试：\n1. 说话更清晰\n2. 减少背景噪音\n3. 使用文字输入模式"
                
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return "无法理解音频内容，请重新录制或尝试文字输入"
        except sr.RequestError as e:
            print(f"❌ Could not request results; {e}")
            return f"语音识别服务错误：{e}"
        except Exception as e:
            print(f"❌ Error processing audio: {e}")
            import traceback
            traceback.print_exc()
            return "音频处理出错，请重试"
    
    def generate_waveform_data(
        self,
        audio_path: Path,
        num_points: int = 200
    ) -> List[float]:
        """
        Generate waveform data for visualization
        
        Args:
            audio_path: Path to audio file
            num_points: Number of data points to generate
            
        Returns:
            List of amplitude values
        """
        if not LIBROSA_AVAILABLE:
            print("Librosa not available, returning placeholder waveform")
            # Return a nice-looking sine wave as placeholder
            return [0.5 + 0.3 * np.sin(i * 0.1) for i in range(num_points)]
        
        try:
            # Load audio file
            y, sr_rate = librosa.load(str(audio_path), sr=None)
            
            # Calculate RMS energy for smoother visualization
            hop_length = len(y) // num_points
            if hop_length < 1:
                hop_length = 1
            
            rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
            
            # Normalize to 0-1 range
            if len(rms) > 0:
                rms = rms / np.max(rms) if np.max(rms) > 0 else rms
            
            # Ensure we have exactly num_points
            if len(rms) > num_points:
                rms = rms[:num_points]
            elif len(rms) < num_points:
                rms = np.pad(rms, (0, num_points - len(rms)), mode='constant')
            
            return rms.tolist()
        
        except Exception as e:
            print(f"Error generating waveform: {e}")
            # Return default waveform
            return [0.5] * num_points
    
    def get_audio_features(self, audio_path: Path) -> Dict:
        """
        Extract audio features for artistic visualization
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dictionary with audio features
        """
        if not LIBROSA_AVAILABLE:
            print("Librosa not available, returning default audio features")
            return {
                'tempo': 120.0,
                'spectral_centroid': 1000.0,
                'spectral_rolloff': 2000.0,
                'zero_crossing_rate': 0.1,
                'duration': 0.0
            }
        
        try:
            y, sr_rate = librosa.load(str(audio_path), sr=None)
            
            # Extract features
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr_rate)
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr_rate))
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr_rate))
            zero_crossing_rate = np.mean(librosa.feature.zero_crossing_rate(y))
            
            return {
                'tempo': float(tempo),
                'spectral_centroid': float(spectral_centroid),
                'spectral_rolloff': float(spectral_rolloff),
                'zero_crossing_rate': float(zero_crossing_rate),
                'duration': len(y) / sr_rate
            }
        
        except Exception as e:
            print(f"Error extracting audio features: {e}")
            return {
                'tempo': 120.0,
                'spectral_centroid': 1000.0,
                'spectral_rolloff': 2000.0,
                'zero_crossing_rate': 0.1,
                'duration': 0.0
            }
