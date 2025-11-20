# 体验版API配置说明

## 🎉 免费体验DeepSeek AI功能

为了让大家体验完整的AI情感分析功能，我们提供了体验版API密钥。

### 快速开始

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd Soulnote.v1

# 2. 创建.env文件
echo "DEEPSEEK_API_KEY=sk-EXPERIENCE_KEY_HERE" > .env

# 3. 安装依赖并运行
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python soulnote_complete.py
```

### 🔑 体验密钥获取

**方式1：扫码获取**
（添加你的二维码或联系方式）

**方式2：邮件申请**
发送邮件到：your-email@example.com
主题：申请Soulnote体验密钥

**方式3：课程群获取**
在课程群中私信获取

### ⚠️ 使用须知

- 每个密钥限制调用1000次
- 仅用于学习和体验目的
- 请勿滥用或分享给他人
- 如需长期使用，请申请个人密钥

### 💡 获取个人API密钥

1. 访问 https://platform.deepseek.com/
2. 注册账户（新用户送$5额度）
3. 创建API密钥
4. 替换.env文件中的密钥

### 🎨 功能特色

有了真实API密钥，你将体验到：
- 🧠 **智能情感识别**：准确分析复杂情感状态
- 💭 **个性化反思**：基于你的具体内容生成独特洞察  
- 🎯 **上下文理解**：AI理解你的情感背景和细微差别
- 📖 **哲学思考**：深度的情感哲学分析

### 📊 成本参考

DeepSeek定价非常友好：
- 输入：~$0.14/1M tokens
- 输出：~$0.28/1M tokens
- 每次分析成本：~$0.001-0.005
- $5可支持1000-5000次分析
