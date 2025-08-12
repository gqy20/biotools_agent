"""AI分析器，使用大模型分析项目内容"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from .config import config_manager
from .llm_client import LLMClient
from .models import Publication, FunctionalityInfo, UsageInfo, BioToolAnalysis


class AIAnalyzer:
    """AI分析器"""
    
    def __init__(self, config_override: dict = None):
        # 初始化LLM客户端
        self.llm_client = LLMClient(config_manager)
        print("✅ AI分析器初始化完成")
    
    def analyze_repository_content(self, repo_path: Path, repo_info, authors) -> BioToolAnalysis:
        """使用AI分析仓库内容"""
        
        print("🚀 开始AI全面分析仓库内容...")
        print(f"📂 分析仓库路径: {repo_path}")
        
        # 收集README文档内容
        print("📁 收集README文档内容...")
        readme_content = self._collect_readme_content(repo_path)
        
        if not readme_content:
            print("⚠️ 未找到README文档，使用默认信息")
            return self._create_default_analysis(repo_info, authors)
        
        print(f"✅ README内容长度: {len(readme_content)} 字符")
        
        # 一次性AI分析获取所有信息
        print("🤖 一次性AI分析获取所有信息...")
        analysis_result = self._analyze_all_in_one(readme_content)
        
        # 组装完整分析结果
        print("📋 组装完整分析结果...")
        analysis = BioToolAnalysis(
            repository=repo_info,
            authors=authors,
            publications=analysis_result["publications"],
            functionality=analysis_result["functionality"],
            usage=analysis_result["usage"],
            analysis_timestamp=datetime.now().isoformat()
        )
        
        print("🎉 AI分析完成!")
        print(f"  - 发表文章: {len(analysis_result['publications'])} 篇")
        print(f"  - 主要功能: {analysis_result['functionality'].main_purpose}")
        print(f"  - 核心特性: {len(analysis_result['functionality'].key_features)} 个")
        
        return analysis
    
    def _collect_readme_content(self, repo_path: Path) -> str:
        """收集README文档内容"""
        
        # README文件的可能命名
        readme_files = [
            "README.md", "README.rst", "README.txt", "README",
            "readme.md", "readme.rst", "readme.txt", "readme",
            "Readme.md", "Readme.rst", "Readme.txt", "Readme"
        ]
        
        for readme_file in readme_files:
            file_path = repo_path / readme_file
            if file_path.exists() and file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"📄 找到README文件: {readme_file}")
                        # 限制内容长度，避免过长
                        return content[:150000] if len(content) > 150000 else content
                except Exception:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                            print(f"📄 找到README文件: {readme_file} (latin-1编码)")
                            return content[:150000] if len(content) > 150000 else content
                    except Exception:
                        continue
        
        print("⚠️ 未找到README文件")
        return ""
    
    def _analyze_all_in_one(self, readme_content: str) -> dict:
        """一次性分析所有信息"""
        
        # 截取README内容，避免过长
        content_preview = readme_content[:8000] if len(readme_content) > 8000 else readme_content
        
        prompt = f"""
分析生物信息学工具README，返回JSON格式信息：

README内容：
{content_preview}

返回JSON格式：
{{
    "publications": [
        {{"title": "文章标题", "authors": ["作者"], "journal": "期刊", "year": 年份, "doi": "DOI"}}
    ],
    "functionality": {{
        "main_purpose": "主要用途一句话",
        "key_features": ["功能1", "功能2", "功能3"],
        "input_formats": ["输入格式"],
        "output_formats": ["输出格式"],
        "dependencies": ["依赖项"]
    }},
    "usage": {{
        "installation": "安装方法",
        "basic_usage": "基本用法",
        "examples": ["示例1", "示例2"],
        "parameters": ["参数说明"]
    }}
}}

要求：
1. 仅基于README内容分析
2. 缺失信息用空数组[]或"未说明"
3. 重点识别生物信息学格式(FASTA/BAM/VCF等)
4. 确保有效JSON格式
"""
        
        try:
            # 使用新的LLM客户端
            messages = [
                {"role": "system", "content": "You are a helpful assistant specialized in bioinformatics tools analysis. Please respond in the exact JSON format requested."},
                {"role": "user", "content": prompt}
            ]
            
            result = self.llm_client.sync_chat_completion(
                messages=messages,
                max_tokens=2000,
                temperature=0.1,
                timeout=60
            )
            
            # 使用LLM客户端的JSON提取方法
            data = self.llm_client.extract_json_from_response(result)
            
            if data:
                # 解析publications
                publications = []
                for pub_data in data.get("publications", []):
                    pub = Publication(
                        title=pub_data.get("title", ""),
                        authors=pub_data.get("authors", []),
                        journal=pub_data.get("journal"),
                        year=pub_data.get("year"),
                        doi=pub_data.get("doi"),
                        pmid=pub_data.get("pmid")
                    )
                    publications.append(pub)
                
                # 解析functionality
                func_data = data.get("functionality", {})
                functionality = FunctionalityInfo(
                    main_purpose=func_data.get("main_purpose", "生物信息学分析工具"),
                    key_features=func_data.get("key_features", []),
                    input_formats=func_data.get("input_formats", []),
                    output_formats=func_data.get("output_formats", []),
                    dependencies=func_data.get("dependencies", [])
                )
                
                # 解析usage
                usage_data = data.get("usage", {})
                usage = UsageInfo(
                    installation=usage_data.get("installation", "请参考项目README文档"),
                    basic_usage=usage_data.get("basic_usage", "请查看项目文档获取使用方法"),
                    examples=usage_data.get("examples", []),
                    parameters=usage_data.get("parameters", [])
                )
                
                print(f"✅ 成功解析所有信息")
                print(f"  - 发表文章: {len(publications)} 篇")
                print(f"  - 功能特性: {len(functionality.key_features)} 个")
                print(f"  - 使用示例: {len(usage.examples)} 个")
                
                return {
                    "publications": publications,
                    "functionality": functionality,
                    "usage": usage
                }
            
        except Exception as e:
            print(f"⚠️ AI综合分析失败: {e}")
            print("将使用默认信息...")
        
        # 返回默认值
        return self._get_default_analysis_data()
    
    def _create_default_analysis(self, repo_info, authors) -> BioToolAnalysis:
        """创建默认分析结果"""
        default_data = self._get_default_analysis_data()
        
        return BioToolAnalysis(
            repository=repo_info,
            authors=authors,
            publications=default_data["publications"],
            functionality=default_data["functionality"],
            usage=default_data["usage"],
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _get_default_analysis_data(self) -> dict:
        """获取默认分析数据"""
        return {
            "publications": [],
            "functionality": FunctionalityInfo(
                main_purpose="生物信息学分析工具",
                key_features=["数据处理", "结果分析"],
                input_formats=["未在文档中说明"],
                output_formats=["未在文档中说明"],
                dependencies=["未在文档中说明"]
            ),
            "usage": UsageInfo(
                installation="请参考项目README文档",
                basic_usage="请查看项目文档获取使用方法",
                examples=["请参考项目示例"],
                parameters=["请查看帮助文档"]
            )
        }
    

