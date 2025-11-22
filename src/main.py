"""主程序入口"""

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .ai_analyzer_adapter import AIAnalyzer
from .config import ConfigManager, config_manager
from .github_analyzer import GitHubAnalyzer
from .supabase_client import supabase_manager
from .visualizer import DocumentVisualizer

app = typer.Typer(
    name="biotools-agent", help="生物信息学GitHub仓库分析工具", add_completion=False
)
console = Console()


@app.command()
def analyze(
    repo_url: str = typer.Argument(..., help="GitHub仓库URL"),
    output_dir: Optional[str] = typer.Option(None, "--output", "-o", help="输出目录"),
    env_file: Optional[str] = typer.Option(None, "--env-file", help=".env配置文件路径"),
    formats: str = typer.Option(
        "html,md,json", "--formats", "-f", help="输出格式 (html,md,json)"
    ),
    save_to_db: bool = typer.Option(
        True,
        "--save-to-db/--no-save-to-db",
        "-s/-S",
        help="是否将结果保存到Supabase数据库 (默认: 保存)",
    ),
):
    """分析GitHub生物信息学工具仓库"""

    console.print(
        Panel(
            f"[bold blue]BioTools Agent[/bold blue]\n"
            f"分析仓库: [green]{repo_url}[/green]",
            title="🧬 生物信息学工具分析",
            expand=False,
        )
    )

    # 如果指定了env文件，重新加载配置
    if env_file:
        current_config = ConfigManager(env_file)
    else:
        current_config = config_manager

    # 验证配置
    is_valid, errors = current_config.validate_config()
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
        console.print(
            f"[red]❌ 错误: 无效的输出格式。支持的格式: {', '.join(valid_formats)}[/red]"
        )
        raise typer.Exit(1)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # 1. 初始化分析器
            task1 = progress.add_task("初始化分析器...", total=None)
            github_analyzer = GitHubAnalyzer()
            ai_analyzer = AIAnalyzer()
            visualizer = DocumentVisualizer(
                output_dir=output_dir or current_config.config.output_dir
            )
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

            # 5. 分析项目架构
            task5 = progress.add_task("分析项目架构...", total=None)
            architecture = github_analyzer.analyze_project_architecture(repo_path)
            progress.update(task5, completed=1)

            # 6. AI分析
            task6 = progress.add_task("AI分析项目内容...", total=None)
            analysis_result = ai_analyzer.analyze_repository_content(
                repo_path, repo_info, authors
            )
            # 将架构信息和其他AI分析结果添加到分析结果中
            analysis_result.architecture = architecture
            progress.update(task6, completed=1)

            # 7. 安全分析 (MVP新增功能)
            task7 = progress.add_task("安全风险分析...", total=None)
            security_analysis = github_analyzer.analyze_security(repo_path)
            if security_analysis:
                analysis_result.security = security_analysis
                print(f"🔒 安全分析完成: {security_analysis.total_high_risk + security_analysis.total_medium_risk + security_analysis.total_low_risk} 个安全问题")
            else:
                print("⚠️ 安全分析跳过或失败")
            progress.update(task7, completed=1)
            
            analysis = analysis_result

            # 8. 生成报告
            task8 = progress.add_task("生成可视化报告...", total=None)
            reports = {}

            if "html" in output_formats:
                reports["html"] = visualizer.generate_html_report(analysis)
            if "md" in output_formats:
                reports["markdown"] = visualizer.generate_markdown_report(analysis)
            if "json" in output_formats:
                reports["json"] = visualizer.generate_json_report(analysis)

            progress.update(task8, completed=1)

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
        current_config = ConfigManager(env_file)
    else:
        current_config = config_manager

    console.print(
        Panel(
            "[bold blue]BioTools Agent 配置检查[/bold blue]",
            title="⚙️ 配置状态",
            expand=False,
        )
    )

    # 验证配置
    is_valid, errors = current_config.validate_config()

    # 显示配置信息
    config_table = Table(title="当前配置")
    config_table.add_column("配置项", style="cyan")
    config_table.add_column("值", style="green")
    config_table.add_column("状态", style="yellow")

    # Claude SDK配置（推荐）
    config_table.add_row(
        "CLAUDE_API_KEY",
        "***已设置***" if current_config.config.claude_sdk.claude_api_key else "未设置",
        "✅" if current_config.config.claude_sdk.claude_api_key else "❌",
    )
    config_table.add_row("CLAUDE_BASE_URL", current_config.config.claude_sdk.claude_base_url, "✅")
    config_table.add_row("CLAUDE_MODEL", current_config.config.claude_sdk.claude_model, "✅")

    # 传统AI配置（向后兼容）
    config_table.add_row(
        "OPENAI_API_KEY",
        "***已设置***" if current_config.config.legacy_ai.openai_api_key else "未设置",
        "⚠️" if current_config.config.legacy_ai.openai_api_key else "⚪",
    )
    config_table.add_row("OPENAI_BASE_URL", current_config.config.legacy_ai.openai_base_url, "⚪")
    config_table.add_row("OPENAI_MODEL", current_config.config.legacy_ai.openai_model, "⚪")
    config_table.add_row(
        "HUB_TOKEN",
        "***已设置***" if current_config.config.hub_token else "未设置",
        "✅" if current_config.config.hub_token else "⚠️",
    )
    config_table.add_row(
        "SUPABASE_URL",
        "***已设置***" if current_config.config.supabase_url else "未设置",
        "✅" if current_config.config.supabase_url else "⚠️",
    )
    config_table.add_row(
        "SUPABASE_KEY",
        "***已设置***" if current_config.config.supabase_key else "未设置",
        "✅" if current_config.config.supabase_key else "⚠️",
    )
    config_table.add_row("TMP_DIR", current_config.config.tmp_dir, "✅")
    config_table.add_row("OUTPUT_DIR", current_config.config.output_dir, "✅")

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

    # 项目架构信息
    if analysis.architecture:
        console.print("\n[bold magenta]🏗️ 项目架构:[/bold magenta]")
        if analysis.architecture.programming_languages:
            console.print(
                f"  [cyan]编程语言:[/cyan] {', '.join(analysis.architecture.programming_languages)}"
            )
        if analysis.architecture.frameworks:
            console.print(
                f"  [cyan]框架/库:[/cyan] {', '.join(analysis.architecture.frameworks)}"
            )
        if analysis.architecture.entry_points:
            console.print(
                f"  [cyan]入口点:[/cyan] {', '.join(analysis.architecture.entry_points)}"
            )

    # 代码质量信息
    if analysis.code_quality:
        console.print("\n[bold blue]💻 代码质量:[/bold blue]")
        console.print(
            f"  [cyan]代码结构:[/cyan] {analysis.code_quality.code_structure}"
        )
        console.print(
            f"  [cyan]文档质量:[/cyan] {analysis.code_quality.documentation_quality}"
        )

    # 性能特征信息
    if analysis.performance:
        console.print("\n[bold red]⚡ 性能特征:[/bold red]")
        console.print(
            f"  [cyan]时间复杂度:[/cyan] {analysis.performance.time_complexity}"
        )
        console.print(
            f"  [cyan]并行化支持:[/cyan] {analysis.performance.parallelization}"
        )

    # 生物信息学专业性信息
    if analysis.bioinformatics_expertise:
        console.print("\n[bold green]🧬 生物信息学专业性:[/bold green]")
        console.print(
            f"  [cyan]算法准确性:[/cyan] {analysis.bioinformatics_expertise.algorithm_accuracy}"
        )
        if analysis.bioinformatics_expertise.applicable_scenarios:
            console.print(
                f"  [cyan]适用场景:[/cyan] {', '.join(analysis.bioinformatics_expertise.applicable_scenarios[:3])}"
            )

    # 可用性信息
    if analysis.usability:
        console.print("\n[bold yellow]👋 可用性:[/bold yellow]")
        console.print(
            f"  [cyan]文档完整性:[/cyan] {analysis.usability.documentation_completeness}"
        )
        console.print(f"  [cyan]学习曲线:[/cyan] {analysis.usability.learning_curve}")

    # 生成的报告
    console.print("\n[bold green]📄 已生成报告:[/bold green]")
    for format_name, file_path in reports.items():
        console.print(f"  • {format_name.upper()}: [cyan]{file_path}[/cyan]")

    console.print("\n[bold blue]✅ 分析完成![/bold blue]")


def _save_analysis_to_database(analysis):
    """将分析结果保存到Supabase数据库"""
    console.print("\n[bold yellow]💾 正在保存分析结果到数据库...[/bold yellow]")

    # 检查Supabase是否已配置
    if not supabase_manager.is_configured():
        console.print(
            "[red]❌ Supabase 未正确配置，无法保存结果。请检查 .env 文件中的 SUPABASE_URL 和 SUPABASE_KEY。[/red]"
        )
        return

    # 调用Supabase客户端保存数据
    success = supabase_manager.save_analysis_result(analysis)

    if success:
        console.print("[bold green]✅ 分析结果已成功保存到数据库![/bold green]")
    else:
        console.print("[red]❌ 保存分析结果到数据库失败。[/red]")


if __name__ == "__main__":
    app()
