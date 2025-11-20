# 🔒 GitHub上传安全指南

## ⚠️ 重要警告

**绝对不要**将API密钥直接写在代码中上传到GitHub！

## 🛡️ 安全的做法

### 1. 检查敏感信息
上传前，确保代码中没有硬编码的API密钥：

```bash
# 搜索可能的API密钥
grep -r "sk-" . --exclude-dir=venv
grep -r "api_key" . --exclude-dir=venv
```

### 2. 使用.env文件
```bash
# 创建.env文件（不会上传）
echo "DEEPSEEK_API_KEY=你的密钥" > .env

# 确保.gitignore包含.env
echo ".env" >> .gitignore
```

### 3. 验证.gitignore
```bash
# 检查哪些文件会被上传
git status
git ls-files --ignored --exclude-standard

# 确保.env不在待上传列表中
```

## 📤 安全上传步骤

```bash
# 1. 添加所有文件
git add .

# 2. 检查状态（确保.env不在列表中）
git status

# 3. 提交
git commit -m "Add Soulnote AI emotional journaling tool"

# 4. 推送
git push origin main
```

## 🔍 如果意外上传了密钥

### 立即行动：
1. **撤销提交**（如果还没推送）
```bash
git reset --soft HEAD~1
git reset HEAD .env
```

2. **删除密钥并生成新的**
- 登录DeepSeek控制台
- 删除泄露的密钥
- 生成新密钥

3. **清理Git历史**（如果已推送）
```bash
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch .env' \
--prune-empty --tag-name-filter cat -- --all
```

## ✅ 当前项目状态

- ✅ 所有硬编码密钥已移除
- ✅ .env文件已创建（包含你的密钥）
- ✅ .gitignore已配置
- ✅ 代码支持从环境变量读取密钥
- ✅ 演示模式在无密钥时自动启用

## 👥 团队协作

### 给teammate：
1. 分享你的密钥（私下发送，不要通过GitHub）
2. 让他们创建自己的.env文件
3. 或者让他们使用演示模式开发

### 给老师：
- 老师直接运行演示模式即可
- 无需任何API配置
- 所有功能都可以体验

## 🎯 总结

现在你可以安全地上传到GitHub了：
- 代码中没有密钥
- .env文件不会被上传
- 项目在演示模式下完全可用
