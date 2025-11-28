"""配置管理"""

from pathlib import Path
import yaml
from typing import Any

from ..exceptions import ConfigError


class Config:
    """配置管理
    
    特性：
    - 无签名验证（简化）
    - 自动解析路径
    - 基础完整性检查
    """
    
    def __init__(self, config_dict: dict, config_file: Path):
        self.data = config_dict
        self.config_file = config_file
        self._resolve_paths()
        self._validate_basic()
    
    def _resolve_paths(self):
        """解析和创建工作区路径"""
        workspace = self.data.get('workspace', {})
        base = workspace.get('base', './')
        
        # 相对路径 → 绝对路径（相对配置文件）
        if not Path(base).is_absolute():
            base = (self.config_file.parent / base).resolve()
        else:
            base = Path(base)
        
        # 解析各个路径
        self.workspace_base = base
        self.inbox = base / "inbox"
        self.repo = base / ".repo"  # 隐藏的Git仓库
        self.failed = base / "failed"  # 失败文件
        self.logs = base / "logs"  # 日志
    
    def _validate_basic(self):
        """基础验证（必需字段）"""
        required_fields = {
            'project.name': '项目名称',
            'git.repository': 'Git仓库地址',
            'path_template': '路径模板',
            'naming.pattern': '命名规则'
        }
        
        for field, desc in required_fields.items():
            if not self._get_nested(field):
                raise ConfigError(f"配置缺少必需字段：{desc} ({field})")
        
        # 验证Git URL格式
        git_url = self.git_url
        if not (git_url.startswith('https://github.com') or 
                git_url.startswith('https://gitee.com')):
            raise ConfigError(f"不支持的Git仓库地址：{git_url}")
    
    def _get_nested(self, key_path: str) -> Any:
        """获取嵌套字段值"""
        keys = key_path.split('.')
        value = self.data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
        
        return value
    
    @property
    def project_name(self) -> str:
        return self.data['project']['name']
    
    @property
    def git_url(self) -> str:
        return self.data['git']['repository']
    
    @property
    def git_branch(self) -> str:
        return self.data.get('git', {}).get('branch', 'main')
    
    @property
    def git_commit_template(self) -> str:
        return self.data.get('git', {}).get('commit_template', 
                                           'Update {category}: {feature}')
    
    @property
    def path_template(self) -> str:
        return self.data['path_template']
    
    @property
    def asset_root(self) -> str:
        return self.data['project'].get('asset_root', 'Assets/GameRes/')
    
    @property
    def naming_pattern(self) -> str:
        return self.data['naming']['pattern']
    
    @property
    def naming_example(self) -> str:
        return self.data['naming'].get('example', '')
    
    @property
    def language(self) -> str:
        return self.data.get('language', 'zh-CN')
    
    def ensure_dirs(self):
        """确保所有必需目录存在"""
        dirs = [self.inbox, self.failed, self.logs]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def load(config_file: Path) -> 'Config':
        """加载配置文件"""
        if not config_file.exists():
            raise ConfigError(f"配置文件不存在：{config_file}")
        
        try:
            data = yaml.safe_load(config_file.read_text(encoding='utf-8'))
        except yaml.YAMLError as e:
            raise ConfigError(f"配置文件格式错误：{e}")
        
        return Config(data, config_file)
    
    @staticmethod
    def create(
        project_name: str,
        git_url: str,
        asset_root: str = "Assets/GameRes/",
        output_file: Path = None
    ) -> Path:
        """创建新配置文件（程序员使用）"""
        
        # 读取模板文件
        template_path = Path(__file__).parent.parent / "templates" / "config.yaml"
        
        if not template_path.exists():
            raise ConfigError(f"配置模板不存在: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # 替换占位符（保留注释和格式）
        content = template_content.replace(
            'name: "示例游戏项目"',
            f'name: "{project_name}"'
        ).replace(
            'asset_root: "Assets/GameRes/"',
            f'asset_root: "{asset_root}"'
        ).replace(
            'repository: "https://github.com/your-org/your-project.git"',
            f'repository: "{git_url}"'
        )
        
        # 输出文件
        if output_file is None:
            safe_name = project_name.lower().replace(' ', '-').replace('_', '-')
            output_file = Path(f"{safe_name}.yaml")
        
        # 保存（直接写入，保留注释）
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_file
