# Soulnote - AI情感日记工具 🌟

一个基于AI的情感日记工具，支持语音和文本输入，生成艺术化的情感海报和哲学思考。

## ✨ 主要特性

- 🎤 **语音录制** - 录制你的想法和感受
- ✍️ **文本输入** - 写下你的日记条目  
- 🧠 **AI情感分析** - 使用在线AI服务分析情感
- 🎨 **艺术海报** - 生成美丽的可视化图形
- 📖 **哲学思考** - 基于情感生成深刻的反思
- 📱 **社交分享** - 导出为各种社交媒体格式

## 🚀 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 配置AI服务 (可选)
```bash
# 复制配置文件
cp .env.example .env

# 编辑配置文件，添加API密钥
nano .env
```

支持的AI提供商：
- **OpenAI GPT** - 设置 `OPENAI_API_KEY`
- **Anthropic Claude** - 设置 `ANTHROPIC_API_KEY`  
- **Mock模式** - 无需API密钥，用于测试

### 启动应用
```bash
python backend/app.py
```

访问 http://localhost:5002 开始使用！

## 🔧 配置选项

### AI提供商配置

#### OpenAI (推荐)
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

#### Anthropic Claude
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

#### 测试模式
```env
AI_PROVIDER=mock
```

## 📱 使用方法

### 文本日记
1. 选择"文本输入"标签
2. 输入你的想法和感受
3. 点击"分析情感"
4. 查看情感分析结果和生成的海报

### 语音日记
1. 选择"语音录制"标签
2. 点击"开始录制"并说出你的想法
3. 点击"停止录制"
4. 点击"分析情感"查看结果

## 🌐 生产部署

### Docker部署
```bash
docker build -t soulnote .
docker run -p 5002:5002 -e OPENAI_API_KEY=your-key soulnote
```

### 传统部署
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 backend.app:app
```

详细部署指南请查看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 🧪 测试

```bash
# 运行API测试
python test_api.py

# 手动测试健康检查
curl http://localhost:5002/api/health
```

## 📂 项目结构

```
Soulnote/
├── backend/
│   └── app.py              # Flask API服务器
├── models/
│   ├── emotion_analyzer.py # 情感分析逻辑
│   └── online_ai_client.py # 在线AI客户端
├── utils/
│   ├── audio_processor.py  # 音频处理
│   ├── poster_generator.py # 海报生成
│   └── card_exporter.py    # 社交媒体导出
├── frontend/
│   └── index.html          # 前端界面
├── static/                 # 静态资源
├── uploads/                # 音频上传
├── output/                 # 生成的海报
└── config.py              # 配置管理
```

## 🔒 隐私和安全

- 支持本地部署，数据完全控制
- API密钥安全存储在环境变量中
- 音频文件本地处理，不上传到第三方
- 支持HTTPS和访问控制

## 💰 成本估算

使用在线AI服务的大致成本：
- OpenAI GPT-3.5: ~$0.001-0.002 每次分析
- OpenAI GPT-4: ~$0.01-0.03 每次分析
- Anthropic Claude: 类似定价

Mock模式完全免费，适合测试和演示。

## 🛠️ 技术栈

- **后端**: Python 3.8+, Flask
- **AI**: OpenAI API, Anthropic API
- **音频**: SpeechRecognition, Librosa, PyDub
- **图像**: Pillow, Matplotlib
- **前端**: HTML, CSS, JavaScript

## 📖 API文档

### 健康检查
```
GET /api/health
```

### 文本情感分析
```
POST /api/analyze/text
Content-Type: application/json

{
  "text": "你的文本内容"
}
```

### 语音情感分析
```
POST /api/analyze/voice
Content-Type: multipart/form-data

audio: [音频文件]
```

### 生成海报
```
POST /api/generate/poster
Content-Type: application/json

{
  "text": "原始文本",
  "primary_emotion": "主要情感",
  "emotions": {...},
  "philosophical_note": "哲学思考"
}
```

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- OpenAI 和 Anthropic 提供AI服务
- 开源社区的支持

---

**🌟 享受你的情感日记之旅！**
