"""用户认证服务 - 用户注册、登录、会话管理"""

import json
import os
import hashlib
import secrets
from typing import Optional, Dict
from datetime import datetime, timedelta
import threading


class AuthService:
    """用户认证服务"""
    
    def __init__(self, storage_dir: str = "auth_data"):
        """初始化认证服务
        
        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = storage_dir
        self.lock = threading.Lock()
        
        # 确保存储目录存在
        os.makedirs(storage_dir, exist_ok=True)
        
        # 用户数据文件
        self.users_file = os.path.join(storage_dir, "users.json")
        self.sessions_file = os.path.join(storage_dir, "sessions.json")
        
        # 初始化文件
        self._init_files()
    
    def _init_files(self):
        """初始化数据文件"""
        with self.lock:
            if not os.path.exists(self.users_file):
                with open(self.users_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
            
            if not os.path.exists(self.sessions_file):
                with open(self.sessions_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f, ensure_ascii=False, indent=2)
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def register(self, username: str, password: str, email: Optional[str] = None) -> tuple[bool, Optional[str]]:
        """注册用户
        
        Args:
            username: 用户名
            password: 密码
            email: 邮箱（可选）
            
        Returns:
            (是否成功, 错误信息)
        """
        if not username or not password:
            return False, "用户名和密码不能为空"
        
        if len(username) < 3:
            return False, "用户名至少需要3个字符"
        
        if len(password) < 6:
            return False, "密码至少需要6个字符"
        
        with self.lock:
            # 读取用户数据
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            # 检查用户名是否已存在
            if username in users:
                return False, "用户名已存在"
            
            # 创建新用户
            users[username] = {
                "username": username,
                "password_hash": self._hash_password(password),
                "email": email,
                "created_at": datetime.now().isoformat(),
                "last_login": None
            }
            
            # 保存用户数据
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            return True, None
    
    def login(self, username: str, password: str) -> tuple[bool, Optional[str], Optional[str]]:
        """用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            (是否成功, 错误信息, session_token)
        """
        if not username or not password:
            return False, "用户名和密码不能为空", None
        
        with self.lock:
            # 读取用户数据
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            # 检查用户是否存在
            if username not in users:
                return False, "用户名或密码错误", None
            
            user = users[username]
            
            # 验证密码
            password_hash = self._hash_password(password)
            if user["password_hash"] != password_hash:
                return False, "用户名或密码错误", None
            
            # 更新最后登录时间
            user["last_login"] = datetime.now().isoformat()
            with open(self.users_file, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            
            # 创建会话
            session_token = secrets.token_urlsafe(32)
            
            # 读取会话数据
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
            
            # 保存会话（30天有效期）
            sessions[session_token] = {
                "username": username,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
            }
            
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(sessions, f, ensure_ascii=False, indent=2)
            
            return True, None, session_token
    
    def validate_session(self, session_token: str) -> tuple[bool, Optional[str]]:
        """验证会话令牌
        
        Args:
            session_token: 会话令牌
            
        Returns:
            (是否有效, 用户名)
        """
        if not session_token:
            return False, None
        
        with self.lock:
            # 读取会话数据
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
            
            if session_token not in sessions:
                return False, None
            
            session = sessions[session_token]
            
            # 检查是否过期
            expires_at = datetime.fromisoformat(session["expires_at"])
            if datetime.now() > expires_at:
                # 删除过期会话
                del sessions[session_token]
                with open(self.sessions_file, 'w', encoding='utf-8') as f:
                    json.dump(sessions, f, ensure_ascii=False, indent=2)
                return False, None
            
            return True, session["username"]
    
    def logout(self, session_token: str) -> bool:
        """登出用户
        
        Args:
            session_token: 会话令牌
            
        Returns:
            是否成功
        """
        if not session_token:
            return False
        
        with self.lock:
            # 读取会话数据
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                sessions = json.load(f)
            
            if session_token in sessions:
                del sessions[session_token]
                with open(self.sessions_file, 'w', encoding='utf-8') as f:
                    json.dump(sessions, f, ensure_ascii=False, indent=2)
                return True
            
            return False
    
    def get_user_info(self, username: str) -> Optional[Dict]:
        """获取用户信息
        
        Args:
            username: 用户名
            
        Returns:
            用户信息字典，如果不存在返回None
        """
        with self.lock:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                users = json.load(f)
            
            if username in users:
                user = users[username].copy()
                # 移除敏感信息
                user.pop("password_hash", None)
                return user
            
            return None


# 全局认证服务实例
_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """获取认证服务实例（单例模式）"""
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
