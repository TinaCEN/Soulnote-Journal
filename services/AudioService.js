import { Audio } from 'expo-av';
import * as FileSystem from 'expo-file-system';

/**
 * AudioService - 处理语音录制功能
 * 
 * TODO for teammate:
 * 1. 实现真实的语音录制
 * 2. 添加录音权限检查
 * 3. 音频格式转换为AI分析需要的格式
 * 4. 错误处理和用户反馈
 */

class AudioService {
  constructor() {
    this.recording = null;
    this.isRecording = false;
  }

  // 检查录音权限
  async requestPermissions() {
    try {
      const permission = await Audio.requestPermissionsAsync();
      return permission.status === 'granted';
    } catch (error) {
      console.error('Permission request failed:', error);
      return false;
    }
  }

  // 开始录音
  async startRecording() {
    try {
      // TODO: 实现录音逻辑
      console.log('Starting recording...');
      
      // 示例代码框架：
      // await Audio.setAudioModeAsync({
      //   allowsRecordingIOS: true,
      //   playsInSilentModeIOS: true,
      // });
      
      // const { recording } = await Audio.Recording.createAsync(
      //   Audio.RECORDING_OPTIONS_PRESET_HIGH_QUALITY
      // );
      
      // this.recording = recording;
      // this.isRecording = true;
      
      return true;
    } catch (error) {
      console.error('Failed to start recording:', error);
      return false;
    }
  }

  // 停止录音
  async stopRecording() {
    try {
      // TODO: 实现停止录音逻辑
      console.log('Stopping recording...');
      
      // 示例代码框架：
      // if (this.recording) {
      //   await this.recording.stopAndUnloadAsync();
      //   const uri = this.recording.getURI();
      //   this.recording = null;
      //   this.isRecording = false;
      //   return uri;
      // }
      
      return null;
    } catch (error) {
      console.error('Failed to stop recording:', error);
      return null;
    }
  }

  // 获取录音状态
  getRecordingStatus() {
    return this.isRecording;
  }

  // 播放录音（用于测试）
  async playRecording(uri) {
    try {
      // TODO: 实现播放逻辑
      console.log('Playing recording:', uri);
      
      // 示例代码框架：
      // const { sound } = await Audio.Sound.createAsync({ uri });
      // await sound.playAsync();
      
    } catch (error) {
      console.error('Failed to play recording:', error);
    }
  }
}

export default new AudioService();
