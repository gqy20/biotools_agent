"""AI分析器，使用大模型分析项目内容"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import config_manager
from .llm_client import LLMClient
from .models import Publication, FunctionalityInfo, UsageInfo, BioToolAnalysis, CodeQualityInfo, PerformanceInfo, BioinformaticsExpertiseInfo, UsabilityInfo


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
            architecture=analysis_result.get("architecture"),
            code_quality=analysis_result.get("code_quality"),
            performance=analysis_result.get("performance"),
            bioinformatics_expertise=analysis_result.get("bioinformatics_expertise"),
            usability=analysis_result.get("usability"),
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
    
    def _build_analysis_prompt(self, readme_content: str) -> str:
        """构建分析用的prompt"""
        # 截取README内容，避免过长
        content_preview = readme_content[:8000] if len(readme_content) > 8000 else readme_content
        
        return f"""
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
    }},
    "code_quality": {{
        "code_structure": "代码结构评价",
        "documentation_quality": "文档质量评价",
        "test_coverage": "测试覆盖度评价",
        "code_style": "代码风格评价",
        "best_practices": ["最佳实践1", "最佳实践2"]
    }},
    "performance": {{
        "time_complexity": "时间复杂度描述",
        "space_complexity": "空间复杂度描述",
        "parallelization": "并行化支持描述",
        "resource_usage": "资源使用情况",
        "optimization_suggestions": ["优化建议1", "优化建议2"]
    }},
    "bioinformatics_expertise": {{
        "algorithm_accuracy": "算法准确性评价",
        "benchmark_results": "基准测试结果",
        "tool_comparison": "与其他工具比较",
        "applicable_scenarios": ["适用场景1", "适用场景2"]
    }},
    "usability": {{
        "documentation_completeness": "文档完整性评价",
        "user_interface": "用户界面评价",
        "error_handling": "错误处理机制评价",
        "learning_curve": "学习曲线评价"
    }}
}}

严格要求：
1. 仅基于README内容分析，不得编造任何信息
2. 如果README中没有明确信息，直接省略该字段，不要返回空值或"未说明"
3. publications数组：只有在README明确提到文章时才返回，否则返回空数组
4. 重点识别生物信息学格式(FASTA/BAM/VCF等)
5. 确保有效JSON格式，所有字符串值必须有实际内容
6. 禁止使用"未说明"、"未知"、"无"、"N/A"等占位符
"""

    def _call_llm_for_analysis(self, prompt: str) -> Optional[str]:
        """调用LLM进行分析"""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant specialized in bioinformatics tools analysis. Please respond in the exact JSON format requested."},
                {"role": "user", "content": prompt}
            ]
            
            return self.llm_client.sync_chat_completion(
                messages=messages,
                max_tokens=3000,
                temperature=0.1,
                timeout=60
            )
        except Exception as e:
            print(f"❌ LLM调用失败: {e}")
            return None

    def _parse_analysis_result(self, llm_response: str) -> dict:
        """解析LLM返回的分析结果"""
        data = self.llm_client.extract_json_from_response(llm_response)
        
        if not data:
            print("⚠️ 未能获取有效的分析结果，使用默认值")
            return self._get_default_analysis_data()
        
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
        
        # 解析其他组件
        functionality = self._parse_functionality(data.get("functionality", {}))
        usage = self._parse_usage(data.get("usage", {}))
        code_quality = self._parse_code_quality(data.get("code_quality", {}))
        performance = self._parse_performance(data.get("performance", {}))
        bioinformatics_expertise = self._parse_bioinformatics_expertise(data.get("bioinformatics_expertise", {}))
        usability = self._parse_usability(data.get("usability", {}))
        
        return {
            "publications": publications,
            "functionality": functionality,
            "usage": usage,
            "code_quality": code_quality,
            "performance": performance,
            "bioinformatics_expertise": bioinformatics_expertise,
            "usability": usability
        }

    def _parse_functionality(self, func_data: dict) -> FunctionalityInfo:
        """解析功能信息"""
        return FunctionalityInfo(
            main_purpose=func_data.get("main_purpose", "生物信息学分析工具"),
            key_features=func_data.get("key_features", []),
            input_formats=func_data.get("input_formats", []),
            output_formats=func_data.get("output_formats", []),
            dependencies=func_data.get("dependencies", [])
        )

    def _parse_usage(self, usage_data: dict) -> UsageInfo:
        """解析使用方法信息"""
        return UsageInfo(
            installation=usage_data.get("installation", "请参考项目README文档"),
            basic_usage=usage_data.get("basic_usage", "请查看项目文档获取使用方法"),
            examples=usage_data.get("examples", []),
            parameters=usage_data.get("parameters", [])
        )

    def _parse_code_quality(self, code_quality_data: dict) -> CodeQualityInfo:
        """解析代码质量信息"""
        return CodeQualityInfo(
            code_structure=code_quality_data.get("code_structure", "基于README分析"),
            documentation_quality=code_quality_data.get("documentation_quality", "基于README分析"),
            test_coverage=code_quality_data.get("test_coverage", "基于README分析"),
            code_style=code_quality_data.get("code_style", "基于README分析"),
            best_practices=code_quality_data.get("best_practices", [])
        )

    def _parse_performance(self, performance_data: dict) -> PerformanceInfo:
        """解析性能特征信息"""
        return PerformanceInfo(
            time_complexity=performance_data.get("time_complexity", "基于README分析"),
            space_complexity=performance_data.get("space_complexity", "基于README分析"),
            parallelization=performance_data.get("parallelization", "基于README分析"),
            resource_usage=performance_data.get("resource_usage", "基于README分析"),
            optimization_suggestions=performance_data.get("optimization_suggestions", [])
        )

    def _parse_bioinformatics_expertise(self, bioinformatics_data: dict) -> BioinformaticsExpertiseInfo:
        """解析生物信息学专业性信息"""
        return BioinformaticsExpertiseInfo(
            algorithm_accuracy=bioinformatics_data.get("algorithm_accuracy", "基于README分析"),
            benchmark_results=bioinformatics_data.get("benchmark_results", "基于README分析"),
            tool_comparison=bioinformatics_data.get("tool_comparison", "基于README分析"),
            applicable_scenarios=bioinformatics_data.get("applicable_scenarios", [])
        )

    def _parse_usability(self, usability_data: dict) -> UsabilityInfo:
        """解析可用性信息"""
        return UsabilityInfo(
            documentation_completeness=usability_data.get("documentation_completeness", "基于README分析"),
            user_interface=usability_data.get("user_interface", "基于README分析"),
            error_handling=usability_data.get("error_handling", "基于README分析"),
            learning_curve=usability_data.get("learning_curve", "基于README分析")
        )

    def _get_default_analysis_data(self) -> dict:
        """获取默认分析数据"""
        return {
            "publications": [],
            "functionality": FunctionalityInfo(
                main_purpose="生物信息学分析工具",
                key_features=[],
                input_formats=[],
                output_formats=[],
                dependencies=[]
            ),
            "usage": UsageInfo(
                installation="请参考项目README文档",
                basic_usage="请查看项目文档获取使用方法",
                examples=[],
                parameters=[]
            ),
            "code_quality": None,
            "performance": None,
            "bioinformatics_expertise": None,
            "usability": None
        }

    def _analyze_all_in_one(self, readme_content: str) -> dict:
        """重构后的分析函数 - 单一职责原则"""
        # 1. 构建prompt
        prompt = self._build_analysis_prompt(readme_content)
        
        # 2. 调用LLM
        llm_response = self._call_llm_for_analysis(prompt)
        if not llm_response:
            return self._get_default_analysis_data()
        
        # 3. 解析结果
        return self._parse_analysis_result(llm_response)
    
    def _create_default_analysis(self, repo_info, authors) -> BioToolAnalysis:
        """创建默认分析结果"""
        default_data = self._get_default_analysis_data()
        
        return BioToolAnalysis(
            repository=repo_info,
            authors=authors,
            publications=default_data["publications"],
            functionality=default_data["functionality"],
            usage=default_data["usage"],
            code_quality=default_data["code_quality"],
            performance=default_data["performance"],
            bioinformatics_expertise=default_data["bioinformatics_expertise"],
            usability=default_data["usability"],
            analysis_timestamp=datetime.now().isoformat()
        )
    
    def _get_default_analysis_data(self) -> dict:
        """获取默认分析数据"""
        return {
            "publications": [],
            "functionality": FunctionalityInfo(
                main_purpose="生物信息学分析工具",
                key_features=[],
                input_formats=[],
                output_formats=[],
                dependencies=[]
            ),
            "usage": UsageInfo(
                installation="请参考项目README文档",
                basic_usage="请查看项目文档获取使用方法",
                examples=[],
                parameters=[]
            ),
            "code_quality": None,
            "performance": None,
            "bioinformatics_expertise": None,
            "usability": None
        }
    

