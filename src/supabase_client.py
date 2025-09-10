"""Supabase数据库客户端"""

import uuid
from typing import Optional

from supabase import Client, create_client

from .config import config_manager
from .models import BioToolAnalysis


class SupabaseManager:
    """Supabase 数据库管理器"""

    def __init__(self):
        self.url = config_manager.config.supabase_url
        self.key = config_manager.config.supabase_key
        self.client: Optional[Client] = None

        if self.url and self.key:
            try:
                self.client = create_client(self.url, self.key)
                print("✅ Supabase 客户端初始化成功")
            except Exception as e:
                print(f"⚠️ Supabase 客户端初始化失败: {e}")
                self.client = None
        else:
            print("⚠️ Supabase 配置缺失 (SUPABASE_URL 或 SUPABASE_KEY 未设置)")

    def is_configured(self) -> bool:
        """检查 Supabase 是否已正确配置"""
        return self.client is not None

    def save_analysis_result(self, analysis: BioToolAnalysis) -> bool:
        """将分析结果保存到 Supabase 数据库"""
        if not self.is_configured():
            print("❌ Supabase 未配置，无法保存分析结果")
            return False

        try:
            # 将 Pydantic 模型转换为字典
            # 注意：需要将 HttpUrl 转换为字符串
            data_dict = analysis.model_dump()
            if "repository" in data_dict and "url" in data_dict["repository"]:
                data_dict["repository"]["url"] = str(data_dict["repository"]["url"])

            # 为每次测试生成唯一的test_id
            test_id = str(uuid.uuid4())

            # 准备插入的数据
            repo_url = str(analysis.repository.url)
            insert_data = {"test_id": test_id, "repo_url": repo_url, "data": data_dict}

            # 使用 insert 操作，确保每次测试都创建新记录
            response = (
                self.client.table("bio_analysis_results").insert(insert_data).execute()
            )

            if response.data:
                print(f"✅ 分析结果已保存到数据库: {repo_url} (测试ID: {test_id})")
                return True
            else:
                print(
                    f"⚠️ 保存分析结果时未返回数据: "
                    f"{response.error.message if response.error else '未知错误'}"
                )
                return False

        except Exception as e:
            print(f"❌ 保存分析结果到数据库时发生异常: {e}")
            return False


# 全局实例
supabase_manager = SupabaseManager()
