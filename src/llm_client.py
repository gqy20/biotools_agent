"""LLM客户端 - 参考Phase2代码实现"""

import json
import time
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .config import config_manager


class LLMClient:
    """LLM客户端，封装大模型调用"""

    def __init__(self, config_manager_instance=None):
        """初始化LLM客户端"""
        self.config_manager = config_manager_instance or config_manager
        self.config = self.config_manager.get_openai_config()
        self.model = self.config_manager.config.openai_model
        self.client = OpenAI(**self.config)

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        temperature: float = 0.1,
        timeout: int = 60,
    ) -> str:
        """
        发送聊天完成请求

        参数类似Phase2代码中的调用方式
        """
        try:
            print(f"🤖 调用LLM模型: {self.model}")
            print("📤 发送请求...")

            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                extra_body={"enable_thinking": False},  # ModelScope特定参数
            )

            elapsed = time.time() - start_time
            result = response.choices[0].message.content.strip()

            print(f"📥 收到响应，耗时: {elapsed:.2f}秒")
            print(f"📝 响应长度: {len(result)} 字符")

            return result

        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            raise e

    def sync_chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 2000,
        temperature: float = 0.1,
        timeout: int = 60,
    ) -> str:
        """
        同步版本的聊天完成请求
        """
        try:
            print(f"🤖 调用LLM模型: {self.model}")
            print("📤 发送请求...")

            start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                extra_body={"enable_thinking": False},  # ModelScope特定参数
            )

            elapsed = time.time() - start_time
            result = response.choices[0].message.content.strip()

            print(f"📥 收到响应，耗时: {elapsed:.2f}秒")
            print(f"📝 响应长度: {len(result)} 字符")

            return result

        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            raise e

    def extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """从响应中提取JSON数据，并验证数据质量"""
        try:
            # 查找JSON部分
            json_start = response.find("{")
            json_end = response.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_content = response[json_start:json_end]
                print(f"📊 提取JSON内容: {len(json_content)} 字符")

                data = json.loads(json_content)

                # 验证数据质量 - 只检查明显的垃圾内容
                if self._contains_obvious_garbage(data):
                    print("❌ 检测到明显垃圾数据，拒绝返回")
                    print(f"🔍 调试信息 - JSON内容前500字符: {json_content[:500]}")
                    return None

                return data
            else:
                print("⚠️ 响应中未找到有效JSON")
                return None

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return None

    def _contains_obvious_garbage(self, data: Dict[str, Any]) -> bool:
        """检测明显的垃圾数据 - Linus风格: 只拒绝真正的垃圾"""
        # 只检测最明显的垃圾字符串
        obvious_garbage = {
            "Unknown",
            "N/A",
            "TBD",
            "Not specified",
            "Not available",
            "未知",
            "无",
            "暂无",
            "未指定",
        }

        def is_obvious_garbage(value) -> bool:
            if isinstance(value, str):
                stripped = value.strip()
                # 空字符串
                if not stripped:
                    return True
                # 只检查最明显的垃圾
                if stripped in obvious_garbage:
                    return True
                return False
            elif isinstance(value, list):
                # 空列表不是垃圾，只检查内容
                return any(is_obvious_garbage(item) for item in value)
            elif isinstance(value, dict):
                return any(is_obvious_garbage(v) for v in value.values())
            return False

        # 只检查最关键的字段
        return is_obvious_garbage(data.get("functionality", {}).get("main_purpose", ""))
