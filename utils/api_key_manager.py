#!/usr/bin/env python3
"""
API密钥管理器 - 为体验用户分配临时密钥
"""

import os
import json
import hashlib
from datetime import datetime, timedelta

class APIKeyManager:
    def __init__(self):
        self.keys_file = 'api_keys.json'
        self.usage_file = 'api_usage.json'
        
        # 体验版密钥池（你可以创建多个小额度密钥）
        self.experience_keys = [
            "sk-experience-001",  # 替换为真实密钥
            "sk-experience-002",  # 替换为真实密钥
            "sk-experience-003",  # 替换为真实密钥
        ]
        
        self.max_usage_per_key = 100  # 每个密钥最大使用次数
        self.key_expire_hours = 24    # 密钥过期时间（小时）
    
    def get_experience_key(self, user_id):
        """为用户分配体验密钥"""
        usage = self.load_usage()
        
        # 检查用户是否已有分配的密钥
        if user_id in usage:
            user_data = usage[user_id]
            assigned_time = datetime.fromisoformat(user_data['assigned_time'])
            
            # 检查是否过期
            if datetime.now() - assigned_time < timedelta(hours=self.key_expire_hours):
                if user_data['usage_count'] < self.max_usage_per_key:
                    return user_data['api_key']
        
        # 为新用户或过期用户分配新密钥
        available_key = self.find_available_key()
        if available_key:
            usage[user_id] = {
                'api_key': available_key,
                'assigned_time': datetime.now().isoformat(),
                'usage_count': 0
            }
            self.save_usage(usage)
            return available_key
        
        return None
    
    def find_available_key(self):
        """找到可用的体验密钥"""
        usage = self.load_usage()
        key_usage = {}
        
        # 统计每个密钥的使用情况
        for user_data in usage.values():
            key = user_data['api_key']
            if key not in key_usage:
                key_usage[key] = 0
            key_usage[key] += user_data['usage_count']
        
        # 找到使用量最少的密钥
        for key in self.experience_keys:
            if key_usage.get(key, 0) < self.max_usage_per_key * 10:  # 允许多用户共享
                return key
        
        return None
    
    def record_usage(self, user_id):
        """记录API使用"""
        usage = self.load_usage()
        if user_id in usage:
            usage[user_id]['usage_count'] += 1
            self.save_usage(usage)
    
    def load_usage(self):
        """加载使用记录"""
        if os.path.exists(self.usage_file):
            with open(self.usage_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_usage(self, usage):
        """保存使用记录"""
        with open(self.usage_file, 'w') as f:
            json.dump(usage, f, indent=2)
    
    @staticmethod
    def generate_user_id(request):
        """根据用户信息生成ID"""
        user_agent = request.headers.get('User-Agent', '')
        ip = request.remote_addr
        return hashlib.md5(f"{ip}{user_agent}".encode()).hexdigest()[:16]

# 在主应用中集成
def get_api_key_for_request(request):
    """为请求获取API密钥"""
    manager = APIKeyManager()
    user_id = manager.generate_user_id(request)
    return manager.get_experience_key(user_id)
