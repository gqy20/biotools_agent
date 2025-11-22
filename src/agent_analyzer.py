"""基于Claude Code SDK的代理分析器

使用多个专业代理进行生物信息学工具的深度分析
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

from .config import config_manager
from .models import (
    BioToolAnalysis,
    DataRequirements,
    DeploymentInfo,
    FunctionalityInfo,
    PerformanceInfo,
    Publication,
    TestingInfo,
    UsageInfo,
    ProjectArchitecture,
    CodeQualityInfo,
    SecurityAnalysis,
)
from .agent_definitions import PROJECT_AGENTS, ANALYSIS_TASKS


class AgentAIAnalyzer:
    """基于Claude Code SDK的AI分析器"""

    def __init__(self, config_override: dict = None):
        """初始化代理分析器"""
        self.config = config_override or config_manager.config
        self.use_file_agents = getattr(self.config, 'use_file_agents', True)
        self.fallback_to_programmatic = getattr(self.config, 'fallback_to_programmatic', True)

        self.options = self._create_agent_options()
        print("✅ Claude Code SDK代理分析器初始化完成")

    def _create_agent_options(self, repo_path: Optional[Path] = None) -> ClaudeAgentOptions:
        """创建代理配置选项"""
        # 正确访问嵌套配置
        claude_config = getattr(self.config, 'claude_sdk', self.config)

        # 基础配置
        options = ClaudeAgentOptions(
            # 允许使用的工具
            allowed_tools=[
                "Read", "Write", "Edit", "Glob", "Grep",
                "Bash", "WebSearch", "WebFetch"
            ],

            # 优先使用程序化定义（现在PROJECT_AGENTS已经是AgentDef实例）
            agents=PROJECT_AGENTS if self.fallback_to_programmatic else None,

            # 模型配置
            model=getattr(claude_config, 'claude_model', 'sonnet'),
            max_turns=getattr(claude_config, 'max_turns', 10),

            # 权限配置
            permission_mode=getattr(claude_config, 'permission_mode', 'acceptEdits'),

            # 工作目录设置（如果提供）
            cwd=str(repo_path) if repo_path else None,
        )

        return options

    async def analyze_repository_content(
        self, repo_path: Path, repo_info, authors
    ) -> BioToolAnalysis:
        """使用代理分析仓库内容"""

        print("🚀 开始Claude代理深度分析仓库内容...")
        print(f"📂 分析仓库路径: {repo_path}")
        print(f"🤖 使用 {len(PROJECT_AGENTS)} 个专业代理进行分析")

        try:
            # 创建包含工作目录的options
            options_with_cwd = self._create_agent_options(repo_path)

            async with ClaudeSDKClient(options=options_with_cwd) as client:
                # 构建分析任务
                analysis_result = await self._execute_parallel_analysis(
                    client, repo_info, authors
                )

                # 转换为BioToolAnalysis对象
                return self._convert_to_biotools_analysis(
                    analysis_result, repo_info, authors
                )

        except Exception as e:
            print(f"❌ Claude代理分析失败: {e}")
            print("🔄 降级到基础分析...")
            return self._create_fallback_analysis(repo_info, authors)

    async def _execute_parallel_analysis(
        self, client: ClaudeSDKClient, repo_info, authors
    ) -> Dict[str, Any]:
        """执行并行分析任务"""

        # 构建项目信息摘要
        author_names = [author.name for author in authors]
        project_info = f"""
## 项目基础信息
- 项目名称: {repo_info.name}
- 项目URL: {repo_info.url}
- 主要语言: {repo_info.language}
- Star数量: {repo_info.stars}
- Fork数量: {repo_info.forks}
- 许可证: {repo_info.license}
- 项目描述: {repo_info.description}

## 作者信息
- 主要作者: {', '.join(author_names)}

请基于这些信息和实际代码进行深度分析。
"""

        analysis_results = {}

        # 并行执行多个分析任务
        tasks = []
        for task_config in ANALYSIS_TASKS:
            task_prompt = f"""
            请使用{task_config['agent']}代理执行以下任务：

            {task_config['description']}

            {project_info}

            请重点关注以下方面：
            {', '.join(task_config['focus'])}

            请提供详细的结构化分析结果，使用JSON格式输出。
            """

            task = self._execute_single_task(
                client, task_config['agent'], task_prompt
            )
            tasks.append(task)

        # 等待所有任务完成
        try:
            task_results = await asyncio.gather(*tasks, return_exceptions=True)

            # 处理结果
            for i, result in enumerate(task_results):
                if isinstance(result, Exception):
                    print(f"⚠️ 任务 {ANALYSIS_TASKS[i]['agent']} 失败: {result}")
                    # 使用空结果继续
                    analysis_results[ANALYSIS_TASKS[i]['agent']] = {}
                else:
                    analysis_results[ANALYSIS_TASKS[i]['agent']] = result

        except Exception as e:
            print(f"❌ 并行任务执行失败: {e}")
            # 尝试串行执行作为备选
            return await self._execute_sequential_analysis(client, repo_info, authors)

        return analysis_results

    async def _execute_single_task(
        self, client: ClaudeSDKClient, agent_name: str, prompt: str
    ) -> Dict[str, Any]:
        """执行单个分析任务"""

        task_prompt = f"""
        请使用{agent_name}代理进行分析。

        {prompt}

        请严格按照JSON格式输出分析结果，确保结果可以被Python解析。
        如果某个字段没有相关信息，请省略该字段或使用空数组/空字符串。
        """

        result_data = {}

        try:
            # 修复：直接 await 调用，而不是 async for
            result = await client.query(task_prompt)

            # 处理返回结果
            if hasattr(result, 'content'):
                content = result.content

                # 尝试解析JSON结果
                if isinstance(content, str):
                    try:
                        # 提取JSON部分
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1

                        if json_start >= 0 and json_end > json_start:
                            json_content = content[json_start:json_end]
                            parsed_data = json.loads(json_content)
                            result_data.update(parsed_data)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON解析失败: {e}")

            # 检查其他可能的属性
            elif hasattr(result, 'text'):
                content = result.text
                if isinstance(content, str):
                    try:
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_content = content[json_start:json_end]
                            parsed_data = json.loads(json_content)
                            result_data.update(parsed_data)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON解析失败: {e}")

            elif hasattr(result, 'response'):
                content = result.response
                if isinstance(content, str):
                    try:
                        json_start = content.find('{')
                        json_end = content.rfind('}') + 1
                        if json_start >= 0 and json_end > json_start:
                            json_content = content[json_start:json_end]
                            parsed_data = json.loads(json_content)
                            result_data.update(parsed_data)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON解析失败: {e}")

        except Exception as e:
            print(f"❌ 任务执行异常: {e}")

        return result_data

    async def _execute_sequential_analysis(
        self, client: ClaudeSDKClient, repo_info, authors
    ) -> Dict[str, Any]:
        """串行执行分析任务（备选方案）"""

        print("🔄 使用串行模式执行分析任务...")
        analysis_results = {}

        for task_config in ANALYSIS_TASKS:
            try:
                print(f"📊 执行任务: {task_config['description']}")

                task_prompt = f"""
                请分析这个生物信息学工具项目：{repo_info.name}

                {task_config['description']}

                请提供结构化的JSON格式分析结果。
                """

                result = await self._execute_single_task(
                    client, task_config['agent'], task_prompt
                )
                analysis_results[task_config['agent']] = result

            except Exception as e:
                print(f"❌ 任务 {task_config['agent']} 失败: {e}")
                analysis_results[task_config['agent']] = {}

        return analysis_results

    def _convert_to_biotools_analysis(
        self, agent_results: Dict[str, Any], repo_info, authors
    ) -> BioToolAnalysis:
        """将代理结果转换为BioToolAnalysis对象"""

        # 合并所有代理结果
        merged_result = {}
        for agent_name, result in agent_results.items():
            if result:
                merged_result.update(result)

        # 解析功能信息
        func_data = merged_result.get('functionality', {})
        functionality = FunctionalityInfo(
            main_purpose=func_data.get('main_purpose', '生物信息学工具'),
            key_features=func_data.get('key_features', []),
            input_formats=func_data.get('input_formats', []),
            output_formats=func_data.get('output_formats', []),
            dependencies=func_data.get('dependencies', [])
        )

        # 解析使用信息
        usage_data = merged_result.get('usage', {})
        usage = UsageInfo(
            installation=usage_data.get('installation', '参考项目文档'),
            basic_usage=usage_data.get('basic_usage', '参考项目文档'),
            examples=usage_data.get('examples', []),
            parameters=usage_data.get('parameters', [])
        )

        # 解析性能信息
        perf_data = merged_result.get('performance', {})
        performance = PerformanceInfo(
            time_complexity=perf_data.get('time_complexity', ''),
            space_complexity=perf_data.get('space_complexity', ''),
            parallelization=perf_data.get('parallelization', ''),
            resource_usage=perf_data.get('resource_usage', ''),
            optimization_suggestions=perf_data.get('optimization_suggestions', [])
        )

        # 解析部署信息
        deploy_data = merged_result.get('deployment', {})
        deployment = DeploymentInfo(
            installation_methods=deploy_data.get('installation_methods', []),
            system_requirements=deploy_data.get('system_requirements', []),
            container_support=deploy_data.get('container_support', []),
            cloud_deployment=deploy_data.get('cloud_deployment', []),
            configuration_files=deploy_data.get('configuration_files', [])
        )

        # 解析测试信息
        test_data = merged_result.get('testing', {})
        testing = TestingInfo(
            test_commands=test_data.get('test_commands', []),
            test_data_sources=test_data.get('test_data_sources', []),
            example_datasets=test_data.get('example_datasets', []),
            validation_methods=test_data.get('validation_methods', []),
            benchmark_datasets=test_data.get('benchmark_datasets', [])
        )

        # 解析数据需求
        data_data = merged_result.get('data_requirements', {})
        data_requirements = DataRequirements(
            required_inputs=data_data.get('required_inputs', []),
            optional_inputs=data_data.get('optional_inputs', []),
            data_formats=data_data.get('data_formats', []),
            file_size_limits=data_data.get('file_size_limits', ''),
            preprocessing_steps=data_data.get('preprocessing_steps', [])
        )

        # 解析发表文章
        pub_data = merged_result.get('publications', [])
        publications = [
            Publication(
                title=pub.get('title', ''),
                authors=pub.get('authors', []),
                journal=pub.get('journal'),
                year=pub.get('year'),
                doi=pub.get('doi'),
                pmid=pub.get('pmid')
            )
            for pub in pub_data
            if pub.get('title')
        ]

        # 解析架构信息
        arch_data = merged_result.get('architecture', {})
        architecture = ProjectArchitecture(
            programming_languages=arch_data.get('programming_languages', []),
            frameworks=arch_data.get('frameworks', []),
            directory_structure=arch_data.get('directory_structure', {}),
            main_components=arch_data.get('main_components', []),
            entry_points=arch_data.get('entry_points', []),
            config_files=arch_data.get('config_files', []),
            test_structure=arch_data.get('test_structure', {})
        )

        # 解析安全信息
        security_data = merged_result.get('security_analysis', {})
        if security_data:
            security = SecurityAnalysis(
                vulnerabilities=security_data.get('vulnerabilities', []),
                sensitive_data=security_data.get('sensitive_data', []),
                dependencies=security_data.get('dependencies', [])
            )
        else:
            security = None

        return BioToolAnalysis(
            repository=repo_info,
            authors=authors,
            publications=publications,
            functionality=functionality,
            usage=usage,
            architecture=architecture,
            code_quality=merged_result.get('code_quality'),
            performance=performance,
            bioinformatics_expertise=merged_result.get('bioinformatics_expertise'),
            usability=merged_result.get('usability'),
            deployment=deployment,
            testing=testing,
            data_requirements=data_requirements,
            security=security,
            analysis_timestamp=datetime.now().isoformat(),
        )

    def _create_fallback_analysis(self, repo_info, authors) -> BioToolAnalysis:
        """创建降级分析结果"""
        return BioToolAnalysis(
            repository=repo_info,
            authors=authors,
            publications=[],
            functionality=FunctionalityInfo(
                main_purpose="生物信息学工具",
                key_features=[],
                input_formats=[],
                output_formats=[],
                dependencies=[]
            ),
            usage=UsageInfo(
                installation="参考项目文档",
                basic_usage="参考项目文档",
                examples=[],
                parameters=[]
            ),
            deployment=None,
            testing=None,
            data_requirements=None,
            analysis_timestamp=datetime.now().isoformat(),
        )

    async def _security_validation_hook(self, tool_call):
        """安全验证Hook"""
        # 基本安全检查
        dangerous_operations = ['rm -rf', 'sudo', 'chmod 777']
        tool_args = str(tool_call.get('arguments', ''))

        for dangerous_op in dangerous_operations:
            if dangerous_op in tool_args:
                print(f"⚠️ 安全警告: 检测到潜在危险操作: {dangerous_op}")
                return False

        return True

    async def _result_quality_hook(self, tool_result):
        """结果质量检查Hook"""
        # 基本结果验证
        if hasattr(tool_result, 'content'):
            content = str(tool_result.content)
            if len(content) > 100000:  # 限制结果大小
                print("⚠️ 结果过大，将被截断")
                return False

        return True