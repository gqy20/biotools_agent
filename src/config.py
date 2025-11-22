"""配置管理模块"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field


class ClaudeSDKConfig(BaseModel):
    """Claude Code SDK 配置模型"""

    # Claude API配置
    claude_api_key: Optional[str] = Field(default=None, description="Claude API密钥")
    claude_base_url: str = Field(
        default="https://api.anthropic.com", description="Claude API基础URL"
    )
    claude_model: str = Field(default="claude-3-5-sonnet-20241022", description="使用的Claude模型")
    max_turns: int = Field(default=10, description="最大对话轮数")
    timeout: int = Field(default=180, description="超时时间(秒)")
    enable_cache: bool = Field(default=True, description="启用缓存")
    permission_mode: str = Field(default="acceptEdits", description="权限模式")

    # 代理配置
    use_file_agents: bool = Field(default=True, description="使用文件系统代理")
    fallback_to_programmatic: bool = Field(default=True, description="回退到程序化代理")


class LegacyAIConfig(BaseModel):
    """传统AI配置模型（向后兼容）"""

    # OpenAI/模型配置
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API密钥")
    openai_base_url: str = Field(
        default="https://api.openai.com/v1", description="OpenAI API基础URL"
    )
    openai_model: str = Field(default="gpt-3.5-turbo", description="使用的模型名称")


class AppConfig(BaseModel):
    """应用配置模型"""

    # Claude SDK配置（推荐）
    claude_sdk: ClaudeSDKConfig = Field(default_factory=ClaudeSDKConfig)

    # 传统AI配置（向后兼容）
    legacy_ai: LegacyAIConfig = Field(default_factory=LegacyAIConfig)

    # GitHub配置
    hub_token: Optional[str] = Field(default=None, description="GitHub访问令牌")

    # Supabase配置
    supabase_url: Optional[str] = Field(default=None, description="Supabase项目URL")
    supabase_key: Optional[str] = Field(
        default=None, description="Supabase服务角色密钥"
    )

    # 应用配置
    tmp_dir: str = Field(default="tmp", description="临时文件目录")
    output_dir: str = Field(default="docs", description="输出目录")
    max_file_size: int = Field(default=10000, description="最大文件大小(字节)")
    max_content_length: int = Field(default=10000, description="最大内容长度(字符)")

    class Config:
        env_prefix = ""  # 不使用前缀，直接使用环境变量名


class ConfigManager:
    """配置管理器"""

    def __init__(self, env_file: Optional[str] = None):
        self.config = self._load_config(env_file)

    def _load_config(self, env_file: Optional[str] = None) -> AppConfig:
        """加载配置"""

        # 1. 加载.env文件
        if env_file:
            load_dotenv(env_file)
        else:
            # 尝试在当前目录和项目根目录查找.env文件
            possible_env_files = [
                Path(".env"),
                Path("../.env"),
                Path("../../.env"),
            ]

            for env_path in possible_env_files:
                if env_path.exists():
                    load_dotenv(env_path)
                    break

        # 2. 从环境变量创建配置
        config_data = {
            "claude_sdk": {
                "claude_api_key": os.getenv("CLAUDE_API_KEY"),
                "claude_base_url": os.getenv(
                    "CLAUDE_BASE_URL", "https://api.anthropic.com"
                ),
                "claude_model": os.getenv("CLAUDE_MODEL", "claude-3-5-sonnet-20241022"),
                "max_turns": int(os.getenv("CLAUDE_MAX_TURNS", "10")),
                "timeout": int(os.getenv("CLAUDE_TIMEOUT", "180")),
                "enable_cache": os.getenv("CLAUDE_ENABLE_CACHE", "true").lower() == "true",
                "permission_mode": os.getenv("CLAUDE_PERMISSION_MODE", "acceptEdits"),
                "use_file_agents": os.getenv("USE_FILE_AGENTS", "true").lower() == "true",
                "fallback_to_programmatic": os.getenv("FALLBACK_TO_PROGRAMMATIC", "true").lower() == "true",
            },
            "legacy_ai": {
                "openai_api_key": os.getenv("OPENAI_API_KEY"),
                "openai_base_url": os.getenv(
                    "OPENAI_BASE_URL", "https://api.openai.com/v1"
                ),
                "openai_model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            },
            "hub_token": os.getenv("HUB_TOKEN"),
            "supabase_url": os.getenv("SUPABASE_URL"),
            "supabase_key": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),  # 使用服务角色密钥
            "tmp_dir": os.getenv("TMP_DIR", "tmp"),
            "output_dir": os.getenv("OUTPUT_DIR", "docs"),
            "max_file_size": int(os.getenv("MAX_FILE_SIZE", "10000")),
            "max_content_length": int(os.getenv("MAX_CONTENT_LENGTH", "10000")),
        }

        return AppConfig(**config_data)

    def get_openai_config(self) -> dict:
        """获取OpenAI配置字典"""
        config = {
            "api_key": self.config.openai_api_key,
        }

        # 如果不是默认的OpenAI URL，则添加base_url
        if self.config.openai_base_url != "https://api.openai.com/v1":
            config["base_url"] = self.config.openai_base_url

        return config

    def get_github_headers(self) -> dict:
        """获取GitHub API请求头"""
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "BioTools-Agent/1.0",
        }

        if self.config.hub_token:
            headers["Authorization"] = f"token {self.config.hub_token}"

        return headers

    def validate_config(self) -> tuple[bool, list[str]]:
        """验证配置是否完整"""
        errors = []

        # 检查Claude SDK配置（推荐）
        if not self.config.claude_sdk.claude_api_key:
            errors.append("缺少CLAUDE_API_KEY配置（推荐使用代理模式）")

        # 如果没有Claude配置，检查传统AI配置
        if not self.config.claude_sdk.claude_api_key and not self.config.legacy_ai.openai_api_key:
            errors.append("缺少AI配置：请设置CLAUDE_API_KEY或OPENAI_API_KEY")

        return len(errors) == 0, errors


# 全局配置实例
config_manager = ConfigManager()
