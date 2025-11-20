# OpenAI Realtime API 设置指南

## 🎙️ 什么是OpenAI Realtime API？

OpenAI Realtime API是OpenAI最新推出的实时语音交互API，支持：
- **实时语音识别** - 边说边转录
- **实时情感分析** - 即时理解情感状态
- **实时语音合成** - AI可以立即语音回应
- **低延迟交互** - 接近人类对话的自然体验

## 🚀 如何获取和配置API密钥

### 步骤1：获取OpenAI API密钥

1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录你的OpenAI账户（需要付费账户）
3. 点击 "Create new secret key"
4. 复制生成的API密钥（格式：sk-...）

### 步骤2：配置API密钥

#### 方法A：环境变量（推荐）
```bash
# macOS/Linux
export OPENAI_API_KEY="sk-your-actual-api-key-here"

# Windows
set OPENAI_API_KEY=sk-your-actual-api-key-here
```

#### 方法B：创建.env文件
```bash
# 在项目根目录创建.env文件
echo "OPENAI_API_KEY=sk-your-actual-api-key-here" > .env
```

### 步骤3：重启应用
```bash
# 设置API密钥后重启
python realtime_app.py
```

## 💰 成本估算

OpenAI Realtime API定价（2024年11月）：
- **输入音频**: ~$0.06 per minute
- **输出音频**: ~$0.24 per minute  
- **文本处理**: 标准GPT-4定价

**示例成本**：
- 5分钟对话 ≈ $1.50
- 1小时使用 ≈ $18
- 每天10分钟 ≈ $3/天

## 🎯 功能对比

| 功能 | 无API密钥 | 有Realtime API |
|------|-----------|----------------|
| 语音录制 | ✅ 基础录制 | ✅ 实时流式 |
| 语音转文字 | ✅ 离线处理 | ✅ 实时转录 |
| 情感分析 | ✅ 模拟结果 | ✅ 实时分析 |
| AI回应 | ✅ 文字回应 | ✅ 语音回应 |
| 延迟 | 5-10秒 | <1秒 |
| 体验 | 基础版 | 专业版 |

## 🛠️ 配置完成后的功能

### 实时交互流程：
1. **开始对话** - 点击"开始实时分析"
2. **边说边转录** - 实时显示你说的话
3. **即时情感分析** - 动态更新情感状态
4. **AI语音回应** - AI用语音回应你的情感
5. **生成艺术海报** - 基于对话内容创建视觉作品

### 高级功能：
- 🎯 **智能打断检测** - AI知道何时该回应
- 🎨 **情感可视化** - 实时情感波动图
- 🎭 **多情感并存** - 识别复杂情感状态
- 🧘 **深度哲学思考** - AI提供个性化洞察

## 🔧 故障排除

### 常见问题：

**Q: 显示"未检测到OpenAI API密钥"**
A: 
```bash
# 检查环境变量是否设置
echo $OPENAI_API_KEY

# 重新设置
export OPENAI_API_KEY="sk-your-key-here"
```

**Q: API密钥无效**
A: 确保密钥格式正确，以"sk-"开头，并且账户有足够余额

**Q: 实时API连接失败**
A: 检查网络连接，确保防火墙允许WebSocket连接

**Q: 音频权限问题**
A: 在浏览器中允许麦克风访问权限

## 🌟 测试API密钥

配置后可以运行测试：
```bash
# 测试API连接
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# 启动应用
python realtime_app.py
```

看到以下信息表示成功：
```
🎙️ OpenAI Realtime API已启用
✨ 支持实时语音情感分析
```

## 🚀 生产部署注意事项

1. **安全性**
   - 不要将API密钥提交到Git
   - 使用环境变量或安全的密钥管理服务
   - 设置API使用限额

2. **成本控制**
   - 监控API使用量
   - 设置预算警报
   - 实现会话时长限制

3. **用户体验**
   - 提供清晰的录音指示
   - 显示实时连接状态
   - 优雅处理网络中断

## 📞 支持

如果遇到问题：
1. 检查OpenAI账户余额
2. 验证API密钥权限
3. 查看应用日志
4. 测试网络连接

---

🎉 配置完成后，你将拥有一个专业级的实时AI情感分析工具！
