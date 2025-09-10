"""数据模型定义"""

from typing import Dict, List, Optional

from pydantic import BaseModel, HttpUrl


class RepositoryInfo(BaseModel):
    """仓库基础信息模型"""

    name: str
    url: HttpUrl
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    license: Optional[str] = None


class AuthorInfo(BaseModel):
    """作者信息模型"""

    name: str
    email: Optional[str] = None
    github_username: Optional[str] = None


class Publication(BaseModel):
    """发表文章信息模型"""

    title: str
    authors: List[str]
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None


class FunctionalityInfo(BaseModel):
    """功能信息模型"""

    main_purpose: str
    key_features: List[str]
    input_formats: List[str]
    output_formats: List[str]
    dependencies: List[str]


class UsageInfo(BaseModel):
    """使用方法信息模型"""

    installation: str
    basic_usage: str
    examples: List[str]
    parameters: List[str]


class DeploymentInfo(BaseModel):
    """部署信息模型 - Linus风格：简单实用"""

    installation_methods: List[str]  # 安装方式：conda, pip, docker等
    system_requirements: List[str]  # 系统要求
    container_support: List[str]  # 容器支持：docker, singularity等
    cloud_deployment: List[str]  # 云部署选项
    configuration_files: List[str]  # 配置文件


class TestingInfo(BaseModel):
    """测试信息模型 - Linus风格：实用导向"""

    test_commands: List[str]  # 测试命令
    test_data_sources: List[str]  # 测试数据来源
    example_datasets: List[str]  # 示例数据集
    validation_methods: List[str]  # 验证方法
    benchmark_datasets: List[str]  # 基准数据集


class DataRequirements(BaseModel):
    """数据需求模型 - Linus风格：明确具体"""

    required_inputs: List[str]  # 必需输入
    optional_inputs: List[str]  # 可选输入
    data_formats: List[str]  # 数据格式要求
    file_size_limits: str  # 文件大小限制
    preprocessing_steps: List[str]  # 预处理步骤


class ProjectArchitecture(BaseModel):
    """项目架构信息模型"""

    programming_languages: List[str]
    frameworks: List[str]
    directory_structure: Dict[str, str]
    main_components: List[str]
    entry_points: List[str]
    config_files: List[str]
    test_structure: Dict[str, str]


class CodeQualityInfo(BaseModel):
    """代码质量信息模型"""

    code_structure: str
    documentation_quality: str
    test_coverage: str
    code_style: str
    best_practices: List[str]


class PerformanceInfo(BaseModel):
    """性能特征信息模型"""

    time_complexity: str
    space_complexity: str
    parallelization: str
    resource_usage: str
    optimization_suggestions: List[str]


class BioinformaticsExpertiseInfo(BaseModel):
    """生物信息学专业性信息模型"""

    algorithm_accuracy: str
    benchmark_results: str
    tool_comparison: str
    applicable_scenarios: List[str]


class UsabilityInfo(BaseModel):
    """可用性信息模型"""

    documentation_completeness: str
    user_interface: str
    error_handling: str
    learning_curve: str


class BioToolAnalysis(BaseModel):
    """完整的生物信息学工具分析结果"""

    repository: RepositoryInfo
    authors: List[AuthorInfo]
    publications: List[Publication]
    functionality: FunctionalityInfo
    usage: UsageInfo
    architecture: Optional[ProjectArchitecture] = None
    code_quality: Optional[CodeQualityInfo] = None
    performance: Optional[PerformanceInfo] = None
    bioinformatics_expertise: Optional[BioinformaticsExpertiseInfo] = None
    usability: Optional[UsabilityInfo] = None
    deployment: Optional[DeploymentInfo] = None  # 新增：部署信息
    testing: Optional[TestingInfo] = None  # 新增：测试信息
    data_requirements: Optional[DataRequirements] = None  # 新增：数据需求
    analysis_timestamp: str
