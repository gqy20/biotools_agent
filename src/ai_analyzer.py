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
        analysis_result = self._analyze_all_in_one(readme_content, repo_path)
        
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
    
    def _collect_core_code_samples(self, repo_path: Path) -> str:
        """收集核心代码样本 - Linus风格：找到算法核心"""
        print("🔍 收集核心代码样本...")
        
        # 核心文件模式 - 生物信息学工具常见的核心文件
        core_patterns = [
            "main.py", "main.cpp", "main.c", "main.java",
            "*algorithm*", "*core*", "*engine*", 
            "*align*", "*search*", "*index*", "*parse*",
            "*.py", "*.cpp", "*.c", "*.java", "*.R"
        ]
        
        code_samples = []
        file_count = 0
        max_files = 5  # 限制文件数量
        max_content = 2000  # 每个文件最大内容长度
        
        for pattern in core_patterns:
            if file_count >= max_files:
                break
                
            # 查找匹配的文件
            try:
                for file_path in repo_path.rglob(pattern):
                    if file_count >= max_files:
                        break
                        
                    # 跳过不相关目录
                    if any(skip in str(file_path) for skip in ['.git', '__pycache__', 'test', 'doc', 'example']):
                        continue
                        
                    if file_path.is_file() and file_path.stat().st_size < 50000:  # 小于50KB
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()[:max_content]
                                if content.strip():
                                    relative_path = file_path.relative_to(repo_path)
                                    code_samples.append(f"=== {relative_path} ===\n{content}\n")
                                    file_count += 1
                                    print(f"📄 收集代码文件: {relative_path}")
                        except Exception:
                            continue
            except Exception:
                continue
        
        result = "\n".join(code_samples)
        print(f"✅ 收集了 {file_count} 个核心代码文件，总长度: {len(result)} 字符")
        return result
    
    def _build_analysis_prompt(self, readme_content: str, code_content: str = "") -> str:
        """构建分析用的prompt - Linus风格：消除特殊情况"""
        # 截取README内容，避免过长
        content_preview = readme_content[:6000] if len(readme_content) > 6000 else readme_content
        code_preview = code_content[:4000] if len(code_content) > 4000 else code_content
        
        prompt = f"""分析这个生物信息学工具的README文档"""
        
        if code_content:
            prompt += "和核心代码"
            
        prompt += f"""，提取其中的事实信息。所有回答必须使用中文。

README内容：
{content_preview}"""

        if code_content:
            prompt += f"""

核心代码片段：
{code_preview}"""

        prompt += """

返回JSON格式，仅包含明确提到或可以从代码中分析出的信息：

{
    "publications": [
        // 仅当README明确提到论文标题时才包含
        {"title": "README中的确切标题", "journal": "如果提到期刊名", "year": 年份数字, "doi": "如果有DOI"}
    ],
    "functionality": {
        "main_purpose": "用一句中文描述此工具的用途",
        "key_features": ["功能特点1", "功能特点2"],  // 仅README明确提到的功能
        "input_formats": ["FASTA", "BAM"],  // 仅明确提到的输入格式
        "output_formats": ["GFF", "VCF"],   // 仅明确提到的输出格式
        "dependencies": ["Python", "BWA"]   // 仅明确提到的依赖
    },
    "usage": {
        "installation": "README中的确切安装命令",
        "basic_usage": "基本使用命令",
        "examples": ["示例1", "示例2"]
    },
    "performance": {
        "algorithm_complexity": "基于代码分析的算法复杂度",
        "resource_requirements": "资源需求分析", 
        "optimization_features": "发现的优化特性"
    }
}

严格要求：
1. 所有文本必须使用中文表达
2. 仅提取README中明确写明的信息
3. 如果提供了代码，结合代码进行算法复杂度分析
4. 如果信息缺失，直接省略该字段
5. 绝不使用占位符或模板文本
6. 返回简洁、事实性的中文JSON"""

        return prompt

    def _call_llm_for_analysis(self, prompt: str) -> Optional[str]:
        """调用LLM进行分析"""
        try:
            messages = [
                {"role": "system", "content": "你是专门分析生物信息学工具的助手。请严格按照要求的JSON格式回答，所有内容必须使用中文表达。"},
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
        """解析LLM返回的分析结果 - Linus风格: 消除复杂度"""
        data = self.llm_client.extract_json_from_response(llm_response)
        
        if not data:
            print("⚠️ 未能获取有效的分析结果，使用最小默认值")
            return self._get_minimal_defaults()
        
        # 简单直接的解析 - 不要过度处理
        publications = [
            Publication(
                title=pub.get("title", ""),
                authors=pub.get("authors", []),
                journal=pub.get("journal"),
                year=pub.get("year"),
                doi=pub.get("doi")
            )
            for pub in data.get("publications", [])
            if pub.get("title")  # 只有title存在才创建
        ]
        
        # 功能信息 - 简单获取，没有复杂的默认值处理
        func_data = data.get("functionality", {})
        functionality = FunctionalityInfo(
            main_purpose=func_data.get("main_purpose", "生物信息学工具"),
            key_features=func_data.get("key_features", []),
            input_formats=func_data.get("input_formats", []),
            output_formats=func_data.get("output_formats", []),
            dependencies=func_data.get("dependencies", [])
        )
        
        # 使用信息 - 最简实现
        usage_data = data.get("usage", {})
        usage = UsageInfo(
            installation=usage_data.get("installation", "参考README"),
            basic_usage=usage_data.get("basic_usage", "参考README"),
            examples=usage_data.get("examples", []),
            parameters=usage_data.get("parameters", [])
        )
        
        # 性能信息 - 基于代码和README的综合分析
        performance_data = data.get("performance", {})
        performance = None
        if performance_data:
            # 安全地处理可能是数组的字段
            def safe_get_string(data_dict, key, default=""):
                value = data_dict.get(key, default)
                if isinstance(value, list):
                    return " ".join(str(v) for v in value) if value else default
                return str(value) if value else default
            
            performance = PerformanceInfo(
                time_complexity=safe_get_string(performance_data, "algorithm_complexity"),
                space_complexity=safe_get_string(performance_data, "resource_requirements"),
                parallelization=safe_get_string(performance_data, "optimization_features"),
                resource_usage=safe_get_string(performance_data, "resource_requirements"),
                optimization_suggestions=[]
            )
        
        return {
            "publications": publications,
            "functionality": functionality,
            "usage": usage,
            "performance": performance,  # 现在包含真实的性能分析
            "code_quality": None,  # 砍掉不必要的复杂性
            "bioinformatics_expertise": None,
            "usability": None
        }

    def _get_minimal_defaults(self) -> dict:
        """获取最小默认数据 - Linus风格: 简单直接"""
        return {
            "publications": [],
            "functionality": FunctionalityInfo(
                main_purpose="生物信息学工具",
                key_features=[],
                input_formats=[],
                output_formats=[],
                dependencies=[]
            ),
            "usage": UsageInfo(
                installation="参考README",
                basic_usage="参考README", 
                examples=[],
                parameters=[]
            ),
            "code_quality": None,
            "performance": None,
            "bioinformatics_expertise": None,
            "usability": None
        }

    def _create_default_analysis(self, repo_info, authors) -> BioToolAnalysis:
        """创建默认分析结果"""
        defaults = self._get_minimal_defaults()
        
        return BioToolAnalysis(
            repository=repo_info,
            authors=authors,
            publications=defaults["publications"],
            functionality=defaults["functionality"],
            usage=defaults["usage"],
            analysis_timestamp=datetime.now().isoformat()
        )

    def _analyze_all_in_one(self, readme_content: str, repo_path: Path) -> dict:
        """一次性分析 - Linus风格：简单高效"""
        # 1. 收集代码样本用于深度分析
        code_content = self._collect_core_code_samples(repo_path)
        
        # 2. 构建包含代码的prompt
        prompt = self._build_analysis_prompt(readme_content, code_content)
        
        # 3. 调用LLM
        llm_response = self._call_llm_for_analysis(prompt)
        if not llm_response:
            return self._get_minimal_defaults()
        
        # 4. 解析结果
        return self._parse_analysis_result(llm_response)

