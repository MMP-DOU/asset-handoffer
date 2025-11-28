"""
Pytest 配置和共享 fixtures

"""
import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """返回项目根目录"""
    return Path(__file__).parent.parent


@pytest.fixture
def sample_config():
    """返回示例配置"""
    return {
        "project": {
            "name": "TestProject",
            "asset_root": "Assets/GameRes/"
        },
        "workspace": {
            "base": "./"
        },
        "git": {
            "repository": "https://github.com/test/test.git",
            "branch": "main",
            "commit_template": "Update {category}: {feature}"
        },
        "path_template": "{module}/{category}/{feature}/",
        "naming": {
            "pattern": r"^(?P<module>\\w+)_(?P<category>\\w+)_(?P<feature>[\\w-]+)(_(?P<variant>\\w+))?\\.(?P<ext>\\w+)$",
            "example": "GameRes_Character_Hero_Idle.fbx"
        },
        "language": "zh-CN"
    }


@pytest.fixture
def sample_files():
    """返回示例文件名列表"""
    return [
        "GameRes_Character_Witch_Idle.anim",
        "GameRes_Character_Witch_Walk.anim",
        "GameRes_UiEffect_LevelUp.png",
    ]
