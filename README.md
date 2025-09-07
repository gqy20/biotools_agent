# BioTools Agent

一个自动化工具，用于分析生物信息学GitHub仓库并生成可视化文档。

## 功能特性

- 自动克隆GitHub生物信息学工具仓库
- 智能分析项目基础信息、作者、相关文章
- 提取功能描述和使用方法
- 生成美观的可视化文档
- **新增：项目架构分析** - 分析项目的编程语言、框架、目录结构等
- **新增：全面的AI分析** - 包括代码质量、性能特征、生物信息学专业性和可用性分析

## 快速开始

### 🚀 方式一: GitHub Actions (推荐)

**无需本地环境，直接在GitHub上运行分析！**

1. Fork 本仓库到您的 GitHub 账号
2. 在仓库 Settings → Environments 中配置 API 密钥和 Supabase 数据库配置
3. 前往 Actions 页面，选择 "BioTools Analysis" 工作流
4. 点击 "Run workflow"，输入要分析的 GitHub 项目 URL
5. 等待分析完成，下载 Artifacts 中的报告文件，分析结果也会自动保存到 Supabase 数据库

详细说明请参考: [GitHub Actions 使用指南](docs/GITHUB_ACTIONS_GUIDE.md)

### 💻 方式二: 本地安装使用

#### 1. 安装依赖
```bash
uv pip install -e .
```

#### 2. 配置环境
复制配置模板并编辑：
```bash
cp env.example .env
# 编辑.env文件，配置您的API密钥
```

#### 3. 运行分析
```bash
# 基本使用（默认会保存到数据库）
biotools-agent analyze https://github.com/username/biotools-repo

# 禁用保存到数据库
biotools-agent analyze https://github.com/username/biotools-repo --no-save-to-db

# 使用自定义配置文件
biotools-agent analyze https://github.com/username/biotools-repo --env-file custom.env
```

## 🎯 分析结果

经过增强的AI分析系统现在提供：

### 📋 基础信息
- **项目概览**: 名称、描述、语言、Stars/Forks统计
- **作者信息**: 自动提取贡献者信息 
- **相关论文**: 识别相关发表文章

### 🔧 功能分析  
- **主要用途**: 一句话概括工具功能（强制中文输出）
- **核心特性**: 详细功能列表
- **输入输出格式**: 支持的数据格式
- **使用示例**: 基本用法和参数说明

### 🏗️ 架构分析
- **编程语言**: 项目使用的主要语言
- **框架依赖**: 使用的框架和库
- **目录结构**: 项目组织方式
- **入口点**: 主要可执行文件

### ⚡ 性能特征
- **算法复杂度**: 时间和空间复杂度分析
- **并行化支持**: 多核利用能力
- **性能优化**: 改进建议

### 🚀 部署信息 
- **安装方法**: 多种安装方式
- **系统要求**: 操作系统和依赖需求
- **容器支持**: Docker/Singularity等
- **云部署**: 云平台支持情况

### 🧪 测试信息
- **测试命令**: 如何运行测试
- **示例数据**: 测试数据来源
- **验证方法**: 结果验证方式
- **基准数据集**: 性能测试数据

### 📊 数据需求
- **必需输入**: 运行所需的数据格式
- **可选输入**: 增强功能的额外数据  
- **预处理步骤**: 数据准备流程
- **文件大小限制**: 处理能力范围

## 💡 特色功能

- **🌐 中文友好**: 所有分析结果强制中文输出，便于中文用户理解
- **🔍 代码级分析**: 深入分析核心算法和实现细节
- **📚 全面文档**: 自动生成HTML、Markdown、JSON多种格式报告
- **🎯 准确识别**: 智能区分生物信息学专业工具vs通用软件
biotools-agent analyze https://github.com/username/repo --env-file custom.env

# 检查配置
biotools-agent config
```

## 配置说明

项目支持通过环境变量或.env文件进行配置：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 (必需) | - |
| `OPENAI_BASE_URL` | API基础URL | `https://api.openai.com/v1` |
| `OPENAI_MODEL` | 使用的模型名称 | `gpt-3.5-turbo` |
| `HUB_TOKEN` | GitHub访问令牌 (可选) | - |
| `SUPABASE_URL` | Supabase项目URL (可选，用于保存分析结果) | - |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase服务角色密钥 (可选，用于保存分析结果) | - |

### 支持的AI服务

- **OpenAI官方API**
- **ModelScope API** (如千问模型)
- **其他兼容OpenAI格式的API服务**

### 数据库导出功能

分析结果默认会保存到 Supabase 数据库中。要启用此功能，需要配置 `SUPABASE_URL` 和 `SUPABASE_SERVICE_ROLE_KEY`。

数据库表结构：
```
bio_analysis_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    test_id UUID DEFAULT gen_random_uuid() NOT NULL,
    analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    repo_url TEXT NOT NULL,
    data JSONB NOT NULL
)
```

**注意：** 为了支持对同一项目的多次测试，数据库表结构已更新，使用 `test_id` 作为每次测试的唯一标识符，
而不是使用 `repo_url` 作为唯一键。这样可以保留同一项目的多次测试记录。

分析数据包含以下信息：
- 仓库基础信息（名称、URL、描述、语言、Stars、Forks等）
- 作者信息
- 相关发表文章
- 功能特性
- 使用方法
- 项目架构（编程语言、框架、目录结构等）
- 代码质量评估
- 性能特征分析
- 生物信息学专业性评估
- 可用性评估

更多信息请参考: [数据库更新说明](docs/DATABASE_UPDATE.md)

## 项目结构

```
biotools_agent/
├── .github/workflows/          # GitHub Actions 工作流
│   ├── biotools-analysis.yml  # 单项目分析工作流
│   └── batch-analysis.yml     # 批量分析工作流
├── src/                       # 源代码目录
│   ├── ai_analyzer.py         # AI分析器（新增：扩展的AI分析功能）
│   ├── config.py              # 配置管理
│   ├── github_analyzer.py     # GitHub仓库分析器（新增：项目架构分析）
│   ├── llm_client.py          # LLM客户端
│   ├── main.py                # 主程序入口
│   ├── models.py              # 数据模型（新增：扩展的数据模型）
│   ├── supabase_client.py     # Supabase数据库客户端
│   └── visualizer.py          # 可视化报告生成器（新增：扩展的可视化功能）
├── docs/                      # 文档目录
│   ├── ARCHITECTURE_ANALYSIS_DESIGN.md  # 项目架构分析设计文档
│   ├── DATABASE_UPDATE.md     # 数据库更新说明
│   ├── GITHUB_ACTIONS_GUIDE.md  # GitHub Actions使用指南
│   └── biotools_agent_pr.md   # 项目文档
├── tests/                     # 测试目录
├── test_results/              # 测试结果示例
├── data/                      # 测试数据
├── env.example                # 配置文件模板
└── pyproject.toml             # 项目配置
```

## 许可证

MIT License
