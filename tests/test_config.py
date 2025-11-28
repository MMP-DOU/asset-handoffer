"""
配置管理测试
"""
import pytest
from pathlib import Path
from asset_handoffer.core.config import Config

def test_create_and_load_config(tmp_path):
    """测试配置创建和加载"""
    config_file = tmp_path / "test_config.yaml"
    
    # 创建配置
    Config.create(
        project_name="TestProject",
        git_url="https://github.com/test/test.git",
        output_file=config_file
    )
    
    assert config_file.exists()
    
    # 加载配置
    config = Config.load(config_file)
    assert config.project_name == "TestProject"
    assert config.git_url == "https://github.com/test/test.git"
    assert config.workspace_base.resolve() == tmp_path.resolve()
