# GitHub Actions API 调用示例

## 概述

这里提供了如何通过其他项目或应用调用 BioTools Agent GitHub Actions 工作流的完整示例。

## JavaScript/Node.js 示例

### 单项目分析 API 调用

```javascript
// api/trigger-biotools.js
async function triggerBioToolsAnalysis(githubUrl, userMessage = '') {
  const response = await fetch('https://api.github.com/repos/YOUR_USERNAME/biotools_agent/actions/workflows/biotools-analysis.yml/dispatches', {
    method: 'POST',
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'Authorization': `token ${process.env.GITHUB_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ref: 'main',
      inputs: {
        github_url: githubUrl,
        analysis_name: `api-analysis-${Date.now()}`,
        user_message: userMessage,
        output_formats: 'html,md,json'
      }
    })
  });

  if (response.status === 204) {
    return { success: true, message: '工作流已成功触发' };
  } else {
    const error = await response.text();
    return { success: false, error };
  }
}

// 使用示例
async function example() {
  try {
    const result = await triggerBioToolsAnalysis(
      'https://github.com/c-zhou/yahs',
      '来自Web应用的分析请求'
    );
    
    if (result.success) {
      console.log('✅ 分析已启动');
    } else {
      console.error('❌ 启动失败:', result.error);
    }
  } catch (error) {
    console.error('网络错误:', error);
  }
}
```

### 批量分析 API 调用

```javascript
async function triggerBatchAnalysis(urlList, userMessage = '') {
  const csvContent = urlList.join('\\n');
  
  const response = await fetch('https://api.github.com/repos/YOUR_USERNAME/biotools_agent/actions/workflows/batch-analysis.yml/dispatches', {
    method: 'POST',
    headers: {
      'Accept': 'application/vnd.github.v3+json',
      'Authorization': `token ${process.env.GITHUB_TOKEN}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ref: 'main',
      inputs: {
        csv_content: csvContent,
        analysis_name: `batch-api-${Date.now()}`,
        user_message: userMessage
      }
    })
  });

  return response.status === 204;
}

// 使用示例
const urls = [
  'https://github.com/c-zhou/yahs',
  'https://github.com/CSU-KangHu/HiTE'
];

await triggerBatchAnalysis(urls, '批量分析请求 - 来自API');
```

## Next.js API Route 示例

```javascript
// pages/api/trigger-analysis.js 或 app/api/trigger-analysis/route.js

import { NextResponse } from 'next/server';

export async function POST(request) {
  try {
    const { githubUrl, message } = await request.json();
    
    // 验证输入
    if (!githubUrl || !githubUrl.startsWith('https://github.com/')) {
      return NextResponse.json(
        { error: '无效的GitHub URL' },
        { status: 400 }
      );
    }

    // 触发 GitHub Actions
    const response = await fetch(
      'https://api.github.com/repos/YOUR_USERNAME/biotools_agent/actions/workflows/biotools-analysis.yml/dispatches',
      {
        method: 'POST',
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'Authorization': `token ${process.env.GITHUB_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ref: 'main',
          inputs: {
            github_url: githubUrl,
            user_message: message || '来自Web界面',
            analysis_name: `web-analysis-${Date.now()}`,
            output_formats: 'html,md,json'
          }
        })
      }
    );

    if (response.status === 204) {
      return NextResponse.json({
        success: true,
        message: '分析已启动，请前往GitHub Actions查看进度'
      });
    } else {
      const errorText = await response.text();
      console.error('GitHub API 错误:', errorText);
      return NextResponse.json(
        { error: '启动分析失败' },
        { status: 500 }
      );
    }
  } catch (error) {
    console.error('API错误:', error);
    return NextResponse.json(
      { error: '服务器内部错误' },
      { status: 500 }
    );
  }
}
```

## Python 示例

```python
import requests
import os
import json
from datetime import datetime

def trigger_biotools_analysis(github_url, user_message=""):
    """触发生物信息学工具分析"""
    
    url = "https://api.github.com/repos/YOUR_USERNAME/biotools_agent/actions/workflows/biotools-analysis.yml/dispatches"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "ref": "main",
        "inputs": {
            "github_url": github_url,
            "user_message": user_message,
            "analysis_name": f"python-api-{int(datetime.now().timestamp())}",
            "output_formats": "html,md,json"
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 204:
        return {"success": True, "message": "工作流已触发"}
    else:
        return {"success": False, "error": response.text}

# 使用示例
if __name__ == "__main__":
    result = trigger_biotools_analysis(
        "https://github.com/c-zhou/yahs",
        "Python脚本调用测试"
    )
    
    if result["success"]:
        print("✅ 分析已启动")
    else:
        print(f"❌ 失败: {result['error']}")
```

## 前端 React 组件示例

```jsx
// components/AnalysisForm.jsx
import { useState } from 'react';

export default function AnalysisForm() {
  const [url, setUrl] = useState('');
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setResult(null);

    try {
      const response = await fetch('/api/trigger-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          githubUrl: url,
          message: message
        })
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({ error: '网络错误' });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">生物信息学工具分析</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">
            GitHub项目URL
          </label>
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/user/repo"
            className="w-full p-2 border rounded-md"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">
            消息 (可选)
          </label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="描述分析目的..."
            className="w-full p-2 border rounded-md"
            rows={3}
          />
        </div>
        
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 text-white p-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? '启动中...' : '开始分析'}
        </button>
      </form>

      {result && (
        <div className={`mt-4 p-3 rounded-md ${
          result.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {result.success ? '✅ ' + result.message : '❌ ' + result.error}
        </div>
      )}
    </div>
  );
}
```

## 环境变量配置

### .env.local (Next.js)
```bash
GITHUB_TOKEN=ghp_your_github_personal_access_token
```

### GitHub Token 权限要求

创建 GitHub Personal Access Token 时，需要以下权限：
- `repo` (如果仓库是私有的)
- `actions:write` (触发Actions工作流)

## 错误处理

### 常见错误和解决方案

1. **422 错误 - "Unexpected inputs provided"**
   - 确保工作流文件中定义了所有发送的input参数
   - 检查参数名称是否完全匹配

2. **401/403 错误 - 权限不足**
   - 检查GitHub Token是否有效
   - 确认Token具有必要的权限

3. **404错误 - 工作流不存在**
   - 确认仓库路径和工作流文件名正确
   - 检查工作流文件是否在main分支上

## 监控和结果获取

触发工作流后，可以通过以下方式监控进度和获取结果：

1. **GitHub Actions页面**: `https://github.com/YOUR_USERNAME/biotools_agent/actions`
2. **API查询运行状态**: 使用GitHub API查询workflow runs
3. **Webhook通知**: 配置GitHub Webhook接收完成通知

## 📊 获取执行结果

### 方法一：轮询状态检查

```javascript
// 触发分析并等待结果
async function analyzeAndWait(githubUrl, userMessage) {
  // 1. 触发工作流
  const triggerResponse = await fetch(
    'https://api.github.com/repos/YOUR_USERNAME/biotools_agent/actions/workflows/biotools-analysis.yml/dispatches',
    {
      method: 'POST',
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'Authorization': `token ${GITHUB_TOKEN}`,
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

  if (triggerResponse.status !== 204) {
    throw new Error('Failed to trigger workflow');
  }

  // 2. 等待并轮询状态
  const startTime = Date.now();
  const timeout = 300000; // 5分钟超时

  while (Date.now() - startTime < timeout) {
    await new Promise(resolve => setTimeout(resolve, 10000)); // 等待10秒

    // 获取最近的工作流运行
    const runsResponse = await fetch(
      'https://api.github.com/repos/YOUR_USERNAME/biotools_agent/actions/workflows/biotools-analysis.yml/runs?per_page=5',
      {
        headers: {
          'Accept': 'application/vnd.github.v3+json',
          'Authorization': `token ${GITHUB_TOKEN}`
        }
      }
    );

    const runsData = await runsResponse.json();
    
    // 查找匹配的运行（时间范围内的）
    const recentRun = runsData.workflow_runs.find(run => {
      const runTime = new Date(run.created_at);
      const timeDiff = runTime - new Date(startTime);
      return timeDiff > -60000 && timeDiff < 60000; // 1分钟内启动的
    });

    if (recentRun && recentRun.status === 'completed') {
      if (recentRun.conclusion === 'success') {
        // 3. 获取 artifacts
        const artifactsResponse = await fetch(
          `https://api.github.com/repos/YOUR_USERNAME/biotools_agent/actions/runs/${recentRun.id}/artifacts`,
          {
            headers: {
              'Accept': 'application/vnd.github.v3+json',
              'Authorization': `token ${GITHUB_TOKEN}`
            }
          }
        );

        const artifactsData = await artifactsResponse.json();

        return {
          success: true,
          run_id: recentRun.id,
          run_url: recentRun.html_url,
          status: recentRun.status,
          conclusion: recentRun.conclusion,
          artifacts: artifactsData.artifacts.map(artifact => ({
            name: artifact.name,
            download_url: `https://api.github.com/repos/YOUR_USERNAME/biotools_agent/actions/artifacts/${artifact.id}/zip`,
            size: artifact.size_in_bytes
          }))
        };
      } else {
        throw new Error(`Workflow failed: ${recentRun.conclusion}`);
      }
    }
  }

  throw new Error('Workflow timeout');
}

// 使用示例
try {
  const result = await analyzeAndWait(
    'https://github.com/c-zhou/yahs',
    '等待结果的API调用'
  );
  
  console.log('分析完成:', result);
  console.log('下载 artifacts:', result.artifacts);
} catch (error) {
  console.error('分析失败:', error);
}
```

### 方法二：Webhook 通知

```javascript
// 设置 webhook 处理器
app.post('/webhook/github-actions', (req, res) => {
  const payload = req.body;
  
  // 检查是否是工作流完成事件
  if (payload.action === 'completed' && payload.workflow_run) {
    const run = payload.workflow_run;
    
    // 检查是否是我们的分析工作流
    if (run.name === 'BioTools Analysis') {
      console.log('收到工作流完成通知:', {
        conclusion: run.conclusion,
        run_id: run.id,
        url: run.html_url
      });
      
      if (run.conclusion === 'success') {
        // 处理成功的分析结果
        handleAnalysisSuccess(run);
      } else {
        // 处理失败情况
        handleAnalysisFailure(run);
      }
    }
  }
  
  res.status(200).send('OK');
});

async function handleAnalysisSuccess(run) {
  // 获取 artifacts
  const artifacts = await getWorkflowArtifacts(run.id);
  
  // 通知用户或更新数据库
  await notifyUser({
    message: '生物信息学工具分析完成',
    results_url: run.html_url,
    download_links: artifacts
  });
}
```

## 🔄 完整的集成示例

### React Hook 示例

```jsx
// hooks/useBioToolsAnalysis.js
import { useState, useCallback } from 'react';

export function useBioToolsAnalysis() {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const triggerAnalysis = useCallback(async (githubUrl, message) => {
    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      // 1. 触发分析
      const response = await fetch('/api/trigger-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ githubUrl, message })
      });

      if (!response.ok) {
        throw new Error('Failed to trigger analysis');
      }

      // 2. 开始轮询状态
      const pollResult = await pollForResults(githubUrl, message);
      setResult(pollResult);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const pollForResults = async (githubUrl, message) => {
    const startTime = Date.now();
    const timeout = 300000; // 5分钟

    while (Date.now() - startTime < timeout) {
      await new Promise(resolve => setTimeout(resolve, 15000)); // 15秒检查一次

      try {
        const statusResponse = await fetch(
          `/api/check-analysis-status?url=${encodeURIComponent(githubUrl)}&message=${encodeURIComponent(message)}`
        );
        
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          
          if (statusData.completed) {
            return statusData;
          }
        }
      } catch (pollError) {
        console.warn('轮询错误:', pollError);
      }
    }

    throw new Error('分析超时');
  };

  return {
    isAnalyzing,
    result,
    error,
    triggerAnalysis
  };
}

// 使用组件
function AnalysisComponent() {
  const { isAnalyzing, result, error, triggerAnalysis } = useBioToolsAnalysis();

  const handleSubmit = async (url, message) => {
    await triggerAnalysis(url, message);
  };

  return (
    <div>
      {isAnalyzing && (
        <div className="loading">
          <p>正在分析中，请稍候...</p>
          <div className="progress-bar">
            <div className="progress-fill"></div>
          </div>
        </div>
      )}

      {result && (
        <div className="result-success">
          <h3>✅ 分析完成</h3>
          <p>运行ID: {result.run_id}</p>
          <p>项目: {result.project_name}</p>
          <div className="download-links">
            <h4>下载结果:</h4>
            {result.artifacts.map(artifact => (
              <a 
                key={artifact.name}
                href={artifact.download_url}
                className="download-link"
              >
                📄 {artifact.name} ({(artifact.size / 1024).toFixed(1)}KB)
              </a>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="result-error">
          <h3>❌ 分析失败</h3>
          <p>{error}</p>
        </div>
      )}
    </div>
  );
}
```

---

💡 **提示**: 
- 将 `YOUR_USERNAME` 替换为实际的GitHub用户名
- 确保环境变量中配置了有效的GitHub Token
- 工作流运行结果会保存在GitHub Artifacts中，有效期30天
- 详细的结果获取方法请参考 [结果反馈机制文档](./RESULT_FEEDBACK.md)
