# BioTools Agent

一个自动化工具，用于分析生物信息学GitHub仓库并生成可视化文档。

## 功能特性

- 自动克隆GitHub生物信息学工具仓库
- 智能分析项目基础信息、作者、相关文章
- 提取功能描述和使用方法
- 生成美观的可视化文档

## 快速开始

### 🚀 方式一: GitHub Actions (推荐)

**无需本地环境，直接在GitHub上运行分析！**

1. Fork 本仓库到您的 GitHub 账号
2. 在仓库 Settings → Secrets 中配置 API 密钥
3. 前往 Actions 页面，选择 "BioTools Analysis" 工作流
4. 点击 "Run workflow"，输入要分析的 GitHub 项目 URL
5. 等待分析完成，下载 Artifacts 中的报告文件

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
# 基本使用
biotools-agent analyze https://github.com/username/biotools-repo

# 使用自定义配置文件
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
| `GITHUB_TOKEN` | GitHub访问令牌 (可选) | - |

### 支持的AI服务

- **OpenAI官方API**
- **ModelScope API** (如千问模型)
- **其他兼容OpenAI格式的API服务**

## 项目结构

```
biotools_agent/
├── .github/workflows/          # GitHub Actions 工作流
│   ├── biotools-analysis.yml  # 单项目分析工作流
│   └── batch-analysis.yml     # 批量分析工作流
├── src/                       # 源代码目录
│   ├── ai_analyzer.py         # AI分析器
│   ├── config.py              # 配置管理
│   ├── github_analyzer.py     # GitHub仓库分析器
│   ├── llm_client.py          # LLM客户端
│   ├── main.py                # 主程序入口
│   ├── models.py              # 数据模型
│   └── visualizer.py          # 可视化报告生成器
├── docs/                      # 文档目录
│   ├── GITHUB_ACTIONS_GUIDE.md  # GitHub Actions使用指南
│   └── biotools_agent_pr.md     # 项目文档
├── tests/                     # 测试目录
├── test_results/              # 测试结果示例
├── data/                      # 测试数据
├── env.example                # 配置文件模板
└── pyproject.toml             # 项目配置
```

## 许可证

MIT License
