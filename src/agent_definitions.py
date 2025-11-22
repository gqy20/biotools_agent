"""BioTools Agent 代理定义

程序化代理定义，作为文件系统代理的可靠备选方案
"""

from typing import Dict, Any
from .agent_models import AgentDef, create_biointools_agent, create_security_agent, create_deployment_agent

# 生物信息学分析专家代理
BIOTOOLS_ANALYZER_AGENT = create_biointools_agent()

# 安全审计代理
SECURITY_AUDITOR_AGENT = create_security_agent()

# 部署专家代理
DEPLOYMENT_EXPERT_AGENT = create_deployment_agent()

# 所有代理定义（使用AgentDef实例以兼容Claude Agent SDK）
PROJECT_AGENTS = {
    "biotools-analyzer": BIOTOOLS_ANALYZER_AGENT,
    "security-auditor": SECURITY_AUDITOR_AGENT,
    "deployment-expert": DEPLOYMENT_EXPERT_AGENT,
}

# 为了向后兼容，提供字典格式的代理定义
PROJECT_AGENTS_DICT: Dict[str, Dict[str, Any]] = {
    name: agent.to_dict() for name, agent in PROJECT_AGENTS.items()
}

# 分析任务配置
ANALYSIS_TASKS = [
    {
        "agent": "biotools-analyzer",
        "description": "生物信息学功能和算法分析",
        "focus": [
            "functionality", "architecture", "performance",
            "bioinformatics_expertise", "data_requirements"
        ]
    },
    {
        "agent": "security-auditor",
        "description": "代码安全和质量审计",
        "focus": ["security_analysis", "code_quality"]
    },
    {
        "agent": "deployment-expert",
        "description": "部署和测试策略分析",
        "focus": ["deployment", "testing", "documentation", "usability"]
    }
]

# 代理加载验证函数
def validate_agent_definitions() -> Dict[str, Any]:
    """验证代理定义的完整性"""
    from .agent_models import validate_agent_def

    validation_result = {
        "total_agents": len(PROJECT_AGENTS),
        "valid_agents": 0,
        "agent_details": [],
        "missing_fields": []
    }

    for agent_name, agent_def in PROJECT_AGENTS.items():
        agent_status = {
            "name": agent_name,
            "valid": True,
            "missing_fields": []
        }

        # 使用统一的验证函数
        if not validate_agent_def(agent_def):
            agent_status["valid"] = False
            validation_result["missing_fields"].append(f"{agent_name}: 无效的代理定义")

        if agent_status["valid"]:
            validation_result["valid_agents"] += 1

        validation_result["agent_details"].append(agent_status)

    return validation_result

# 获取代理统计信息
def get_agent_stats() -> Dict[str, Any]:
    """获取代理统计信息"""
    return {
        "agent_count": len(PROJECT_AGENTS),
        "agent_names": list(PROJECT_AGENTS.keys()),
        "available_tools": list(set(
            tool for agent in PROJECT_AGENTS.values()
            for tool in agent.tools
        )),
        "models_used": list(set(
            agent.model or "unknown"
            for agent in PROJECT_AGENTS.values()
        )),
        "task_count": len(ANALYSIS_TASKS)
    }

if __name__ == "__main__":
    # 验证代理定义
    validation = validate_agent_definitions()
    print(f"代理验证结果:")
    print(f"  总代理数: {validation['total_agents']}")
    print(f"  有效代理数: {validation['valid_agents']}")
    print(f"  缺失字段: {validation['missing_fields']}")

    # 显示统计信息
    stats = get_agent_stats()
    print(f"\n代理统计:")
    print(f"  代理名称: {', '.join(stats['agent_names'])}")
    print(f"  可用工具: {', '.join(stats['available_tools'])}")
    print(f"  使用模型: {', '.join(stats['models_used'])}")