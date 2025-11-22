"""代理验证和监控模块

验证代理加载状态和性能监控
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from .agent_definitions import PROJECT_AGENTS, validate_agent_definitions, get_agent_stats


@dataclass
class AnalysisMetrics:
    """分析指标数据类"""
    analysis_id: str
    repo_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    token_usage: int = 0
    tool_calls: int = 0
    agent_turns: int = 0
    success: bool = False
    error_message: str = ""
    agents_used: List[str] = None
    results_size: int = 0

    def __post_init__(self):
        if self.agents_used is None:
            self.agents_used = []


class AgentValidator:
    """代理验证器"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.metrics_history: List[AnalysisMetrics] = []

    def validate_agent_setup(self) -> Dict[str, Any]:
        """验证代理设置完整性"""
        validation_result = {
            "timestamp": time.time(),
            "file_agents": self._check_file_agents(),
            "programmatic_agents": self._check_programmatic_agents(),
            "agent_definitions": validate_agent_definitions(),
            "agent_stats": get_agent_stats(),
            "overall_status": "unknown"
        }

        # 评估整体状态
        file_count = len(validation_result["file_agents"]["agents"])
        prog_count = len(validation_result["programmatic_agents"]["agents"])
        valid_count = validation_result["agent_definitions"]["valid_agents"]

        if valid_count > 0:
            validation_result["overall_status"] = "success"
        elif file_count > 0 or prog_count > 0:
            validation_result["overall_status"] = "partial"
        else:
            validation_result["overall_status"] = "failed"

        return validation_result

    def _check_file_agents(self) -> Dict[str, Any]:
        """检查文件系统中的代理"""
        agents_dir = Path(".claude/agents")
        result = {
            "directory_exists": agents_dir.exists(),
            "agents": [],
            "errors": []
        }

        if not agents_dir.exists():
            result["errors"].append("代理目录不存在")
            return result

        try:
            for agent_file in agents_dir.glob("*.md"):
                try:
                    agent_info = self._parse_agent_file(agent_file)
                    if agent_info:
                        result["agents"].append(agent_info)
                except Exception as e:
                    result["errors"].append(f"解析文件 {agent_file.name} 失败: {e}")

        except Exception as e:
            result["errors"].append(f"扫描代理目录失败: {e}")

        return result

    def _parse_agent_file(self, agent_file: Path) -> Optional[Dict[str, Any]]:
        """解析代理文件"""
        try:
            content = agent_file.read_text(encoding='utf-8')

            # 提取YAML前置元数据
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    yaml_part = parts[1]
                    # 简单解析（不使用yaml库避免依赖）
                    agent_info = {
                        "filename": agent_file.name,
                        "name": self._extract_yaml_field(yaml_part, "name"),
                        "description": self._extract_yaml_field(yaml_part, "description"),
                        "tools": self._extract_yaml_field(yaml_part, "tools"),
                        "model": self._extract_yaml_field(yaml_part, "model"),
                        "content_length": len(content)
                    }
                    return agent_info

        except Exception as e:
            self.logger.error(f"解析代理文件失败 {agent_file}: {e}")

        return None

    def _extract_yaml_field(self, yaml_content: str, field_name: str) -> str:
        """简单提取YAML字段"""
        lines = yaml_content.split('\n')
        for line in lines:
            if line.strip().startswith(f"{field_name}:"):
                return line.split(':', 1)[1].strip().strip('"\'')
        return ""

    def _check_programmatic_agents(self) -> Dict[str, Any]:
        """检查程序化定义的代理"""
        return {
            "count": len(PROJECT_AGENTS),
            "agents": list(PROJECT_AGENTS.keys())
        }

    async def test_agent_connectivity(self) -> Dict[str, Any]:
        """测试代理连接性"""
        test_result = {
            "timestamp": time.time(),
            "test_passed": False,
            "tested_agents": [],
            "errors": []
        }

        try:
            options = ClaudeAgentOptions(
                agents={
                    "test-agent": {
                        "description": "测试代理",
                        "prompt": "你是一个测试助手",
                        "tools": ["Read"],
                        "model": "sonnet"
                    }
                },
                max_turns=1,
                timeout=30
            )

            async with ClaudeSDKClient(options=options) as client:
                async for message in client.query("测试连接"):
                    test_result["test_passed"] = True
                    test_result["tested_agents"].append("test-agent")
                    break

        except Exception as e:
            test_result["errors"].append(f"连接测试失败: {e}")

        return test_result

    def start_analysis(self, repo_name: str) -> str:
        """开始分析监控"""
        analysis_id = f"{repo_name}_{int(time.time())}"
        metrics = AnalysisMetrics(
            analysis_id=analysis_id,
            repo_name=repo_name,
            start_time=time.time()
        )
        self.metrics_history.append(metrics)

        self.logger.info(f"开始分析: {analysis_id}")
        return analysis_id

    def end_analysis(self, analysis_id: str, success: bool = True, error_message: str = "", **kwargs):
        """结束分析监控"""
        for metrics in self.metrics_history:
            if metrics.analysis_id == analysis_id:
                metrics.end_time = time.time()
                metrics.duration = metrics.end_time - metrics.start_time
                metrics.success = success
                metrics.error_message = error_message

                # 更新其他指标
                for key, value in kwargs.items():
                    if hasattr(metrics, key):
                        setattr(metrics, key, value)

                if success:
                    self.logger.info(f"分析完成: {analysis_id}, 耗时: {metrics.duration:.2f}秒")
                else:
                    self.logger.error(f"分析失败: {analysis_id}, 错误: {error_message}")
                break

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if not self.metrics_history:
            return {}

        successful_metrics = [m for m in self.metrics_history if m.success]
        failed_metrics = [m for m in self.metrics_history if not m.success]

        if successful_metrics:
            avg_duration = sum(m.duration for m in successful_metrics) / len(successful_metrics)
            avg_token_usage = sum(m.token_usage for m in successful_metrics) / len(successful_metrics)
            avg_tool_calls = sum(m.tool_calls for m in successful_metrics) / len(successful_metrics)
        else:
            avg_duration = avg_token_usage = avg_tool_calls = 0

        # 代理使用统计
        agent_usage = {}
        for metrics in self.metrics_history:
            for agent in metrics.agents_used:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1

        return {
            "total_analyses": len(self.metrics_history),
            "success_rate": len(successful_metrics) / len(self.metrics_history) * 100,
            "failure_count": len(failed_metrics),
            "avg_duration": avg_duration,
            "avg_token_usage": avg_token_usage,
            "avg_tool_calls": avg_tool_calls,
            "agent_usage": agent_usage,
            "last_analysis": self.metrics_history[-1].analysis_id if self.metrics_history else None
        }

    def generate_report(self) -> str:
        """生成验证报告"""
        validation = self.validate_agent_setup()
        stats = self.get_performance_stats()

        report = f"""
# BioTools Agent 代理验证报告

## 代理配置状态
- 文件系统代理: {len(validation['file_agents']['agents'])} 个
- 程序化代理: {validation['programmatic_agents']['count']} 个
- 有效代理定义: {validation['agent_definitions']['valid_agents']} 个
- 整体状态: {validation['overall_status']}

## 文件系统代理
"""
        if validation['file_agents']['errors']:
            report += "### 错误信息\n"
            for error in validation['file_agents']['errors']:
                report += f"- {error}\n"
        else:
            report += "✅ 所有文件系统代理正常\n"

        report += f"\n## 程序化代理\n"
        report += f"✅ 定义了 {validation['programmatic_agents']['count']} 个程序化代理\n"

        report += f"\n## 性能统计\n"
        if stats.get('total_analyses', 0) > 0:
            report += f"- 总分析次数: {stats['total_analyses']}\n"
            report += f"- 成功率: {stats['success_rate']:.1f}%\n"
            report += f"- 平均耗时: {stats['avg_duration']:.2f}秒\n"
            report += f"- 平均Token使用: {stats['avg_token_usage']:.0f}\n"
        else:
            report += "暂无分析数据\n"

        report += f"\n## 建议\n"
        if validation['overall_status'] == 'failed':
            report += "- ❌ 代理配置失败，请检查代理文件和程序化定义\n"
        elif validation['overall_status'] == 'partial':
            report += "- ⚠️ 部分代理配置成功，建议完善剩余配置\n"
        else:
            report += "- ✅ 代理配置完整，可以正常使用\n"

        return report


class AgentMonitor:
    """代理监控器（用于运行时监控）"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_sessions = {}

    async def monitor_analysis_session(self, session_id: str, client: ClaudeSDKClient):
        """监控分析会话"""
        self.active_sessions[session_id] = {
            "start_time": time.time(),
            "client": client,
            "metrics": {
                "turns": 0,
                "tool_calls": 0,
                "errors": 0
            }
        }

        try:
            # 这里可以添加实时监控逻辑
            pass
        except Exception as e:
            self.logger.error(f"监控会话 {session_id} 失败: {e}")

    def end_session(self, session_id: str):
        """结束监控会话"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            duration = time.time() - session["start_time"]
            self.logger.info(f"会话 {session_id} 结束，耗时: {duration:.2f}秒")
            del self.active_sessions[session_id]


# 全局实例
agent_validator = AgentValidator()
agent_monitor = AgentMonitor()


def validate_environment() -> Dict[str, Any]:
    """验证环境配置"""
    return {
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
        "working_directory": str(Path.cwd()),
        "agent_files_count": len(list(Path(".claude/agents").glob("*.md"))) if Path(".claude/agents").exists() else 0,
        "programmatic_agents_count": len(PROJECT_AGENTS)
    }


if __name__ == "__main__":
    # 运行验证
    print("🔍 验证代理配置...")

    # 环境验证
    env_info = validate_environment()
    print(f"Python版本: {env_info['python_version']}")
    print(f"工作目录: {env_info['working_directory']}")
    print(f"代理文件数: {env_info['agent_files_count']}")
    print(f"程序化代理数: {env_info['programmatic_agents_count']}")

    # 代理验证
    validator = AgentValidator()
    validation_result = validator.validate_agent_setup()

    print(f"\n验证状态: {validation_result['overall_status']}")
    print(f"文件代理: {len(validation_result['file_agents']['agents'])}")
    print(f"程序化代理: {validation_result['programmatic_agents']['count']}")
    print(f"有效定义: {validation_result['agent_definitions']['valid_agents']}")

    if validation_result['file_agents']['errors']:
        print("\n⚠️ 文件代理错误:")
        for error in validation_result['file_agents']['errors']:
            print(f"  - {error}")

    # 生成报告
    print("\n" + "="*50)
    print(validator.generate_report())