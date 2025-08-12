# GitHub Actions 结果反馈机制

## 概述

GitHub Actions 本身是异步执行的，无法在 API 调用时直接返回分析结果。但我们提供了多种方式来获取工作流的执行状态和最终结果。

## 🔍 1. 状态查询 API

### 获取工作流运行状态

```javascript
// 获取最近的工作流运行状态
async function getWorkflowRuns(owner, repo, workflowId) {
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/actions/workflows/${workflowId}/runs?per_page=10`,
    {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `token ${GITHUB_TOKEN}`
      }
    }
  );
  
  const data = await response.json();
  return data.workflow_runs;
}

// 获取特定运行的详细信息
async function getWorkflowRunDetails(owner, repo, runId) {
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/actions/runs/${runId}`,
    {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `token ${GITHUB_TOKEN}`
      }
    }
  );
  
  return await response.json();
}

// 使用示例
const runs = await getWorkflowRuns('username', 'biotools_agent', 'biotools-analysis.yml');
const latestRun = runs[0];

console.log('状态:', latestRun.status); // queued, in_progress, completed
console.log('结论:', latestRun.conclusion); // success, failure, cancelled
console.log('开始时间:', latestRun.created_at);
console.log('完成时间:', latestRun.updated_at);
```

### 工作流状态说明

| 状态 | 说明 |
|------|------|
| `queued` | 已排队等待执行 |
| `in_progress` | 正在执行中 |
| `completed` | 已完成 |

| 结论 | 说明 |
|------|------|
| `success` | 成功完成 |
| `failure` | 执行失败 |
| `cancelled` | 被取消 |
| `neutral` | 中性结果 |

## 📥 2. Artifacts 下载

### 获取 Artifacts 列表

```javascript
async function getWorkflowArtifacts(owner, repo, runId) {
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/actions/runs/${runId}/artifacts`,
    {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `token ${GITHUB_TOKEN}`
      }
    }
  );
  
  const data = await response.json();
  return data.artifacts;
}

// 下载特定的 Artifact
async function downloadArtifact(owner, repo, artifactId) {
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/actions/artifacts/${artifactId}/zip`,
    {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `token ${GITHUB_TOKEN}`
      }
    }
  );
  
  // 返回下载链接（重定向URL）
  return response.url;
}
```

## 🔔 3. Webhook 通知

### 设置 Repository Webhook

1. 前往仓库的 `Settings` → `Webhooks`
2. 点击 `Add webhook`
3. 配置 Webhook：

```json
{
  "payload_url": "https://your-api.com/webhook/github",
  "content_type": "application/json",
  "events": ["workflow_run"],
  "active": true
}
```

### Webhook 处理示例

```javascript
// Express.js webhook 处理器
app.post('/webhook/github', (req, res) => {
  const payload = req.body;
  
  if (payload.action === 'completed' && payload.workflow_run) {
    const run = payload.workflow_run;
    
    // 检查是否是我们关心的工作流
    if (run.name === 'BioTools Analysis' || run.name === 'Batch BioTools Analysis') {
      console.log('工作流完成:', {
        name: run.name,
        status: run.status,
        conclusion: run.conclusion,
        run_id: run.id,
        url: run.html_url,
        created_at: run.created_at,
        updated_at: run.updated_at
      });
      
      // 如果成功完成，获取 artifacts
      if (run.conclusion === 'success') {
        handleSuccessfulRun(run);
      } else {
        handleFailedRun(run);
      }
    }
  }
  
  res.status(200).send('OK');
});

async function handleSuccessfulRun(run) {
  // 获取并处理分析结果
  const artifacts = await getWorkflowArtifacts(
    run.repository.owner.login,
    run.repository.name,
    run.id
  );
  
  console.log('可用的结果文件:', artifacts.map(a => a.name));
  
  // 通知用户或更新数据库
  await notifyUser({
    message: '分析完成',
    run_url: run.html_url,
    artifacts: artifacts
  });
}
```

## 🔄 4. 轮询状态检查

### 完整的轮询示例

```javascript
class BioToolsAnalyzer {
  constructor(owner, repo, token) {
    this.owner = owner;
    this.repo = repo;
    this.token = token;
    this.baseUrl = 'https://api.github.com';
  }

  // 触发分析
  async triggerAnalysis(githubUrl, userMessage = '') {
    const response = await fetch(
      `${this.baseUrl}/repos/${this.owner}/${this.repo}/actions/workflows/biotools-analysis.yml/dispatches`,
      {
        method: 'POST',
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'Authorization': `token ${this.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ref: 'main',
          inputs: {
            github_url: githubUrl,
            user_message: userMessage,
            analysis_name: `api-${Date.now()}`
          }
        })
      }
    );

    if (response.status === 204) {
      // 等待一会儿再开始轮询
      await new Promise(resolve => setTimeout(resolve, 5000));
      return this.waitForCompletion(userMessage);
    } else {
      throw new Error(`Failed to trigger workflow: ${response.status}`);
    }
  }

  // 等待完成
  async waitForCompletion(userMessage, maxWaitTime = 300000) { // 5分钟超时
    const startTime = Date.now();
    const pollInterval = 10000; // 10秒检查一次

    while (Date.now() - startTime < maxWaitTime) {
      try {
        const runs = await this.getRecentRuns();
        
        // 查找匹配的运行（通过用户消息或时间戳）
        const matchingRun = runs.find(run => {
          const timeDiff = new Date(run.created_at) - new Date(startTime);
          return timeDiff > -60000 && timeDiff < 60000; // 1分钟内启动的
        });

        if (matchingRun) {
          if (matchingRun.status === 'completed') {
            if (matchingRun.conclusion === 'success') {
              return await this.getRunResults(matchingRun);
            } else {
              throw new Error(`Workflow failed: ${matchingRun.conclusion}`);
            }
          } else {
            console.log(`工作流状态: ${matchingRun.status}`);
          }
        }

        await new Promise(resolve => setTimeout(resolve, pollInterval));
      } catch (error) {
        console.error('轮询错误:', error);
        await new Promise(resolve => setTimeout(resolve, pollInterval));
      }
    }

    throw new Error('Workflow timeout');
  }

  // 获取最近的运行
  async getRecentRuns() {
    const response = await fetch(
      `${this.baseUrl}/repos/${this.owner}/${this.repo}/actions/workflows/biotools-analysis.yml/runs?per_page=10`,
      {
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'Authorization': `token ${this.token}`
        }
      }
    );

    const data = await response.json();
    return data.workflow_runs;
  }

  // 获取运行结果
  async getRunResults(run) {
    const artifacts = await this.getWorkflowArtifacts(run.id);
    
    return {
      success: true,
      run_id: run.id,
      run_url: run.html_url,
      status: run.status,
      conclusion: run.conclusion,
      created_at: run.created_at,
      updated_at: run.updated_at,
      artifacts: artifacts.map(artifact => ({
        id: artifact.id,
        name: artifact.name,
        size_in_bytes: artifact.size_in_bytes,
        download_url: `${this.baseUrl}/repos/${this.owner}/${this.repo}/actions/artifacts/${artifact.id}/zip`
      }))
    };
  }

  // 获取工作流 artifacts
  async getWorkflowArtifacts(runId) {
    const response = await fetch(
      `${this.baseUrl}/repos/${this.owner}/${this.repo}/actions/runs/${runId}/artifacts`,
      {
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'Authorization': `token ${this.token}`
        }
      }
    );

    const data = await response.json();
    return data.artifacts;
  }
}

// 使用示例
const analyzer = new BioToolsAnalyzer('username', 'biotools_agent', 'your_token');

try {
  const result = await analyzer.triggerAnalysis(
    'https://github.com/c-zhou/yahs',
    '来自API的分析请求'
  );
  
  console.log('分析完成:', result);
  console.log('下载链接:', result.artifacts);
} catch (error) {
  console.error('分析失败:', error);
}
```

## 📊 5. 结果数据结构

### 单项目分析结果

```json
{
  "success": true,
  "run_id": "1234567890",
  "run_url": "https://github.com/user/biotools_agent/actions/runs/1234567890",
  "artifacts_url": "https://github.com/user/biotools_agent/actions/runs/1234567890",
  "analysis_time": "2024-01-15 10:30:00 UTC",
  "project_url": "https://github.com/c-zhou/yahs",
  "project_name": "yahs",
  "user_message": "API调用测试",
  "task_name": "api-analysis",
  "output_formats": "html,md,json",
  "generated_files": [
    "yahs_analysis.html",
    "yahs_analysis.md", 
    "yahs_analysis.json"
  ]
}
```

### 批量分析结果

```json
{
  "success": true,
  "run_id": "1234567891",
  "run_url": "https://github.com/user/biotools_agent/actions/runs/1234567891",
  "total_count": 5,
  "success_count": 4,
  "success_rate": 80,
  "failed_projects": [
    "https://github.com/failed/project"
  ]
}
```

## ⚠️ 注意事项

### API 限制
- GitHub API 有速率限制：
  - 认证用户：5000次/小时
  - 未认证：60次/小时
- 建议使用 webhook 而不是频繁轮询

### 权限要求
- 读取工作流状态：需要 `actions:read` 权限
- 下载 artifacts：需要 `actions:read` 权限
- 如果仓库是私有的，还需要 `repo` 权限

### 最佳实践
1. **使用 Webhook**：避免频繁轮询，提高效率
2. **设置超时**：避免无限等待
3. **错误处理**：妥善处理网络错误和API错误
4. **缓存结果**：避免重复查询相同的运行结果
5. **监控配额**：关注API使用情况，避免超限

## 🔧 调试技巧

### 查看工作流日志

```javascript
async function getWorkflowLogs(owner, repo, runId) {
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/actions/runs/${runId}/logs`,
    {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `token ${GITHUB_TOKEN}`
      }
    }
  );
  
  // 返回日志的下载链接
  return response.url;
}
```

### 获取作业详情

```javascript
async function getWorkflowJobs(owner, repo, runId) {
  const response = await fetch(
    `https://api.github.com/repos/${owner}/${repo}/actions/runs/${runId}/jobs`,
    {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `token ${GITHUB_TOKEN}`
      }
    }
  );
  
  const data = await response.json();
  return data.jobs;
}
```

---

通过这些方法，您可以完整地追踪和获取 GitHub Actions 工作流的执行结果！
