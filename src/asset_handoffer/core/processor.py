"""文件处理器（核心业务逻辑）"""

import shutil
from pathlib import Path
from .config import Config
from .git_repo import GitRepo, GitError
from .path_generator import PathGenerator
from ..parsers import FilenameParser, ParseError
from ..exceptions import ProcessError


class FileProcessor:
    """文件处理器
    
    核心流程：
    1. 从inbox读取文件
    2. 解析文件名
    3. 移动到.repo对应位置
    4. git add + commit + push
    5. 成功 or 失败（留在inbox/移到failed）
    """
    
    def __init__(self, config: Config):
        self.config = config
        self.parser = FilenameParser(config.naming_pattern)
        self.path_gen = PathGenerator(config.path_template, config.asset_root)
        self.repo = GitRepo(config.repo)
    
    def process(self, file_path: Path) -> bool:
        """处理单个文件
        
        Args:
            file_path: 文件路径（通常在inbox中）
            
        Returns:
            True=成功，False=失败
        """
        try:
            # 1. 验证仓库
            if not self.repo.exists():
                raise ProcessError(
                    "本地仓库不存在，请先运行 setup 命令初始化工作区"
                )
            
            # 2. 解析文件名
            try:
                parsed = self.parser.parse(file_path.name)
            except ParseError as e:
                raise ProcessError(f"文件名格式错误：{e}\n正确格式：{self.config.naming_example}")
            
            # 3. 生成目标路径
            target_path = self.path_gen.generate(parsed, self.config.repo)
            
            # 确保目标目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 4. 移动文件到仓库
            shutil.move(str(file_path), str(target_path))
            
            # 5. Git操作
            try:
                # Pull最新代码（避免冲突）
                self.repo.pull()
                
                # Add
                self.repo.add(target_path)
                
                # Commit
                commit_msg = self.config.git_commit_template.format(
                    module=parsed.module,
                    category=parsed.category,
                    feature=parsed.feature
                )
                self.repo.commit(commit_msg)
                
                # Push
                self.repo.push()
                
            except GitError as e:
                # Git操作失败，文件已经移动了，需要移回
                self._handle_git_failure(target_path, file_path, e)
                return False
            
            # 6. 成功
            print(f"成功：{file_path.name}")
            print(f"   目标：{target_path.relative_to(self.config.repo)}")
            return True
            
        except ProcessError as e:
            # 处理错误
            print(f"错误：处理失败：{e}")
            self._move_to_failed(file_path)
            return False
        
        except Exception as e:
            # 未知错误
            print(f"错误：未知错误：{e}")
            self._move_to_failed(file_path)
            return False
    
    def _handle_git_failure(self, target_path: Path, original_path: Path, error: GitError):
        """处理Git操作失败
        
        文件已经移动到仓库了，但Git操作失败
        需要移回原位置或failed目录
        """
        try:
            # 尝试移回inbox
            if original_path.parent.exists():
                shutil.move(str(target_path), str(original_path))
                print(f"警告：Git操作失败，文件已移回inbox：{error}")
            else:
                # inbox不存在了，移到failed
                self._move_to_failed(target_path)
                print(f"错误：Git操作失败：{error}")
        except Exception as e:
            print(f"错误：严重错误：无法恢复文件 - {e}")
    
    def _move_to_failed(self, file_path: Path):
        """移动文件到失败目录"""
        try:
            self.config.failed.mkdir(parents=True, exist_ok=True)
            failed_path = self.config.failed / file_path.name
            
            # 如果已存在，添加时间戳
            if failed_path.exists():
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                stem = file_path.stem
                suffix = file_path.suffix
                failed_path = self.config.failed / f"{stem}_{timestamp}{suffix}"
            
            shutil.move(str(file_path), str(failed_path))
            print(f"📁 文件已移至失败目录：{failed_path}")
            
        except Exception as e:
            print(f"警告：无法移动到失败目录：{e}")
    
    def process_batch(self, files: list[Path]) -> tuple[int, int]:
        """批量处理文件
        
        Args:
            files: 文件列表
            
        Returns:
            (成功数, 失败数)
        """
        success = 0
        failed = 0
        
        for i, file_path in enumerate(files, 1):
            print(f"\n[{i}/{len(files)}] 处理：{file_path.name}")
            
            if self.process(file_path):
                success += 1
            else:
                failed += 1
        
        return success, failed
