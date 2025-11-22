"""AI分析器适配器，提供新旧实现的统一接口和智能切换"""

import asyncio
from pathlib import Path

from .config import AppConfig
from .agent_analyzer import AgentAIAnalyzer

# 延迟导入传统分析器，只在需要时加载
LegacyAIAnalyzer = None


class AIAnalyzer:
    """AI分析器统一接口，支持新旧实现智能切换"""

    def __init__(self, config_override: dict = None):
        """
        初始化AI分析器

        Args:
            config_override: 配置覆盖字典，可以包含：
                - use_agent: bool - 强制使用代理模式
                - use_legacy: bool - 强制使用传统模式
                - auto_select: bool - 自动选择最佳模式（默认）
        """
        self.config_override = config_override or {}
        self.auto_select = self.config_override.get('auto_select', True)
        self.use_agent = self._select_analysis_mode()

        if self.use_agent:
            print("🤖 使用Claude Code SDK代理模式")
            self.analyzer = AgentAIAnalyzer(self.config_override)
        else:
            if LegacyAIAnalyzer is None and not self._can_use_legacy_mode():
                raise ImportError("传统模式依赖不可用，请安装openai包或使用代理模式")
            print("🔧 使用传统LLM模式")
            self.analyzer = LegacyAIAnalyzer(self.config_override)

    def _select_analysis_mode(self) -> bool:
        """智能选择分析模式"""
        # 如果配置中明确指定了模式
        if 'use_agent' in self.config_override:
            return self.config_override['use_agent']
        if 'use_legacy' in self.config_override:
            return not self.config_override['use_legacy']

        if not self.auto_select:
            return True  # 默认使用代理模式

        # 自动选择逻辑
        try:
            # 尝试导入代理模块
            from claude_agent_sdk import ClaudeSDKClient
            return True  # 导入成功，可以使用代理模式
        except ImportError:
            print("⚠️ Claude Agent SDK未安装")
            # 检查是否可以使用传统模式
            if self._can_use_legacy_mode():
                print("🔄 回退到传统LLM模式")
                return False
            else:
                print("❌ 传统模式依赖不可用，无法继续")
                raise ImportError("没有可用的AI分析模式")
        except Exception as e:
            print(f"⚠️ 代理模式初始化失败: {e}")
            if self._can_use_legacy_mode():
                print("🔄 回退到传统LLM模式")
                return False
            else:
                print("❌ 传统模式也不可用，无法继续")
                raise ImportError("没有可用的AI分析模式")

    def _can_use_legacy_mode(self) -> bool:
        """检查是否可以使用传统模式"""
        global LegacyAIAnalyzer
        if LegacyAIAnalyzer is None:
            try:
                from .ai_analyzer import AIAnalyzer as ImportedLegacyAnalyzer
                LegacyAIAnalyzer = ImportedLegacyAnalyzer
                return True
            except ImportError:
                return False
        return True

    def analyze_repository_content(self, repo_path: Path, repo_info, authors):
        """
        分析仓库内容（同步接口）

        Args:
            repo_path: 仓库路径
            repo_info: 仓库信息
            authors: 作者列表

        Returns:
            BioToolAnalysis: 分析结果
        """
        if self.use_agent:
            # 异步调用，但保持同步接口
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(
                    self.analyzer.analyze_repository_content(repo_path, repo_info, authors)
                )
            finally:
                loop.close()
        else:
            return self.analyzer.analyze_repository_content(repo_path, repo_info, authors)

    async def analyze_repository_content_async(self, repo_path: Path, repo_info, authors):
        """
        分析仓库内容（异步接口）

        Args:
            repo_path: 仓库路径
            repo_info: 仓库信息
            authors: 作者列表

        Returns:
            BioToolAnalysis: 分析结果
        """
        if self.use_agent:
            return await self.analyzer.analyze_repository_content(repo_path, repo_info, authors)
        else:
            # 对于传统模式，需要在事件循环中运行
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                self.analyzer.analyze_repository_content,
                repo_path, repo_info, authors
            )

    def get_mode_info(self) -> dict:
        """获取当前模式信息"""
        return {
            "use_agent": self.use_agent,
            "analyzer_type": type(self.analyzer).__name__,
            "config_override": self.config_override
        }


# 为了向后兼容，创建一个便利函数
def create_ai_analyzer(config_override: dict = None, force_legacy: bool = False) -> AIAnalyzer:
    """
    创建AI分析器的便利函数

    Args:
        config_override: 配置覆盖
        force_legacy: 强制使用传统模式

    Returns:
        AIAnalyzer: AI分析器实例
    """
    if force_legacy:
        config_override = config_override or {}
        config_override['use_legacy'] = True
        config_override['auto_select'] = False

    return AIAnalyzer(config_override)


# 配置验证函数
def validate_ai_config(config: AppConfig) -> dict:
    """
    验证AI配置

    Args:
        config: 应用配置

    Returns:
        dict: 验证结果
    """
    result = {
        "claude_available": False,
        "legacy_available": False,
        "recommended_mode": "agent",
        "issues": [],
        "warnings": []
    }

    # 检查Claude SDK配置
    if config.claude_sdk.claude_api_key:
        result["claude_available"] = True
    else:
        result["issues"].append("Claude API密钥未配置 (CLAUDE_API_KEY)")

    # 检查传统AI配置
    if config.legacy_ai.openai_api_key:
        result["legacy_available"] = True
    else:
        result["issues"].append("OpenAI API密钥未配置 (OPENAI_API_KEY)")

    # 推荐模式选择
    if result["claude_available"]:
        result["recommended_mode"] = "agent"
    elif result["legacy_available"]:
        result["recommended_mode"] = "legacy"
    else:
        result["recommended_mode"] = "none"
        result["issues"].append("没有可用的AI配置")

    # 检查代理配置
    if not config.claude_sdk.fallback_to_programmatic and result["claude_available"]:
        result["warnings"].append("未启用程序化代理备选，可能影响稳定性")

    return result


if __name__ == "__main__":
    # 测试配置
    from .config import config_manager

    print("🔍 测试AI分析器配置...")

    # 验证配置
    validation = validate_ai_config(config_manager.config)
    print(f"推荐模式: {validation['recommended_mode']}")

    if validation['issues']:
        print("配置问题:")
        for issue in validation['issues']:
            print(f"  - {issue}")

    if validation['warnings']:
        print("配置警告:")
        for warning in validation['warnings']:
            print(f"  - {warning}")

    # 测试分析器创建
    try:
        analyzer = create_ai_analyzer()
        mode_info = analyzer.get_mode_info()
        print(f"\n创建的分析器模式: {mode_info}")
    except Exception as e:
        print(f"创建分析器失败: {e}")