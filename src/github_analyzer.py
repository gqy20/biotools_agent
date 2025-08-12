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
from .models import RepositoryInfo, AuthorInfo


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
            response = requests.get(api_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
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
                # API调用失败，使用基础信息
                return RepositoryInfo(
                    name=repo_name,
                    url=repo_url
                )
        except Exception as e:
            print(f"⚠️ 获取仓库信息失败: {e}")
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
