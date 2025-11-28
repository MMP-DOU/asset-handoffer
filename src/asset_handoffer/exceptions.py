"""
异常体系

定义所有自定义异常，替代 sys.exit() 的使用。
这使得核心库可以被嵌入到其他应用中，由调用者决定如何处理错误。
"""


class HandofferError(Exception):
    """Asset Handoffer 基础异常类"""
    
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ValidationError(HandofferError):
    """文件名验证错误"""
    
    def __init__(self, message: str, filename: str | None = None, **kwargs):
        details = {"filename": filename, **kwargs}
        super().__init__(message, details)


class ConfigError(HandofferError):
    """配置错误"""
    
    def __init__(self, message: str, config_path: str | None = None, **kwargs):
        details = {"config_path": config_path, **kwargs}
        super().__init__(message, details)


class GitError(HandofferError):
    """Git 操作错误"""
    
    def __init__(self, message: str, command: str | None = None, **kwargs):
        details = {"command": command, **kwargs}
        super().__init__(message, details)


class ProcessError(HandofferError):
    """文件处理错误"""
    
    def __init__(self, message: str, filename: str | None = None, **kwargs):
        details = {"filename": filename, **kwargs}
        super().__init__(message, details)


class ParseError(HandofferError):
    """文件名解析错误"""
    
    def __init__(self, message: str, filename: str | None = None, **kwargs):
        details = {"filename": filename, **kwargs}
        super().__init__(message, details)


class FileOperationError(HandofferError):
    """文件操作错误"""
    
    def __init__(
        self,
        message: str,
        source: str | None = None,
        target: str | None = None,
        **kwargs
    ):
        details = {"source": source, "target": target, **kwargs}
        super().__init__(message, details)


class ConflictError(HandofferError):
    """文件冲突错误（内容不同的同名文件）"""
    
    def __init__(self, message: str, conflicts: list | None = None, **kwargs):
        details = {"conflicts": conflicts or [], **kwargs}
        super().__init__(message, details)


class PreflightCheckError(HandofferError):
    """预检查失败"""
    
    def __init__(self, message: str, failed_checks: list | None = None, **kwargs):
        details = {"failed_checks": failed_checks or [], **kwargs}
        super().__init__(message, details)


class InboxEmptyError(HandofferError):
    """收件箱为空"""
    pass


class ResourceNotFoundError(HandofferError):
    """资源未找到错误（模板、配置等）"""
    
    def __init__(self, message: str, resource_type: str | None = None, **kwargs):
        details = {"resource_type": resource_type, **kwargs}
        super().__init__(message, details)
