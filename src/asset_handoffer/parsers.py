"""文件名解析器"""

import re
from dataclasses import dataclass
from typing import Pattern

from .exceptions import ParseError


@dataclass
class ParsedFilename:
    """解析后的文件名信息"""
    module: str
    category: str
    feature: str
    variant: str | None
    extension: str
    original_name: str


class FilenameParser:
    """文件名解析器
    
    使用正则表达式解析文件名，提取结构化信息
    """
    
    def __init__(self, pattern: str):
        """
        Args:
            pattern: 正则表达式，必须包含命名组：module, category, feature
                    可选命名组：variant, ext
        """
        try:
            self.pattern: Pattern = re.compile(pattern)
        except re.error as e:
            raise ParseError(f"无效的正则表达式：{e}")
        
        # 验证必需的命名组
        required_groups = {'module', 'category', 'feature'}
        pattern_groups = set(self.pattern.groupindex.keys())
        
        if not required_groups.issubset(pattern_groups):
            missing = required_groups - pattern_groups
            raise ParseError(f"正则表达式缺少必需的命名组：{missing}")
    
    def parse(self, filename: str) -> ParsedFilename:
        """解析文件名
        
        Args:
            filename: 文件名
            
        Returns:
            ParsedFilename对象
            
        Raises:
            ParseError: 文件名格式错误
        """
        match = self.pattern.match(filename)
        
        if not match:
            raise ParseError(f"文件名不匹配格式：{filename}")
        
        # 提取组件
        groups = match.groupdict()
        
        module = groups.get('module')
        category = groups.get('category')
        feature = groups.get('feature')
        variant = groups.get('variant')  # 可选
        extension = groups.get('ext', groups.get('extension', ''))
        
        if not module or not category or not feature:
            raise ParseError(f"文件名缺少必需组件：{filename}")
        
        return ParsedFilename(
            module=module,
            category=category,
            feature=feature,
            variant=variant,
            extension=extension,
            original_name=filename
        )
