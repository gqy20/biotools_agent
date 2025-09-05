"""数据模型定义"""

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict


class RepositoryInfo(BaseModel):
    """仓库基础信息模型"""
    
    name: str
    url: HttpUrl
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    license: Optional[str] = None


class AuthorInfo(BaseModel):
    """作者信息模型"""
    
    name: str
    email: Optional[str] = None
    github_username: Optional[str] = None


class Publication(BaseModel):
    """发表文章信息模型"""
    
    title: str
    authors: List[str]
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    pmid: Optional[str] = None


class FunctionalityInfo(BaseModel):
    """功能信息模型"""
    
    main_purpose: str
    key_features: List[str]
    input_formats: List[str]
    output_formats: List[str]
    dependencies: List[str]


class UsageInfo(BaseModel):
    """使用方法信息模型"""
    
    installation: str
    basic_usage: str
    examples: List[str]
    parameters: List[str]


class ProjectArchitecture(BaseModel):
    """项目架构信息模型"""
    
    programming_languages: List[str]
    frameworks: List[str]
    directory_structure: Dict[str, str]
    main_components: List[str]
    entry_points: List[str]
    config_files: List[str]
    test_structure: Dict[str, str]


class BioToolAnalysis(BaseModel):
    """完整的生物信息学工具分析结果"""
    
    repository: RepositoryInfo
    authors: List[AuthorInfo]
    publications: List[Publication]
    functionality: FunctionalityInfo
    usage: UsageInfo
    architecture: Optional[ProjectArchitecture] = None
    analysis_timestamp: str
