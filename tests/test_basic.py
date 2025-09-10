"""基础功能测试"""

import pytest

from src.github_analyzer import GitHubAnalyzer
from src.models import AuthorInfo, RepositoryInfo


def test_repository_info_creation():
    """测试仓库信息模型创建"""
    repo = RepositoryInfo(
        name="test-repo",
        url="https://github.com/user/test-repo",
        description="测试仓库",
        language="Python",
        stars=100,
        forks=20
    )
    assert repo.name == "test-repo"
    assert repo.stars == 100


def test_author_info_creation():
    """测试作者信息模型创建"""
    author = AuthorInfo(
        name="张三",
        email="zhangsan@example.com"
    )
    assert author.name == "张三"
    assert author.email == "zhangsan@example.com"


def test_github_analyzer_init():
    """测试GitHub分析器初始化"""
    analyzer = GitHubAnalyzer()
    assert analyzer.tmp_dir.exists()


def test_extract_repo_name():
    """测试仓库名称提取"""
    analyzer = GitHubAnalyzer()
    
    # 测试不同格式的URL
    urls = [
        "https://github.com/user/repo",
        "https://github.com/user/repo.git",
        "https://github.com/user/repo/",
    ]
    
    for url in urls:
        name = analyzer._extract_repo_name(url)
        assert name == "repo"


def test_parse_github_url():
    """测试GitHub URL解析"""
    analyzer = GitHubAnalyzer()
    
    url = "https://github.com/samtools/samtools"
    owner, repo = analyzer._parse_github_url(url)
    
    assert owner == "samtools"
    assert repo == "samtools"
