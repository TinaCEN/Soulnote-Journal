#!/usr/bin/env python3
"""
在线API密钥分发服务
"""

from flask import Flask, jsonify, request
import hashlib
import time
import json
import os

app = Flask(__name__)

# 配置
EXPERIENCE_KEYS = [
    "sk-your-shared-key-1",  # 替换为实际密钥
    "sk-your-shared-key-2",  # 替换为实际密钥
]

MAX_REQUESTS_PER_USER = 50
KEY_EXPIRE_SECONDS = 3600  # 1小时

def get_user_id():
    """生成用户标识"""
    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent', '')
    return hashlib.md5(f"{ip}{user_agent}".encode()).hexdigest()[:16]

@app.route('/api/get-key', methods=['POST'])
def get_api_key():
    """分发体验API密钥"""
    user_id = get_user_id()
    
    # 检查用户是否还有配额
    usage_data = load_usage()
    current_time = time.time()
    
    if user_id in usage_data:
        user_data = usage_data[user_id]
        if current_time - user_data['first_request'] < KEY_EXPIRE_SECONDS:
            if user_data['count'] >= MAX_REQUESTS_PER_USER:
                return jsonify({
                    'success': False,
                    'message': '体验次数已用完，请申请个人API密钥'
                }), 429
        else:
            # 重置过期用户的计数
            usage_data[user_id] = {
                'count': 0,
                'first_request': current_time
            }
    else:
        usage_data[user_id] = {
            'count': 0,
            'first_request': current_time
        }
    
    # 选择可用的密钥
    selected_key = select_available_key()
    if not selected_key:
        return jsonify({
            'success': False,
            'message': '暂时没有可用的体验密钥，请稍后再试'
        }), 503
    
    # 更新使用计数
    usage_data[user_id]['count'] += 1
    save_usage(usage_data)
    
    return jsonify({
        'success': True,
        'api_key': selected_key,
        'remaining_requests': MAX_REQUESTS_PER_USER - usage_data[user_id]['count'],
        'expire_time': usage_data[user_id]['first_request'] + KEY_EXPIRE_SECONDS
    })

def select_available_key():
    """选择可用的API密钥"""
    # 简单轮询策略
    import random
    return random.choice(EXPERIENCE_KEYS)

def load_usage():
    """加载使用统计"""
    if os.path.exists('usage.json'):
        with open('usage.json', 'r') as f:
            return json.load(f)
    return {}

def save_usage(data):
    """保存使用统计"""
    with open('usage.json', 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5008)
