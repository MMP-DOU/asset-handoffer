"""Token加密存储"""

import os
import json
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import hashlib


class TokenStorage:
    """Token加密存储
    
    特性：
    - Token加密存储在本地
    - 基于机器特征生成加密密钥
    - 多项目支持
    """
    
    def __init__(self):
        # 存储目录
        self.storage_dir = Path.home() / ".asset-handoffer"
        self.storage_dir.mkdir(exist_ok=True, parents=True)
        
        # Token文件
        self.token_file = self.storage_dir / "tokens.enc"
        
        # 生成加密密钥
        self.key = self._get_encryption_key()
        self.cipher = Fernet(self.key)
    
    def _get_encryption_key(self) -> bytes:
        """生成机器唯一的加密密钥"""
        # 基于机器特征
        machine_id = f"{os.getenv('COMPUTERNAME', '')}{os.getenv('USERNAME', '')}"
        
        # 如果环境变量为空，使用默认值
        if not machine_id.strip():
            machine_id = "default_machine"
        
        # 生成密钥
        key_material = hashlib.sha256(machine_id.encode()).digest()
        return base64.urlsafe_b64encode(key_material)
    
    def save_token(self, project_name: str, token: str):
        """保存Token
        
        Args:
            project_name: 项目名称
            token: GitHub Personal Access Token
        """
        # 加载现有tokens
        tokens = self._load_tokens()
        
        # 更新
        tokens[project_name] = token
        
        # 加密并保存
        self._save_tokens(tokens)
    
    def get_token(self, project_name: str) -> str | None:
        """获取Token
        
        Args:
            project_name: 项目名称
            
        Returns:
            Token或None
        """
        tokens = self._load_tokens()
        return tokens.get(project_name)
    
    def remove_token(self, project_name: str):
        """删除Token
        
        Args:
            project_name: 项目名称
        """
        tokens = self._load_tokens()
        if project_name in tokens:
            del tokens[project_name]
            self._save_tokens(tokens)
    
    def list_projects(self) -> list[str]:
        """列出所有已保存Token的项目"""
        tokens = self._load_tokens()
        return list(tokens.keys())
    
    def _load_tokens(self) -> dict:
        """加载所有tokens"""
        if not self.token_file.exists():
            return {}
        
        try:
            # 读取加密数据
            encrypted = self.token_file.read_bytes()
            
            # 解密
            decrypted = self.cipher.decrypt(encrypted).decode('utf-8')
            
            # 解析JSON
            return json.loads(decrypted)
        
        except Exception:
            # 解密失败或文件损坏，返回空
            return {}
    
    def _save_tokens(self, tokens: dict):
        """保存所有tokens"""
        try:
            # 转JSON
            json_str = json.dumps(tokens)
            
            # 加密
            encrypted = self.cipher.encrypt(json_str.encode('utf-8'))
            
            # 保存
            self.token_file.write_bytes(encrypted)
        
        except Exception as e:
            raise RuntimeError(f"保存Token失败：{e}")
