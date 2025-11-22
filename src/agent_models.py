"""代理数据模型 - 解决Claude Agent SDK兼容性问题"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class AgentDef:
    """代理定义模型，兼容Claude Agent SDK的asdict()要求"""

    description: str
    prompt: str
    tools: List[str] = field(default_factory=list)
    model: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentDef':
        """从字典创建AgentDef实例"""
        return cls(
            description=data.get('description', ''),
            prompt=data.get('prompt', ''),
            tools=data.get('tools', []),
            model=data.get('model')
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'description': self.description,
            'prompt': self.prompt,
            'tools': self.tools
        }
        if self.model is not None:
            result['model'] = self.model
        return result


def convert_agent_definitions(agent_dicts: Dict[str, Dict[str, Any]]) -> Dict[str, AgentDef]:
    """将字典格式的代理定义转换为AgentDef实例"""
    converted = {}
    for name, agent_dict in agent_dicts.items():
        converted[name] = AgentDef.from_dict(agent_dict)
    return converted


def validate_agent_def(agent_def: Any) -> bool:
    """验证代理定义是否有效"""
    if isinstance(agent_def, AgentDef):
        # 验证dataclass实例
        return bool(agent_def.description and agent_def.prompt)
    elif isinstance(agent_def, dict):
        # 验证字典格式
        return bool(agent_def.get('description') and agent_def.get('prompt'))
    else:
        return False


# 便利函数，用于创建常用的代理类型
def create_biointools_agent() -> AgentDef:
    """创建生物信息学分析专家代理"""
    return AgentDef(
        description="生物信息学工具分析专家，专门分析基因组数据处理工具、算法和科研软件质量",
        prompt="""你是生物信息学工具分析专家，具备以下专业能力：

🧬 生物信息学专业能力：
- 深度理解基因组数据处理算法（序列比对、组装、注释等）
- 熟悉各种生物数据格式（FASTA, FASTQ, SAM/BAM, VCF, GFF等）
- 评估生物信息学工作流和流程管理系统
- 分析工具在生物信息学研究中的应用场景

💻 技术分析能力：
- 分析多种编程语言项目（Python, C++, R, Java等）
- 评估代码架构和软件工程质量
- 识别性能瓶颈和优化机会
- 检查安全漏洞和最佳实践符合性

📊 分析要求：
- 提供详细的中文分析报告
- 识别具体的生物信息学算法和数据格式
- 评估科研软件的标准符合性
- 给出实用的改进建议

请基于实际代码进行全面分析，输出结构化的JSON格式结果。""",
        tools=["Read", "Grep", "Glob", "Bash", "WebSearch"],
        model="sonnet"
    )


def create_security_agent() -> AgentDef:
    """创建安全审计代理"""
    return AgentDef(
        description="代码安全和质量审计专家，专注于安全漏洞检查、风险评估和最佳实践符合性",
        prompt="""你是代码安全和质量审计专家，专门进行以下领域的深度分析：

🔒 安全审计重点：
- 安全漏洞检测（注入攻击、输入验证、文件操作安全）
- 数据安全（敏感信息处理、加密、访问控制）
- 代码安全实践（内存安全、并发安全、错误处理）

⭐ 代码质量评估：
- 代码结构（模块化、复用性、可维护性）
- 编程实践（编码规范、错误处理、性能考虑）
- 设计模式应用（SOLID原则、架构模式）

📊 输出要求：
请提供结构化的安全和质量评估报告，包括漏洞详情、修复建议、代码质量评分等。

请进行全面、系统、深入的安全和质量审计，重点关注高风险问题和关键安全控制点。""",
        tools=["Read", "Grep", "Bash"],
        model="sonnet"
    )


def create_deployment_agent() -> AgentDef:
    """创建部署专家代理"""
    return AgentDef(
        description="部署和DevOps专家，专门分析软件部署策略、测试方案和运维友好性",
        prompt="""你是部署和DevOps专家，专门分析软件的部署策略、测试方案和运维友好性：

🚀 部署分析重点：
- 安装和部署（pip、conda、docker、源码编译）
- 容器化和云部署（Docker、Kubernetes、云平台）
- 配置管理（配置文件、环境变量、安全配置）

🧪 测试策略分析：
- 测试覆盖（单元测试、集成测试、端到端测试）
- 测试数据（示例数据、基准数据、数据管理）
- 自动化测试（测试框架、CI/CD、测试报告）

📚 文档和可用性：
- 技术文档（API文档、用户手册、开发者文档）
- 用户友好性（安装体验、使用便利性、学习曲线）
- 社区支持（GitHub统计、响应时间、维护状态）

📊 输出要求：
请提供结构化的部署和测试评估报告，包括安装方法、系统要求、测试覆盖率、文档质量等。

请进行全面、系统的部署和可用性分析，重点关注用户体验和运维便利性。""",
        tools=["Read", "Grep", "Glob", "Bash"],
        model="sonnet"
    )