# GitHub Actions 使用指南

## 🚀 概述

BioTools Agent 提供了两个 GitHub Actions 工作流，可以直接在 GitHub 上执行生物信息学工具分析，无需本地环境配置。

## ⚙️ 环境配置

### 必需的环境配置

在使用工作流之前，需要在 GitHub 仓库中配置环境变量。工作流使用名为 `biotools` 的环境：

#### 步骤一：创建环境
1. 前往仓库的 `Settings` → `Environments`
2. 点击 `New environment`
3. 环境名称输入：`biotools`
4. 点击 `Configure environment`

#### 步骤二：配置环境权限 (可选)
- **Required reviewers**: 可以不设置，用于自动化运行
- **Wait timer**: 设置为 0 分钟，避免不必要的等待
- **Deployment branches**: 选择 `All branches` 或配置特定分支

#### 步骤三：添加环境变量
在 `biotools` 环境配置页面的 **Environment variables** 部分，添加以下变量：

| 环境变量名称 | 说明 | 示例值 |
|-------------|------|--------|
| `OPENAI_API_KEY` | ModelScope API 密钥 | `ms-xxxxxxxxxxxxx` |
| `OPENAI_BASE_URL` | API 基础地址 | `https://api-inference.modelscope.cn/v1` |
| `OPENAI_MODEL` | 使用的模型名称 | `Qwen/Qwen3-235B-A22B-Instruct-2507` |
| `HUB_TOKEN` | GitHub Personal Access Token (可选) | `ghp_xxxxxxxxxxxxx` |
| `SUPABASE_URL` | Supabase 项目 URL (可选，用于保存分析结果) | `https://your-project.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase 服务角色密钥 (可选，用于保存分析结果) | `sb_secret_xxxxxxxxxx` |

> 📝 **注意**: 
> - 所有变量都配置在 `biotools` 环境中，而不是 repository secrets
> - `HUB_TOKEN` 是可选的，用于提高 GitHub API 访问限制
> - `SUPABASE_URL` 和 `SUPABASE_SERVICE_ROLE_KEY` 是可选的，用于将分析结果保存到 Supabase 数据库
> - 环境配置提供了更好的安全性和管理便利性

## 🔧 工作流说明

### 1. 单项目分析 (`biotools-analysis.yml`)

**功能**: 分析单个 GitHub 生物信息学工具项目，提供全面的AI分析，包括项目架构、代码质量、性能特征、生物信息学专业性和可用性评估，默认将结果保存到 Supabase 数据库

**触发方式**: 手动触发 (workflow_dispatch)

**使用步骤**:
1. 前往仓库的 `Actions` 页面
2. 选择 `BioTools Analysis` 工作流
3. 点击 `Run workflow`
4. 填写参数：
   - **GitHub URL**: 要分析的项目地址 (例如: `https://github.com/c-zhou/yahs`)
   - **输出格式**: 生成的报告格式 (默认: `html,md,json`)
   - **任务名称**: 自定义任务名称 (可选)
5. 点击 `Run workflow` 开始分析

**输出结果**:
- HTML 可视化报告（包含完整的项目分析）
- Markdown 文档
- JSON 结构化数据
- 分析摘要文件
- 自动保存到 Supabase 数据库（如果配置了 Supabase）

**新增分析维度**:
- 项目架构分析（编程语言、框架、目录结构等）
- 代码质量评估
- 性能特征分析
- 生物信息学专业性评估
- 可用性评估

### 2. 批量分析 (`batch-analysis.yml`)

**功能**: 批量分析多个项目，提供全面的AI分析，包括项目架构、代码质量、性能特征、生物信息学专业性和可用性评估，默认将结果保存到 Supabase 数据库

**触发方式**: 手动触发 (workflow_dispatch)

**使用步骤**:
1. 前往仓库的 `Actions` 页面
2. 选择 `Batch BioTools Analysis` 工作流
3. 点击 `Run workflow`
4. 在 **CSV内容** 输入框中填写URL列表，每行一个：
   ```
   https://github.com/c-zhou/yahs
   https://github.com/CSU-KangHu/HiTE
   https://github.com/samtools/samtools
   ```
5. 设置任务名称 (可选)
6. 点击 `Run workflow` 开始批量分析

**输出结果**:
- 每个项目的完整分析报告（包含新增的分析维度）
- 批量分析汇总报告
- 成功率统计
- 自动保存到 Supabase 数据库（如果配置了 Supabase）

**新增分析维度**:
- 项目架构分析（编程语言、框架、目录结构等）
- 代码质量评估
- 性能特征分析
- 生物信息学专业性评估
- 可用性评估

## 📋 参数说明

### 单项目分析参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `github_url` | string | ✅ | - | GitHub项目URL |
| `output_formats` | string | ❌ | `html,md,json` | 输出格式，逗号分隔 |
| `analysis_name` | string | ❌ | `biotools-analysis` | 任务名称 |
| `user_message` | string | ❌ | `''` | 用户消息 (用于API调用) |

### 批量分析参数

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `csv_content` | string | ✅ | - | URL列表，每行一个 |
| `analysis_name` | string | ❌ | `batch-analysis` | 批量任务名称 |
| `user_message` | string | ❌ | `''` | 用户消息 (用于API调用) |

## 🔌 API 调用

### 通过 GitHub API 触发工作流

除了手动触发外，您还可以通过 GitHub API 或其他项目调用这些工作流：

#### API 调用示例 (单项目分析)

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/biotools_agent/actions/workflows/biotools-analysis.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "github_url": "https://github.com/c-zhou/yahs",
      "analysis_name": "api-test",
      "user_message": "API调用测试分析"
    }
  }'
```

#### API 调用示例 (批量分析)

```bash
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/repos/YOUR_USERNAME/biotools_agent/actions/workflows/batch-analysis.yml/dispatches \
  -d '{
    "ref": "main",
    "inputs": {
      "csv_content": "https://github.com/c-zhou/yahs\nhttps://github.com/CSU-KangHu/HiTE",
      "analysis_name": "batch-api-test",
      "user_message": "批量API调用测试"
    }
  }'
```

#### 参数说明

- **`ref`**: 要运行工作流的分支，通常是 `main`
- **`inputs`**: 工作流输入参数
  - `user_message`: 可选参数，用于标识API调用来源或传递额外信息
  - 其他参数与手动触发时相同

#### 权限要求

调用 API 需要具有 `actions:write` 权限的 GitHub Personal Access Token。

### 获取执行结果

GitHub Actions 是异步执行的，无法在 API 调用时直接返回结果。可以通过以下方式获取执行状态和结果：

#### 方法一：状态轮询

```javascript
// 轮询工作流状态
async function checkWorkflowStatus(owner, repo, workflowFile) {
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflowFile}/runs?per_page=5`,
    {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `token ${GITHUB_TOKEN}`
      }
    }
  );
  
  const data = await response.json();
  return data.workflow_runs[0]; // 最新的运行
}

// 检查状态：queued, in_progress, completed
// 检查结论：success, failure, cancelled
```

#### 方法二：Webhook 通知

设置 Repository Webhook 接收工作流完成通知：
- **Payload URL**: `https://your-api.com/webhook/github`
- **Content type**: `application/json`
- **Events**: 选择 `Workflow runs`

详细的结果获取方法请参考：[结果反馈机制文档](./RESULT_FEEDBACK.md)

## 📁 结果下载

### 下载步骤
1. 工作流完成后，前往 `Actions` 页面
2. 点击对应的工作流运行记录
3. 在 `Artifacts` 部分下载生成的文件包
4. 解压后即可查看分析报告

### 文件结构
```
biotools-analysis-{name}-{run_number}/
├── SUMMARY.md                    # 分析摘要
├── {project_name}_analysis.html  # HTML报告
├── {project_name}_analysis.md    # Markdown报告
└── {project_name}_analysis.json  # JSON数据
```

## ⏱️ 性能与限制

### 执行时间
- **单项目分析**: 通常 1-3 分钟
- **AI 分析阶段**: 约 10-15 秒
- **批量分析**: 每个项目约 1-3 分钟 + 15秒间隔

### 资源限制
- **超时时间**: 单个项目 5 分钟
- **文件保留**: Artifacts 保留 30 天
- **并发限制**: 批量分析按顺序执行，避免 API 限制

### API 配额
- ModelScope API 有调用频率限制
- 批量分析会在项目间增加 15 秒间隔
- 建议合理安排批量任务数量

## 🛠️ 故障排除

### 常见错误

**1. 环境配置错误**
- 错误信息: `❌ 配置验证失败`
- 解决方案: 
  - 确认已创建名为 `biotools` 的环境
  - 检查环境变量是否正确配置
  - 验证 API 密钥格式是否正确

**2. URL 格式错误**
- 错误信息: `❌ 错误: 请提供有效的GitHub URL格式`
- 解决方案: 确保 URL 格式为 `https://github.com/user/repo`

**3. 克隆超时**
- 错误信息: `❌ 分析超时或失败`
- 解决方案: 检查项目是否为公开仓库，仓库大小是否过大

**4. AI 分析失败**
- 错误信息: `❌ LLM调用失败`
- 解决方案: 检查 API 密钥是否有效，API 配额是否充足

### 调试技巧

1. **查看完整日志**: 点击工作流运行记录查看详细日志
2. **验证配置**: 工作流会先执行 `biotools-agent config` 验证配置
3. **分步执行**: 可以先用单项目分析测试配置
4. **联系支持**: 如遇到持续问题可提交 Issue

## 🔐 安全说明

- **环境变量保护**: `biotools` 环境中的敏感信息不会在日志中显示
- **访问控制**: 环境配置可以限制哪些分支能够访问敏感变量
- **审批流程**: 可以配置环境审批者，增加安全层级
- **API 密钥安全**: 密钥仅用于模型调用，不会被存储或传输到其他地方
- **结果安全**: 分析结果通过 GitHub Artifacts 安全存储和分发
- **最佳实践**: 建议定期轮换 API 密钥并监控使用情况

## 📚 更多资源

- [BioTools Agent 用户手册](../README.md)
- [项目配置说明](../pyproject.toml)
- [示例分析结果](../test_results/)

---

💡 **提示**: 首次使用建议先用一个简单的项目测试工作流配置是否正确！
