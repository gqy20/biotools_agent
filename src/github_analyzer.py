"""GitHub仓库分析器"""

import os
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Optional

import git
import requests
from bs4 import BeautifulSoup

from .config import config_manager
from .models import RepositoryInfo, AuthorInfo, ProjectArchitecture


class GitHubAnalyzer:
    """GitHub仓库分析器"""
    
    def __init__(self, tmp_dir: str = None):
        self.tmp_dir = Path(tmp_dir or config_manager.config.tmp_dir)
        self.tmp_dir.mkdir(exist_ok=True)
        self.headers = config_manager.get_github_headers()
    
    def clone_repository(self, repo_url: str) -> Path:
        """克隆GitHub仓库到临时目录"""
        repo_name = self._extract_repo_name(repo_url)
        clone_path = self.tmp_dir / repo_name
        
        # 如果目录已存在，先删除
        if clone_path.exists():
            import shutil
            shutil.rmtree(clone_path)
        
        # 检查是否是本地文件路径
        if repo_url.startswith("file://"):
            local_path = Path(repo_url[7:])  # 移除 "file://" 前缀
            if local_path.exists():
                # 复制本地目录到临时目录
                shutil.copytree(local_path, clone_path)
                print(f"✅ 成功复制本地仓库到: {clone_path}")
                return clone_path
            else:
                raise RuntimeError(f"本地路径不存在: {local_path}")
        else:
            try:
                git.Repo.clone_from(repo_url, clone_path)
                print(f"✅ 成功克隆仓库到: {clone_path}")
                return clone_path
            except Exception as e:
                raise RuntimeError(f"克隆仓库失败: {e}")
    
    def analyze_repository_info(self, repo_url: str) -> RepositoryInfo:
        """分析仓库基础信息"""
        owner, repo_name = self._parse_github_url(repo_url)
        
        # 调用GitHub API获取仓库信息
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        
        try:
            # 首先尝试带认证的调用
            response = requests.get(api_url, headers=self.headers, timeout=10)
            
            # 如果认证失败，尝试无认证调用
            if response.status_code == 401:
                print("⚠️ GitHub认证失败，尝试无认证访问...")
                response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 成功获取GitHub仓库信息: {data.get('stargazers_count')} stars")
                return RepositoryInfo(
                    name=data.get("name", repo_name),
                    url=repo_url,
                    description=data.get("description"),
                    language=data.get("language"),
                    stars=data.get("stargazers_count", 0),
                    forks=data.get("forks_count", 0),
                    license=data.get("license", {}).get("name") if data.get("license") else None
                )
            else:
                print(f"⚠️ GitHub API调用失败，状态码: {response.status_code}")
                # API调用失败，使用基础信息
                return RepositoryInfo(
                    name=repo_name,
                    url=repo_url
                )
        except Exception as e:
            print(f"⚠️ 获取仓库信息失败: {e}")
            # 异常情况，使用基础信息
            return RepositoryInfo(
                name=repo_name,
                url=repo_url
            )
            return RepositoryInfo(
                name=repo_name,
                url=repo_url
            )
    
    def extract_authors_from_repo(self, repo_path: Path) -> List[AuthorInfo]:
        """从仓库中提取作者信息"""
        authors = []
        
        # 1. 从README文件中提取作者信息
        readme_authors = self._extract_authors_from_readme(repo_path)
        authors.extend(readme_authors)
        
        # 2. 从setup.py或pyproject.toml中提取作者信息
        setup_authors = self._extract_authors_from_setup_files(repo_path)
        authors.extend(setup_authors)
        
        # 3. 从Git提交记录中提取作者信息
        git_authors = self._extract_authors_from_git(repo_path)
        authors.extend(git_authors)
        
        # 去重处理
        unique_authors = self._deduplicate_authors(authors)
        
        return unique_authors
    
    def analyze_project_architecture(self, repo_path: Path) -> ProjectArchitecture:
        """分析项目架构"""
        # 1. 识别主要编程语言
        programming_languages = self._detect_programming_languages(repo_path)
        
        # 2. 识别框架和库
        frameworks = self._detect_frameworks(repo_path)
        
        # 3. 分析目录结构
        directory_structure = self._analyze_directory_structure(repo_path)
        
        # 4. 识别主要组件
        main_components = self._identify_main_components(repo_path)
        
        # 5. 识别入口点
        entry_points = self._identify_entry_points(repo_path)
        
        # 6. 识别配置文件
        config_files = self._identify_config_files(repo_path)
        
        # 7. 识别测试结构
        test_structure = self._analyze_test_structure(repo_path)
        
        return ProjectArchitecture(
            programming_languages=programming_languages,
            frameworks=frameworks,
            directory_structure=directory_structure,
            main_components=main_components,
            entry_points=entry_points,
            config_files=config_files,
            test_structure=test_structure
        )
    
    def read_file_content(self, repo_path: Path, filename: str) -> Optional[str]:
        """读取指定文件内容"""
        file_patterns = [
            filename,
            filename.upper(),
            filename.lower(),
            f"{filename}.md",
            f"{filename.upper()}.md",
            f"{filename.lower()}.md",
            f"{filename}.txt",
            f"{filename.upper()}.txt",
            f"{filename.lower()}.txt",
        ]
        
        for pattern in file_patterns:
            file_path = repo_path / pattern
            if file_path.exists() and file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except UnicodeDecodeError:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            return f.read()
                    except Exception:
                        continue
        
        return None
    
    def _extract_repo_name(self, repo_url: str) -> str:
        """从URL中提取仓库名称"""
        return repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    
    def _parse_github_url(self, repo_url: str) -> tuple:
        """解析GitHub URL获取owner和repo名称"""
        # 处理不同格式的GitHub URL
        if 'github.com' in repo_url:
            parts = repo_url.replace('https://', '').replace('http://', '').replace('.git', '').split('/')
            if len(parts) >= 3:
                return parts[1], parts[2]
        
        raise ValueError(f"无效的GitHub URL: {repo_url}")
    
    def _extract_authors_from_readme(self, repo_path: Path) -> List[AuthorInfo]:
        """从README文件中提取作者信息"""
        authors = []
        readme_content = self.read_file_content(repo_path, "README")
        
        if not readme_content:
            return authors
        
        # 查找作者相关的模式
        author_patterns = [
            r'(?i)author[s]?[:\-\s]*([^\n]+)',
            r'(?i)contributor[s]?[:\-\s]*([^\n]+)',
            r'(?i)developed?\s+by[:\-\s]*([^\n]+)',
            r'(?i)created?\s+by[:\-\s]*([^\n]+)',
            r'(?i)maintainer[s]?[:\-\s]*([^\n]+)',
        ]
        
        for pattern in author_patterns:
            matches = re.findall(pattern, readme_content)
            for match in matches:
                # 清理和解析作者信息
                author_text = match.strip()
                if author_text and len(author_text) < 100:  # 避免提取过长的文本
                    author_info = self._parse_author_text(author_text)
                    if author_info:
                        authors.append(author_info)
        
        return authors
    
    def _extract_authors_from_setup_files(self, repo_path: Path) -> List[AuthorInfo]:
        """从setup文件中提取作者信息"""
        authors = []
        
        # 检查setup.py
        setup_py_path = repo_path / "setup.py"
        if setup_py_path.exists():
            setup_content = self.read_file_content(repo_path, "setup.py")
            if setup_content:
                author_matches = re.findall(r'author\s*=\s*["\']([^"\']+)["\']', setup_content)
                for author in author_matches:
                    authors.append(AuthorInfo(name=author.strip()))
        
        # 检查pyproject.toml
        pyproject_path = repo_path / "pyproject.toml"
        if pyproject_path.exists():
            pyproject_content = self.read_file_content(repo_path, "pyproject.toml")
            if pyproject_content:
                author_matches = re.findall(r'name\s*=\s*["\']([^"\']+)["\']', pyproject_content)
                for author in author_matches:
                    authors.append(AuthorInfo(name=author.strip()))
        
        return authors
    
    def _extract_authors_from_git(self, repo_path: Path) -> List[AuthorInfo]:
        """从Git提交记录中提取作者信息"""
        authors = []
        
        try:
            repo = git.Repo(repo_path)
            commits = list(repo.iter_commits(max_count=100))  # 只检查最近100次提交
            
            author_set = set()
            for commit in commits:
                author_name = commit.author.name
                author_email = commit.author.email
                
                if author_name and author_name not in author_set:
                    author_set.add(author_name)
                    authors.append(AuthorInfo(
                        name=author_name,
                        email=author_email if '@' in author_email else None
                    ))
        
        except Exception as e:
            print(f"⚠️ 从Git记录提取作者信息失败: {e}")
        
        return authors
    
    def _parse_author_text(self, text: str) -> Optional[AuthorInfo]:
        """解析作者文本信息"""
        # 移除常见的标记符号
        cleaned_text = re.sub(r'[*\[\](){}]', '', text).strip()
        
        # 提取邮箱
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', cleaned_text)
        email = email_match.group(1) if email_match else None
        
        # 移除邮箱后的名称
        name = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '', cleaned_text).strip()
        name = re.sub(r'[<>]', '', name).strip()
        
        if name and len(name) > 1:
            return AuthorInfo(name=name, email=email)
        
        return None
    
    def _deduplicate_authors(self, authors: List[AuthorInfo]) -> List[AuthorInfo]:
        """去重作者信息"""
        seen_names = set()
        unique_authors = []
        
        for author in authors:
            # 标准化名称进行比较
            normalized_name = author.name.lower().strip()
            if normalized_name not in seen_names and len(normalized_name) > 1:
                seen_names.add(normalized_name)
                unique_authors.append(author)
        
        return unique_authors[:10]  # 最多返回10个作者

    def _detect_programming_languages(self, repo_path: Path) -> List[str]:
        """检测项目使用的编程语言"""
        languages = set()
        
        # 通过文件扩展名识别编程语言
        extension_mapping = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#',
            '.go': 'Go',
            '.rs': 'Rust',
            '.rb': 'Ruby',
            '.php': 'PHP',
            '.swift': 'Swift',
            '.kt': 'Kotlin',
            '.R': 'R',
            '.r': 'R',
            '.sql': 'SQL',
            '.sh': 'Shell',
            '.pl': 'Perl',
            '.lua': 'Lua',
            '.dart': 'Dart',
            '.scala': 'Scala',
            '.m': 'Objective-C',
            '.mm': 'Objective-C++',
            '.groovy': 'Groovy',
            '.hs': 'Haskell',
            '.clj': 'Clojure',
            '.ex': 'Elixir',
            '.exs': 'Elixir',
            '.erl': 'Erlang',
            '.fs': 'F#',
            '.ml': 'OCaml',
            '.mli': 'OCaml'
        }
        
        # 遍历项目文件
        for root, dirs, files in os.walk(repo_path):
            # 跳过隐藏目录和node_modules等
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
            
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in extension_mapping:
                    languages.add(extension_mapping[ext])
        
        # 检查特殊文件
        if (repo_path / "Cargo.toml").exists():
            languages.add("Rust")
        if (repo_path / "go.mod").exists():
            languages.add("Go")
        if (repo_path / "package.json").exists():
            languages.add("JavaScript")
        if (repo_path / "requirements.txt").exists() or (repo_path / "setup.py").exists() or (repo_path / "pyproject.toml").exists():
            languages.add("Python")
        
        return list(languages)
    
    def _detect_frameworks(self, repo_path: Path) -> List[str]:
        """检测项目使用的框架和库"""
        frameworks = []
        
        # Python框架检测
        if (repo_path / "requirements.txt").exists():
            content = self.read_file_content(repo_path, "requirements.txt") or ""
            python_frameworks = {
                'django': 'Django',
                'flask': 'Flask',
                'fastapi': 'FastAPI',
                'pyramid': 'Pyramid',
                'tornado': 'Tornado',
                'dash': 'Dash',
                'streamlit': 'Streamlit',
                'numpy': 'NumPy',
                'pandas': 'Pandas',
                'scikit-learn': 'Scikit-learn',
                'tensorflow': 'TensorFlow',
                'torch': 'PyTorch',
                'keras': 'Keras'
            }
            for package, framework in python_frameworks.items():
                if package in content.lower():
                    frameworks.append(framework)
        
        if (repo_path / "setup.py").exists() or (repo_path / "pyproject.toml").exists():
            content = self.read_file_content(repo_path, "setup.py") or self.read_file_content(repo_path, "pyproject.toml") or ""
            python_frameworks = {
                'django': 'Django',
                'flask': 'Flask',
                'fastapi': 'FastAPI',
                'pyramid': 'Pyramid',
                'tornado': 'Tornado',
                'dash': 'Dash',
                'streamlit': 'Streamlit'
            }
            for package, framework in python_frameworks.items():
                if package in content.lower():
                    frameworks.append(framework)
        
        # JavaScript/Node.js框架检测
        if (repo_path / "package.json").exists():
            content = self.read_file_content(repo_path, "package.json") or ""
            js_frameworks = {
                'react': 'React',
                'vue': 'Vue.js',
                'angular': 'Angular',
                'express': 'Express',
                'next': 'Next.js',
                'nuxt': 'Nuxt.js',
                'svelte': 'Svelte',
                'ember': 'Ember.js'
            }
            for package, framework in js_frameworks.items():
                if package in content.lower():
                    frameworks.append(framework)
        
        # Java框架检测
        if (repo_path / "pom.xml").exists() or (repo_path / "build.gradle").exists():
            content = self.read_file_content(repo_path, "pom.xml") or self.read_file_content(repo_path, "build.gradle") or ""
            java_frameworks = {
                'spring': 'Spring',
                'hibernate': 'Hibernate',
                'struts': 'Struts',
                'play': 'Play Framework'
            }
            for framework_key, framework_name in java_frameworks.items():
                if framework_key in content.lower():
                    frameworks.append(framework_name)
        
        return list(set(frameworks))  # 去重
    
    def _analyze_directory_structure(self, repo_path: Path) -> Dict[str, str]:
        """分析目录结构"""
        directory_structure = {}
        
        def analyze_dir(path: Path, prefix: str = ""):
            if path.name.startswith('.') or path.name in ['node_modules', 'venv', '__pycache__', '.git']:
                return
            
            for item in path.iterdir():
                if item.is_dir():
                    # 记录目录
                    dir_path = f"{prefix}/{item.name}" if prefix else item.name
                    # 尝试识别目录用途
                    purpose = self._identify_directory_purpose(item)
                    directory_structure[dir_path] = purpose
                    # 递归分析子目录，但限制深度
                    if prefix.count('/') < 2:  # 限制递归深度
                        analyze_dir(item, dir_path)
                elif item.is_file() and prefix == "":  # 根目录的文件
                    directory_structure[item.name] = "根目录文件"
        
        analyze_dir(repo_path)
        return directory_structure
    
    def _identify_directory_purpose(self, dir_path: Path) -> str:
        """识别目录用途"""
        dir_name = dir_path.name.lower()
        
        purpose_mapping = {
            'src': '源代码目录',
            'source': '源代码目录',
            'lib': '库文件目录',
            'libs': '库文件目录',
            'library': '库文件目录',
            'bin': '可执行文件目录',
            'dist': '构建输出目录',
            'build': '构建目录',
            'out': '输出目录',
            'target': 'Maven/Gradle构建目录',
            'test': '测试目录',
            'tests': '测试目录',
            'spec': '测试目录',
            'specs': '测试目录',
            'docs': '文档目录',
            'doc': '文档目录',
            'documentation': '文档目录',
            'config': '配置文件目录',
            'conf': '配置文件目录',
            'cfg': '配置文件目录',
            'scripts': '脚本目录',
            'script': '脚本目录',
            'tools': '工具目录',
            'utils': '工具目录',
            'util': '工具目录',
            'examples': '示例目录',
            'example': '示例目录',
            'demo': '演示目录',
            'demos': '演示目录',
            'assets': '资源文件目录',
            'static': '静态文件目录',
            'public': '公共资源目录',
            'templates': '模板目录',
            'views': '视图目录',
            'controllers': '控制器目录',
            'models': '模型目录',
            'services': '服务目录',
            'api': 'API接口目录',
            'routes': '路由目录'
        }
        
        return purpose_mapping.get(dir_name, "普通目录")
    
    def _identify_main_components(self, repo_path: Path) -> List[str]:
        """识别主要组件"""
        components = []
        
        # 通过目录结构识别组件
        for item in repo_path.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in ['node_modules', 'venv', '__pycache__', '.git']:
                components.append(item.name)
        
        # 通过特殊文件识别组件
        special_files = {
            'Dockerfile': 'Docker容器',
            'docker-compose.yml': 'Docker容器编排',
            'docker-compose.yaml': 'Docker容器编排',
            'Makefile': '构建工具',
            'CMakeLists.txt': 'CMake构建配置',
            'pom.xml': 'Maven项目配置',
            'build.gradle': 'Gradle项目配置',
            'webpack.config.js': 'Webpack打包配置',
            'vite.config.js': 'Vite构建配置',
            'package.json': 'Node.js项目配置'
        }
        
        for file_name, component in special_files.items():
            if (repo_path / file_name).exists():
                components.append(component)
        
        return list(set(components))  # 去重
    
    def _identify_entry_points(self, repo_path: Path) -> List[str]:
        """识别项目入口点"""
        entry_points = []
        
        # Python项目入口点
        if (repo_path / "setup.py").exists():
            content = self.read_file_content(repo_path, "setup.py") or ""
            entry_matches = re.findall(r'entry_points.*?console_scripts.*?=\s*\[(.*?)\]', content, re.DOTALL | re.IGNORECASE)
            if entry_matches:
                entry_points.append("Python CLI命令")
        
        # 查找main文件
        for item in repo_path.iterdir():
            if item.is_file():
                if item.name.startswith('main.') or 'main' in item.name:
                    entry_points.append(f"主程序文件: {item.name}")
                elif item.name == "app.py" or item.name == "application.py":
                    entry_points.append(f"应用入口: {item.name}")
        
        # 查找可执行脚本
        scripts_dir = repo_path / "scripts"
        if scripts_dir.exists() and scripts_dir.is_dir():
            for script in scripts_dir.iterdir():
                if script.is_file() and script.stat().st_mode & 0o111:  # 可执行文件
                    entry_points.append(f"可执行脚本: {script.name}")
        
        # package.json中的scripts
        if (repo_path / "package.json").exists():
            content = self.read_file_content(repo_path, "package.json") or ""
            if '"start"' in content or '"dev"' in content:
                entry_points.append("Node.js应用入口")
        
        return entry_points
    
    def _identify_config_files(self, repo_path: Path) -> List[str]:
        """识别配置文件"""
        config_files = []
        
        common_configs = [
            'config.json', 'config.yaml', 'config.yml', 'config.toml',
            'settings.json', 'settings.yaml', 'settings.yml',
            '.env', '.env.local', '.env.production',
            'application.properties', 'application.yml',
            'web.xml', 'server.xml',
            'nginx.conf', 'apache.conf',
            'docker-compose.yml', 'docker-compose.yaml'
        ]
        
        for config in common_configs:
            if (repo_path / config).exists():
                config_files.append(config)
        
        # 查找配置目录中的文件
        config_dirs = ['config', 'conf', 'cfg']
        for dir_name in config_dirs:
            config_dir = repo_path / dir_name
            if config_dir.exists() and config_dir.is_dir():
                for config_file in config_dir.iterdir():
                    if config_file.is_file():
                        config_files.append(f"{dir_name}/{config_file.name}")
        
        return config_files
    
    def _analyze_test_structure(self, repo_path: Path) -> Dict[str, str]:
        """分析测试结构"""
        test_structure = {}
        
        # 查找测试目录
        test_dirs = ['test', 'tests', 'spec', 'specs']
        for dir_name in test_dirs:
            test_dir = repo_path / dir_name
            if test_dir.exists() and test_dir.is_dir():
                # 分析测试目录中的文件和子目录
                for item in test_dir.iterdir():
                    if item.is_dir():
                        test_structure[f"{dir_name}/{item.name}"] = "测试子目录"
                    elif item.is_file():
                        test_structure[f"{dir_name}/{item.name}"] = "测试文件"
        
        # 查找根目录的测试文件
        for item in repo_path.iterdir():
            if item.is_file() and 'test' in item.name.lower():
                test_structure[item.name] = "根目录测试文件"
        
        return test_structure
