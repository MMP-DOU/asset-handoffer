"""路径生成器"""

from pathlib import Path
from ..parsers import ParsedFilename


class PathGenerator:
    """路径生成器
    
    根据解析的文件名信息生成目标路径
    """
    
    def __init__(self, path_template: str, asset_root: str):
        """
        Args:
            path_template: 路径模板，如 "{module}/{category}/{feature}/"
            asset_root: Unity资产根路径，如 "Assets/GameRes/"
        """
        self.path_template = path_template
        self.asset_root = asset_root
    
    def generate(self, parsed: ParsedFilename, repo_base: Path) -> Path:
        """生成完整的目标路径
        
        Args:
            parsed: 解析后的文件名信息
            repo_base: 仓库根目录
            
        Returns:
            完整的目标文件路径
        """
        # 生成相对路径
        rel_dir = self.path_template.format(
            module=parsed.module,
            category=parsed.category,
            feature=parsed.feature
        )
        
        # 组合完整路径
        full_dir = repo_base / self.asset_root / rel_dir
        full_path = full_dir / parsed.original_name
        
        return full_path
    
    def sanitize_path_component(self, component: str) -> str:
        """清理路径组件中的不安全字符
        
        Args:
            component: 路径组件（如模块名、类别名）
            
        Returns:
            清理后的安全路径组件
        """
        # 替换不安全字符
        unsafe_chars = '<>:"|?*\\/'
        for char in unsafe_chars:
            component = component.replace(char, '_')
        
        # 限制长度
        if len(component) > 100:
            component = component[:100]
        
        return component
