"""主程序入口"""

import os
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

from .config import config_manager
from .github_analyzer import GitHubAnalyzer
from .ai_analyzer import AIAnalyzer
from .visualizer import DocumentVisualizer
from .supabase_client import supabase_manager


app = typer.Typer(
    name="biotools-agent",
    help="生物信息学GitHub仓库分析工具",
    add_completion=False
)
console = Console()


@app.command()
def analyze(
    repo_url: str = typer.Argument(..., help="GitHub仓库URL"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="输出目录"),
    env_file: Optional[str] = typer.Option(None, "--env-file", help=".env配置文件路径"),
    formats: str = typer.Option("html,md,json", "--formats", "-f", help="输出格式 (html,md,json)"),
    save_to_db: bool = typer.Option(True, "--save-to-db/--no-save-to-db", "-s/-S", help="是否将结果保存到Supabase数据库 (默认: 保存)"),
):
    """分析GitHub生物信息学工具仓库"""
    
    console.print(Panel(
        f"[bold blue]BioTools Agent[/bold blue]\n"
        f"分析仓库: [green]{repo_url}[/green]",
        title="🧬 生物信息学工具分析",
        expand=False
    ))
    
    # 如果指定了env文件，重新加载配置
    if env_file:
        from .config import ConfigManager
        global config_manager
        config_manager = ConfigManager(env_file)
    
    # 验证配置
    is_valid, errors = config_manager.validate_config()
    if not is_valid:
        console.print("[red]❌ 配置错误:[/red]")
        for error in errors:
            console.print(f"  • {error}")
        console.print("\n请检查您的.env文件或环境变量配置")
        console.print("参考示例: env.example")
        raise typer.Exit(1)
    
    # 解析输出格式
    output_formats = [f.strip().lower() for f in formats.split(",")]
    valid_formats = {"html", "md", "json"}
    if not all(f in valid_formats for f in output_formats):
        console.print(f"[red]❌ 错误: 无效的输出格式。支持的格式: {', '.join(valid_formats)}[/red]")
        raise typer.Exit(1)
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # 1. 初始化分析器
            task1 = progress.add_task("初始化分析器...", total=None)
            github_analyzer = GitHubAnalyzer()
            ai_analyzer = AIAnalyzer()
            visualizer = DocumentVisualizer(output_dir=output_dir or config_manager.config.output_dir)
            progress.update(task1, completed=1)
            
            # 2. 克隆仓库
            task2 = progress.add_task("克隆GitHub仓库...", total=None)
            repo_path = github_analyzer.clone_repository(repo_url)
            progress.update(task2, completed=1)
            
            # 3. 分析仓库基础信息
            task3 = progress.add_task("分析仓库基础信息...", total=None)
            repo_info = github_analyzer.analyze_repository_info(repo_url)
            progress.update(task3, completed=1)
            
            # 4. 提取作者信息
            task4 = progress.add_task("提取作者信息...", total=None)
            authors = github_analyzer.extract_authors_from_repo(repo_path)
            progress.update(task4, completed=1)
            
            # 5. AI分析
            task5 = progress.add_task("AI分析项目内容...", total=None)
            analysis = ai_analyzer.analyze_repository_content(repo_path, repo_info, authors)
            progress.update(task5, completed=1)
            
            # 6. 生成报告
            task6 = progress.add_task("生成可视化报告...", total=None)
            reports = {}
            
            if "html" in output_formats:
                reports["html"] = visualizer.generate_html_report(analysis)
            if "md" in output_formats:
                reports["markdown"] = visualizer.generate_markdown_report(analysis)
            if "json" in output_formats:
                reports["json"] = visualizer.generate_json_report(analysis)
            
            progress.update(task6, completed=1)
        
        # 显示结果摘要
        _display_analysis_summary(analysis, reports)
        
        # 7. 保存到数据库 (如果启用)
        if save_to_db:
            _save_analysis_to_database(analysis)
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ 用户中断操作[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ 分析失败: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """显示版本信息"""
    console.print("[bold blue]BioTools Agent[/bold blue] v0.1.0")
    console.print("生物信息学GitHub仓库分析工具")


@app.command()
def config(
    env_file: Optional[str] = typer.Option(None, "--env-file", help=".env配置文件路径"),
):
    """检查配置是否正确"""
    
    # 如果指定了env文件，重新加载配置
    if env_file:
        from .config import ConfigManager
        global config_manager
        config_manager = ConfigManager(env_file)
    
    console.print(Panel(
        "[bold blue]BioTools Agent 配置检查[/bold blue]",
        title="⚙️ 配置状态",
        expand=False
    ))
    
    # 验证配置
    is_valid, errors = config_manager.validate_config()
    
    # 显示配置信息
    config_table = Table(title="当前配置")
    config_table.add_column("配置项", style="cyan")
    config_table.add_column("值", style="green")
    config_table.add_column("状态", style="yellow")
    
    config_table.add_row(
        "OPENAI_API_KEY", 
        "***已设置***" if config_manager.config.openai_api_key else "未设置",
        "✅" if config_manager.config.openai_api_key else "❌"
    )
    config_table.add_row("OPENAI_BASE_URL", config_manager.config.openai_base_url, "✅")
    config_table.add_row("OPENAI_MODEL", config_manager.config.openai_model, "✅")
    config_table.add_row(
        "HUB_TOKEN", 
        "***已设置***" if config_manager.config.hub_token else "未设置",
        "✅" if config_manager.config.hub_token else "⚠️"
    )
    config_table.add_row(
        "SUPABASE_URL", 
        "***已设置***" if config_manager.config.supabase_url else "未设置",
        "✅" if config_manager.config.supabase_url else "⚠️"
    )
    config_table.add_row(
        "SUPABASE_KEY", 
        "***已设置***" if config_manager.config.supabase_key else "未设置",
        "✅" if config_manager.config.supabase_key else "⚠️"
    )
    config_table.add_row("TMP_DIR", config_manager.config.tmp_dir, "✅")
    config_table.add_row("OUTPUT_DIR", config_manager.config.output_dir, "✅")
    
    console.print(config_table)
    
    if is_valid:
        console.print("\n[bold green]✅ 配置验证通过！[/bold green]")
        console.print("您可以开始使用BioTools Agent进行分析。")
    else:
        console.print("\n[bold red]❌ 配置验证失败！[/bold red]")
        for error in errors:
            console.print(f"  • {error}")
        console.print("\n请参考env.example文件配置您的环境变量。")


def _display_analysis_summary(analysis, reports):
    """显示分析结果摘要"""
    
    # 基础信息表格
    info_table = Table(title="📊 分析结果摘要")
    info_table.add_column("项目", style="cyan")
    info_table.add_column("信息", style="green")
    
    info_table.add_row("项目名称", analysis.repository.name)
    info_table.add_row("项目地址", str(analysis.repository.url))
    info_table.add_row("主要语言", analysis.repository.language or "未知")
    info_table.add_row("Stars", str(analysis.repository.stars))
    info_table.add_row("Forks", str(analysis.repository.forks))
    info_table.add_row("作者数量", str(len(analysis.authors)))
    info_table.add_row("发表文章", str(len(analysis.publications)))
    
    console.print(info_table)
    
    # 功能特性
    if analysis.functionality.key_features:
        console.print("\n[bold yellow]🔧 核心功能:[/bold yellow]")
        for feature in analysis.functionality.key_features[:5]:  # 显示前5个功能
            console.print(f"  • {feature}")
    
    # 生成的报告
    console.print(f"\n[bold green]📄 已生成报告:[/bold green]")
    for format_name, file_path in reports.items():
        console.print(f"  • {format_name.upper()}: [cyan]{file_path}[/cyan]")
    
    console.print(f"\n[bold blue]✅ 分析完成![/bold blue]")


def _save_analysis_to_database(analysis):
    """将分析结果保存到Supabase数据库"""
    console.print("\n[bold yellow]💾 正在保存分析结果到数据库...[/bold yellow]")
    
    # 检查Supabase是否已配置
    if not supabase_manager.is_configured():
        console.print("[red]❌ Supabase 未正确配置，无法保存结果。请检查 .env 文件中的 SUPABASE_URL 和 SUPABASE_KEY。[/red]")
        return
    
    # 调用Supabase客户端保存数据
    success = supabase_manager.save_analysis_result(analysis)
    
    if success:
        console.print("[bold green]✅ 分析结果已成功保存到数据库![/bold green]")
    else:
        console.print("[red]❌ 保存分析结果到数据库失败。[/red]")


if __name__ == "__main__":
    app()