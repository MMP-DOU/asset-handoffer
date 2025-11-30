"""Git仓库管理（本地仓库操作）"""

import subprocess
from pathlib import Path
from typing import Optional

from ..exceptions import GitError


class GitRepo:
    """Git仓库管理
    
    特性：
    - 操作本地Git仓库（.repo目录）
    - 简单的Git命令封装
    - 美术无感知
    """
    
    def __init__(self, repo_path: Path):
        """
        Args:
            repo_path: 本地仓库路径（通常是 workspace/.repo）
        """
        self.repo_path = repo_path
    
    def exists(self) -> bool:
        """检查仓库是否已存在"""
        return (self.repo_path / ".git").exists()
    
    def clone(self, git_url: str, branch: str = "main"):
        """Clone仓库
        
        Args:
            git_url: GitHub仓库URL
            branch: 分支名
        """
        if self.exists():
            raise GitError(f"仓库已存在：{self.repo_path}")
        
        try:
            # Clone
            subprocess.run(
                ['git', 'clone', '-b', branch, '--single-branch', git_url, str(self.repo_path)],
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            raise GitError(f"Clone失败：{e.stderr}")
    
    def pull(self):
        """拉取最新代码"""
        try:
            self._run_git(['pull'])
        except subprocess.CalledProcessError as e:
            raise GitError(f"Pull失败：{e.stderr}")
    
    def add(self, file_path: Path):
        """添加文件到暂存区
        
        Args:
            file_path: 文件绝对路径（在仓库中）
        """
        try:
            rel_path = file_path.relative_to(self.repo_path)
            self._run_git(['add', str(rel_path)])
        except ValueError as e:
            raise GitError(f"文件不在仓库中：{file_path}")
        except subprocess.CalledProcessError as e:
            raise GitError(f"Add失败：{e.stderr}")
    
    def commit(self, message: str):
        """提交变更
        
        Args:
            message: 提交消息
        """
        try:
            self._run_git(['commit', '-m', message])
        except subprocess.CalledProcessError as e:
            # 如果没有变更，不算错误
            if "nothing to commit" in e.stderr:
                return
            raise GitError(f"Commit失败：{e.stderr}")
    
    def push(self, branch: Optional[str] = None):
        """推送到远程
        
        Args:
            branch: 分支名（None=当前分支）
        """
        try:
            if branch:
                self._run_git(['push', 'origin', branch])
            else:
                self._run_git(['push'])
        except subprocess.CalledProcessError as e:
            raise GitError(f"Push失败：{e.stderr}")
    
    def remove(self, file_path: Path):
        """删除文件（git rm）
        
        Args:
            file_path: 文件绝对路径（在仓库中）
        """
        try:
            rel_path = file_path.relative_to(self.repo_path)
            self._run_git(['rm', str(rel_path)])
        except ValueError:
            raise GitError(f"文件不在仓库中：{file_path}")
        except subprocess.CalledProcessError as e:
            raise GitError(f"Remove失败：{e.stderr}")
    
    def status(self) -> str:
        """获取仓库状态"""
        try:
            result = self._run_git(['status', '--short'])
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise GitError(f"Status失败：{e.stderr}")
    
    def _run_git(self, args: list) -> subprocess.CompletedProcess:
        """执行git命令
        
        Args:
            args: Git命令参数
            
        Returns:
            命令执行结果
        """
        return subprocess.run(
            ['git'] + args,
            cwd=str(self.repo_path),
            check=True,
            capture_output=True,
            text=True
        )
