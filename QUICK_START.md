# 🚀 队友快速开始指南

## 📥 第一步：获取项目

```bash
# 1. 克隆项目
git clone https://github.com/TinaCEN/Soulnote-Journal.git
cd Soulnote-Journal

# 2. 安装依赖
npm install

# 3. 启动项目
npx expo start
```

## 📱 第二步：测试当前功能

1. 在手机上下载 **Expo Go** app
2. 扫描终端显示的二维码
3. 测试当前的演示功能：
   - 点击录音按钮
   - 观看颜色变化效果
   - 体验UI动画

## 🛠 第三步：开始开发

### 优先开发顺序：

#### 1️⃣ 真实录音功能 (Week 1)
- 文件：`services/AudioService.js`
- 需要：实现真实的语音录制
- 参考：代码中的TODO注释

#### 2️⃣ 情感分析AI (Week 2)  
- 文件：`services/EmotionAnalysisService.js`
- 需要：申请Azure或IBM Watson API
- 功能：分析语音情感

#### 3️⃣ 视觉艺术生成 (Week 3)
- 文件：需要创建 `components/EmotionalArt.js`
- 技术：react-native-svg + 动画

#### 4️⃣ GPT集成 (Week 4)
- 文件：`services/GPTService.js` 
- 需要：申请OpenAI API密钥
- 功能：生成哲学回应

## 📚 完整指南

详细的开发指南请查看：**[DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)**

## 🆘 遇到问题？

1. 检查 `DEVELOPMENT_GUIDE.md` 中的常见问题解决方案
2. 查看各个服务文件中的TODO注释
3. 参考Expo官方文档：https://docs.expo.dev/

## 🎯 项目愿景

> "It's not just a journal — it's a mirror that feels."

我们在创造一个真正能够理解和回应情感的AI应用，让技术与人文相结合，为用户提供独特的情感表达和反思体验。

**加油！期待看到你的创意实现！** 🌟
