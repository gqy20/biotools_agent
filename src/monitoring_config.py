"""监控配置模块"""

from typing import Optional
from pydantic import BaseModel, Field


class MonitoringConfig(BaseModel):
    """监控配置模型"""

    # OpenTelemetry配置
    otel_enabled: bool = Field(default=True, description="启用OpenTelemetry追踪")
    otel_endpoint: str = Field(default="http://localhost:4317", description="OTLP端点")
    service_name: str = Field(default="biotools-agent", description="服务名称")
    service_version: str = Field(default="1.0.0", description="服务版本")
    sampling_rate: float = Field(default=1.0, description="采样率")

    # Prometheus配置
    prometheus_enabled: bool = Field(default=True, description="启用Prometheus指标")
    prometheus_port: int = Field(default=8000, description="Prometheus端口")
    metrics_path: str = Field(default="/metrics", description="指标路径")

    # Jaeger配置
    jaeger_enabled: bool = Field(default=True, description="启用Jaeger追踪")
    jaeger_endpoint: str = Field(default="http://localhost:14268/api/traces", description="Jaeger端点")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_format: str = Field(default="json", description="日志格式 (json/text)")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")

    # 告警配置
    alerts_enabled: bool = Field(default=True, description="启用告警")
    alert_webhook_url: Optional[str] = Field(default=None, description="告警Webhook URL")

    # 性能监控
    performance_monitoring: bool = Field(default=True, description="启用性能监控")
    memory_threshold_gb: float = Field(default=8.0, description="内存告警阈值(GB)")
    response_time_threshold_s: float = Field(default=30.0, description="响应时间告警阈值(秒)")
    error_rate_threshold: float = Field(default=0.1, description="错误率告警阈值")

    # 业务指标
    business_metrics: bool = Field(default=True, description="启用业务指标")
    analysis_quality_monitoring: bool = Field(default=True, description="启用分析质量监控")


class PerformanceMetrics(BaseModel):
    """性能指标模型"""

    # 响应时间指标
    end_to_end_latency: float = Field(description="端到端延迟(秒)")
    github_analysis_time: float = Field(description="GitHub分析时间(秒)")
    ai_analysis_time: float = Field(description="AI分析时间(秒)")
    report_generation_time: float = Field(description="报告生成时间(秒)")

    # 吞吐量指标
    concurrent_tasks: int = Field(description="并发任务数")
    success_rate: float = Field(description="成功率")

    # 资源使用指标
    cpu_usage_percent: float = Field(description="CPU使用率")
    memory_usage_mb: float = Field(description="内存使用量(MB)")
    disk_io_mb_s: float = Field(description="磁盘IO速率(MB/s)")
    network_io_mb_s: float = Field(description="网络IO速率(MB/s)")


class AIMetrics(BaseModel):
    """AI指标模型"""

    # Token使用指标
    input_tokens: int = Field(description="输入token数")
    output_tokens: int = Field(description="输出token数")
    total_tokens: int = Field(description="总token数")
    cost_per_request: float = Field(description="单次请求成本")

    # 模型性能指标
    response_time: float = Field(description="模型响应时间(秒)")
    success_rate: float = Field(description="模型调用成功率")
    quality_score: float = Field(description="输出质量评分")

    # 错误分析
    error_types: dict = Field(default_factory=dict, description="错误类型分布")
    retry_count: int = Field(default=0, description="重试次数")


class BioinformaticsMetrics(BaseModel):
    """生物信息学指标模型"""

    # 功能完整性
    feature_detection_rate: float = Field(description="特性检测准确率")
    dependency_identification_rate: float = Field(description="依赖识别准确率")
    api_completeness_score: float = Field(description="API接口识别完整性")

    # 架构理解
    code_structure_analysis_score: float = Field(description="代码结构分析质量")
    design_pattern_recognition_rate: float = Field(description="设计模式识别准确率")

    # 领域专业性
    terminology_coverage_rate: float = Field(description="专业术语覆盖度")
    algorithm_identification_rate: float = Field(description="算法识别准确率")
    data_type_recognition_rate: float = Field(description="数据类型识别准确率")

    # 分析质量
    overall_accuracy: float = Field(description="整体分析准确性")
    consistency_score: float = Field(description="结果一致性评分")
    expert_validation_score: float = Field(description="专家验证评分")


# 全局监控配置实例
monitoring_config = MonitoringConfig()