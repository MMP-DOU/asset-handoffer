from importlib import resources
from pathlib import Path
import os
import yaml


class Messages:
    def __init__(
        self,
        language: str,
        messages_path: Path | None = None,
        home: Path | None = None,
    ):
        self.language = language
        self.messages: dict[str, str] = {}
        if messages_path:
            p = Path(messages_path)
            if p.is_dir():
                f = p / f"{language}.yaml"
            else:
                f = p
            if f.exists():
                with open(f, "r", encoding="utf-8") as fh:
                    self.messages = yaml.safe_load(fh) or {}
                return
        try:
            base = resources.files("asset_handoffer").joinpath("locales")
            candidate = base / f"{language}.yaml"
            with resources.as_file(candidate) as src:
                with open(src, "r", encoding="utf-8") as fh:
                    self.messages = yaml.safe_load(fh) or {}
        except Exception:
            pass

    def t(self, key: str, default: str | None = None, **kwargs) -> str:
        """翻译

        Args:
            key: 消息键
            default: 默认值（当键不存在时使用）
            **kwargs: 格式化参数

        Returns:
            翻译后的字符串
        """
        s = self.messages.get(key, default or key)
        try:
            return s.format(**kwargs)
        except Exception:
            return s

    @classmethod
    def from_config(cls, config: dict, explicit_lang: str | None = None) -> "Messages":
        """
        从配置对象创建 Messages 实例
        
        Args:
            config: 配置字典
            explicit_lang: 显式指定的语言（覆盖配置中的语言）
            
        Returns:
            Messages 实例
            
        Example:
            >>> config = {"localization": {"language": "zh-CN"}}
            >>> m = Messages.from_config(config)
            >>> m.t("some.key")
        """
        lang = explicit_lang or config.get("localization", {}).get("language", "zh-CN")
        return cls(lang)


def resolve_lang(lang: str | None, home: Path | None) -> str:
    if lang:
        return lang
    env_lang = os.environ.get("ASSET_HANDOFFER_LANG")
    if env_lang:
        return env_lang
    env_home = os.environ.get("ASSET_HANDOFFER_HOME")
    base_home = home or (Path(env_home) if env_home else Path(".asset-handoffer"))
    cfg = base_home / "config.yaml"
    if cfg.exists():
        try:
            with open(cfg, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            loc = data.get("localization") or {}
            v = loc.get("language")
            if isinstance(v, str) and v:
                return v
        except Exception:
            pass
    return "zh-CN"


def get_messages(language: str = "zh-CN") -> Messages:
    """获取 Messages 实例

    Args:
        language: 语言代码，如 "zh-CN" 或 "en-US"

    Returns:
        Messages 实例

    Example:
        >>> m = get_messages("zh-CN")
        >>> m.t("some.key")
    """
    return Messages(language)


def get_messages_from_config(config: dict) -> Messages:
    """
    从配置字典中获取 Messages 实例
    
    Args:
        config: 配置字典
        
    Returns:
        Messages 实例
        
    Example:
        >>> config = {"localization": {"language": "en-US"}}
        >>> m = get_messages_from_config(config)
        >>> m.t("some.key")
    """
    lang = config.get("localization", {}).get("language", "zh-CN")
    return Messages(lang)
