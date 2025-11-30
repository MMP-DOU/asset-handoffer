"""CLI命令行界面"""

import typer
from pathlib import Path
from getpass import getpass

from .core.config import Config, ConfigError
from .core.git_repo import GitRepo, GitError
from .core.processor import FileProcessor

from .i18n import get_messages

app = typer.Typer(
    help="Asset Handoffer - 资产交接自动化工具",
    no_args_is_help=True
)


@app.command()
def init(
    project_name: str = typer.Option(..., prompt="项目名称"),
    git_url: str = typer.Option(..., prompt="GitHub仓库URL"),
    asset_root: str = typer.Option("Assets/GameRes/", prompt="Unity资产根路径"),
    output: Path = typer.Option(None, "--output", "-o", help="输出文件路径")
):
    """创建配置文件（程序员使用）
    
    生成一个配置文件，包含项目的所有必要信息。
    将此配置文件发给美术人员使用。
    """
    try:
        config_file = Config.create(
            project_name=project_name,
            git_url=git_url,
            asset_root=asset_root,
            output_file=output
        )
        
        print(f"已生成配置文件：{config_file}")
        print("\n下一步：")
        print("1. 确保已配置 Git 凭据（SSH 或 Credential Manager）")
        print("2. 将配置文件发给美术人员")
        print(f"\n3. 美术人员运行：asset-handoffer setup {config_file}")
        
    except Exception as e:
        print(f"错误：生成配置失败：{e}")
        raise typer.Exit(1)


@app.command()
def setup(config_file: Path):
    """设置工作区（美术使用）
    
    首次使用时运行此命令，将：
    1. 创建工作区目录（inbox等）
    2. 克隆Git仓库到本地
    2. 克隆Git仓库到本地
    """
    try:
        # 加载配置
        config = Config.load(config_file)
        m = get_messages(config.language)
        
        print("=" * 60)
        print(f"  {m.t('setup.title', default='Asset Handoffer - 工作区设置')}")
        print("=" * 60)
        print(f"\n项目：{config.project_name}")
        print(f"仓库：{config.git_url}")
        print(f"工作区：{config.workspace_base}\n")
        
        # 创建目录
        config.ensure_dirs()
        print(f"收件箱：{config.inbox}")
        
        # 检查仓库是否已存在
        repo = GitRepo(config.repo)
        
        if repo.exists():
            print(f"警告：本地仓库已存在：{config.repo}")
            if not typer.confirm("是否重新克隆？"):
                print("跳过克隆")
            else:
                import shutil
                shutil.rmtree(config.repo)
                repo_exists = False
        else:
            repo_exists = False
        
        if not repo_exists or not repo.exists():
            # Clone仓库
            print("\n正在克隆仓库...")
            try:
                repo.clone(config.git_url, config.git_branch)
                print(f"仓库已克隆到：{config.repo}")
            except GitError as e:
                print(f"错误：克隆失败：{e}")
                raise typer.Exit(1)
        
        print("\n" + "=" * 60)
        print("  设置完成")
        print("=" * 60)
        print("\n使用方法：")
        print(f"  1. 将文件放入：{config.inbox}")
        print(f"  2. 运行：asset-handoffer process {config_file}")
        print()
        
    except ConfigError as e:
        print(f"错误：配置错误：{e}")
        raise typer.Exit(1)
    except Exception as e:
        print(f"错误：设置失败：{e}")
        raise typer.Exit(1)


@app.command()
def process(
    config_file: Path = typer.Argument(..., help="配置文件路径"),
    files: list[Path] = typer.Option(None, "--file", "-f", help="指定文件（可多次）")
):
    """处理文件（提交到GitHub）
    
    从inbox读取文件，移动到正确位置，并提交到GitHub。
    """
    try:
        # 加载配置
        config = Config.load(config_file)
        m = get_messages(config.language)
        
        # 创建处理器
        processor = FileProcessor(config)
        
        # 确定要处理的文件
        if files:
            # 用户指定了文件
            file_list = files
        else:
            # 处理整个inbox
            file_list = [f for f in config.inbox.iterdir() if f.is_file()]
        
        if not file_list:
            print(m.t('inbox.empty', default='收件箱为空'))
            print(f"收件箱：{config.inbox}")
            return
        
        print(f"发现 {len(file_list)} 个文件\n")
        
        # 批量处理
        success, failed = processor.process_batch(file_list)
        
        # 显示结果
        print("\n" + "=" * 60)
        if failed == 0:
            print(f"  全部成功")
        else:
            print(f"  部分失败")
        print("=" * 60)
        print(f"\n成功：{success}")
        print(f"失败：{failed}")
        
        if failed > 0:
            print(f"\n失败的文件已移至：{config.failed}")
            raise typer.Exit(1)
        
    except ConfigError as e:
        print(f"错误：配置错误：{e}")
        raise typer.Exit(1)
    except Exception as e:
        print(f"错误：处理失败：{e}")
        raise typer.Exit(1)


@app.command()
def delete(
    pattern: str = typer.Argument(..., help="文件名模式（支持通配符）"),
    config_file: Path = typer.Argument(..., help="配置文件路径")
):
    """删除文件（从本地仓库删除并push）
    
    示例：
        asset-handoffer delete "Hero_*.fbx" config.yaml
    """
    try:
        config = Config.load(config_file)
        repo = GitRepo(config.repo)
        
        # 搜索匹配的文件
        matches = list(config.repo.rglob(pattern))
        
        if not matches:
            print(f"未找到匹配的文件：{pattern}")
            return
        
        # 显示
        print(f"找到 {len(matches)} 个文件：\n")
        for match in matches:
            rel_path = match.relative_to(config.repo)
            print(f"  {rel_path}")
        
        # 确认
        if not typer.confirm("\n确认删除？"):
            print("已取消")
            return
        
        # 删除
        for match in matches:
            match.unlink()
            repo.remove(match)
        
        # 提交
        repo.commit(f"Delete: {pattern}")
        repo.push()
        
        print(f"\n已删除 {len(matches)} 个文件")
        
    except Exception as e:
        print(f"错误：删除失败：{e}")
        raise typer.Exit(1)


@app.command()
def status(config_file: Path = typer.Argument(..., help="配置文件路径")):
    """查看收件箱状态"""
    try:
        config = Config.load(config_file)
        
        # 扫描inbox
        files = [f for f in config.inbox.iterdir() if f.is_file()]
        
        print(f"收件箱：{config.inbox}\n")
        
        if not files:
            print("收件箱为空")
            return
        
        print(f"待处理文件 ({len(files)}):\n")
        for f in files:
            size_mb = f.stat().st_size / (1024 * 1024)
            print(f"  {f.name} ({size_mb:.2f} MB)")
        
        print(f"\n运行：asset-handoffer process {config_file}")
        
    except Exception as e:
        print(f"错误：{e}")
        raise typer.Exit(1)





def main():
    """主入口"""
    app()


if __name__ == "__main__":
    main()
