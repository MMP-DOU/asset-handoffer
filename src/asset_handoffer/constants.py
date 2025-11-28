"""常量定义"""

# 文件哈希
HASH_CHUNK_SIZE = 8192  # 8KB chunks for file hashing

# Git配置默认值
DEFAULT_GIT_BRANCH = "main"
DEFAULT_GIT_REMOTE = "origin"
DEFAULT_GIT_AUTO_PUSH = True
DEFAULT_COMMIT_TEMPLATE = (
    "feat(assets): Add {category}\n\n"
    "Feature: {feature}\n"
    "Files: {file_count}\n\n"
    "{file_list}"
)

# 国际化默认值
DEFAULT_LANGUAGE = "zh-CN"

# 路径配置
DEFAULT_HOME_DIR = ".asset-handoffer"
DEFAULT_CONFIG_NAME = "config.yaml"
DEFAULT_INBOX_NAME = "inbox"
