# Soulnote 部署指南 - 生产环境

## 概述

Soulnote 现在已经更新为使用在线AI服务，无需用户安装LM Studio。支持以下AI提供商：

- **OpenAI GPT** (推荐用于生产环境)
- **Anthropic Claude** (高质量输出)
- **Mock Provider** (测试模式)

## 🚀 快速部署

### 1. 环境配置

创建 `.env` 文件：

```bash
# 复制示例配置
cp .env.example .env

# 编辑配置文件
nano .env
```

### 2. 选择AI提供商

#### Option A: OpenAI (推荐)
```env
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
```

**获取API密钥：**
1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 注册/登录账户
3. 创建新的API密钥
4. 复制密钥到 `.env` 文件

**成本估算：**
- gpt-3.5-turbo: ~$0.001-0.002 per request
- gpt-4: ~$0.01-0.03 per request

#### Option B: Anthropic Claude
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**获取API密钥：**
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册/登录账户
3. 创建新的API密钥

#### Option C: 测试模式
```env
AI_PROVIDER=mock
```
无需API密钥，返回模拟响应

### 3. 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python backend/app.py
```

### 4. 生产部署

#### Docker 部署 (推荐)

创建 `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5002

CMD ["python", "backend/app.py"]
```

创建 `docker-compose.yml`:
```yaml
version: '3.8'
services:
  soulnote:
    build: .
    ports:
      - "5002:5002"
    environment:
      - AI_PROVIDER=openai
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./output:/app/output
      - ./uploads:/app/uploads
```

部署命令：
```bash
docker-compose up -d
```

#### 传统服务器部署

使用 Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5002 backend.app:app
```

使用 systemd service:
```ini
[Unit]
Description=Soulnote App
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/soulnote
Environment=PATH=/path/to/soulnote/venv/bin
ExecStart=/path/to/soulnote/venv/bin/gunicorn -w 4 -b 127.0.0.1:5002 backend.app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # 支持大文件上传
        client_max_body_size 16M;
    }

    # 静态文件
    location /static/ {
        alias /path/to/soulnote/static/;
    }

    # 输出文件
    location /api/output/ {
        alias /path/to/soulnote/output/;
    }
}
```

## 🌐 云平台部署

### Heroku
```bash
# 创建 Procfile
echo "web: gunicorn -w 4 -b 0.0.0.0:\$PORT backend.app:app" > Procfile

# 部署
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your-key-here
git push heroku main
```

### Railway
```bash
# 安装 Railway CLI
npm install -g @railway/cli

# 部署
railway login
railway init
railway add
railway deploy
```

### Vercel (Serverless)
```json
{
  "functions": {
    "backend/app.py": {
      "runtime": "python3.9"
    }
  },
  "env": {
    "OPENAI_API_KEY": "@openai_api_key"
  }
}
```

## 📊 监控和维护

### 健康检查
```bash
curl http://your-domain.com/api/health
```

响应示例：
```json
{
  "status": "healthy",
  "ai_provider": "OpenAI (gpt-3.5-turbo)",
  "ai_connected": true
}
```

### 日志监控
```bash
# 查看应用日志
tail -f /var/log/soulnote/app.log

# Docker日志
docker logs -f soulnote_container
```

### 性能优化
- 使用Redis缓存频繁请求
- 实现请求限制防止滥用
- 优化音频文件处理
- 使用CDN分发静态资源

## 🔒 安全考虑

### API密钥安全
- 使用环境变量存储密钥
- 定期轮换API密钥
- 限制API密钥权限

### 输入验证
- 限制文件大小和类型
- 验证音频文件格式
- 防止XSS和注入攻击

### 访问控制
```python
# 实现请求限制
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.remote_addr,
    default_limits=["100 per hour"]
)

@app.route('/api/analyze/text', methods=['POST'])
@limiter.limit("10 per minute")
def analyze_text():
    # ...
```

## 🎯 生产环境清单

- [ ] 配置AI提供商API密钥
- [ ] 设置域名和SSL证书
- [ ] 配置反向代理 (Nginx/Apache)
- [ ] 实现日志记录和监控
- [ ] 设置自动备份
- [ ] 配置错误报告
- [ ] 实现健康检查
- [ ] 优化性能和缓存
- [ ] 设置请求限制
- [ ] 测试所有功能

## 📞 支持

如需帮助：
1. 检查日志文件
2. 验证API密钥配置
3. 测试网络连接
4. 查看错误信息

---

🎉 现在你的Soulnote应用已经准备好为用户提供服务，无需他们安装任何本地软件！
