"""LLM客户端 - 参考Phase2代码实现"""

import json
import time
from typing import List, Dict, Any, Optional

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
        timeout: int = 60
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
                extra_body={"enable_thinking": False}  # ModelScope特定参数
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
        timeout: int = 60
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
                extra_body={"enable_thinking": False}  # ModelScope特定参数
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
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_content = response[json_start:json_end]
                print(f"📊 提取JSON内容: {len(json_content)} 字符")
                
                data = json.loads(json_content)
                
                # 验证数据质量
                if self._contains_garbage_data(data):
                    print("❌ 检测到垃圾数据，拒绝返回")
                    return None
                
                return data
            else:
                print("⚠️ 响应中未找到有效JSON")
                return None
                
        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return None
    
    def _contains_garbage_data(self, data: Dict[str, Any]) -> bool:
        """检测垃圾数据 - Linus风格: 严格标准"""
        # 明确的垃圾字符串列表
        garbage_strings = {
            # 中文垃圾
            "未说明", "未知", "无", "未定义", "暂无", "未明确列出", "未指定",
            # 英文垃圾  
            "Unknown", "N/A", "TBD", "Not specified", "Not mentioned", "Not available",
            # 模板占位符
            "文章标题", "作者", "期刊", "DOI", "主要用途一句话", "功能1", "功能2", "功能3",
            "输入格式", "输出格式", "代码结构评价", "文档质量评价", "时间复杂度描述",
            "并行化支持描述", "算法准确性评价", "适用场景1", "适用场景2", "文档完整性评价",
            "学习曲线评价", "基于README分析", "参考README"
        }
        
        def is_garbage(value) -> bool:
            if isinstance(value, str):
                stripped = value.strip()
                # 空字符串或仅空白符
                if not stripped:
                    return True
                # 明确的垃圾字符串
                if stripped in garbage_strings:
                    return True
                # 包含垃圾模式的字符串
                if any(garbage in stripped for garbage in ["未明确", "请参考", "基于README"]):
                    return True
                return False
            elif isinstance(value, list):
                return any(is_garbage(item) for item in value)
            elif isinstance(value, dict):
                return any(is_garbage(v) for v in value.values())
            return False
        
        # 特别检查publications中的垃圾作者信息
        publications = data.get("publications", [])
        for pub in publications:
            if isinstance(pub, dict):
                authors = pub.get("authors", [])
                if authors and any(is_garbage(author) for author in authors):
                    print(f"❌ 检测到垃圾作者信息: {authors}")
                    return True
        
        # 递归检查所有数据
        if is_garbage(data):
            return True
            
        return False
