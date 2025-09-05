# 项目架构分析功能设计方案

## MVP功能需求

1. **核心功能**
   - 根据GitHub URL下载仓库（已有功能）
   - 分析项目架构（新功能）

2. **MVP功能列表**
   - 识别项目的主要编程语言
   - 识别项目的主要框架或库
   - 分析项目的目录结构
   - 识别项目的主要组件或模块
   - 识别项目的入口点（如main文件、CLI命令等）
   - 识别项目的配置文件
   - 识别项目的测试结构
   - 生成项目架构报告

## 技术实现方案

### 1. 数据模型扩展

在`src/models.py`中添加新的数据模型：

```python
class ProjectArchitecture(BaseModel):
    """项目架构信息模型"""
    programming_languages: List[str]
    frameworks: List[str]
    directory_structure: Dict[str, str]  # 路径: 描述
    main_components: List[str]
    entry_points: List[str]
    config_files: List[str]
    test_structure: Dict[str, str]  # 路径: 描述
```

### 2. 架构分析器实现

在`src/github_analyzer.py`中添加新的方法：

```python
def analyze_project_architecture(self, repo_path: Path) -> ProjectArchitecture:
    """分析项目架构"""
    # 实现架构分析逻辑
    pass
```

### 3. AI分析集成

在`src/ai_analyzer.py`中扩展AI分析功能，添加对项目架构的分析。

### 4. 可视化展示

在`src/visualizer.py`中添加架构信息的可视化展示。

## 实现步骤

1. 扩展数据模型
2. 实现架构分析方法
3. 集成AI分析功能
4. 更新可视化报告
5. 测试功能