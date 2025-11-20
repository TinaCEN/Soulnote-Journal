# Soulnote项目设置指南

## teammate使用步骤

### 1. 环境准备
```bash
# 克隆项目后
cd Soulnote.v1

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 系统依赖
```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg
```

### 3. API配置
```bash
# 复制环境文件
cp .env.example .env

# 编辑.env文件，添加你的DeepSeek API密钥
# DEEPSEEK_API_KEY=sk-your-key-here
```

### 4. 运行应用
```bash
python soulnote_complete.py
```

访问: http://localhost:5007

## 重要提醒

1. **API密钥**: 需要自己的DeepSeek账户和API密钥
2. **FFmpeg**: 必须安装才能使用语音功能  
3. **虚拟环境**: 建议使用独立的Python环境
4. **充值**: DeepSeek需要充值才能使用AI功能

## 当前功能状态

✅ **完整可用**:
- 语音录制和识别
- 文字输入分析
- 海报生成
- DeepSeek AI集成

🎨 **待优化**:
- UI/UX设计
- 响应式布局
- 动画效果
- 海报样式
