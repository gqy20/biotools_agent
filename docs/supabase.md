# Supabase 数据库使用指南

本文档详细说明了如何在 BioTools Agent 项目中使用 Supabase 数据库，以及如何在其他项目中调用数据库中的结果信息。

## 1. 客户端初始化

Supabase Python 客户端通过 `create_client` 方法初始化，需要提供两个参数：

1. `supabase_url`: 项目的 URL，格式为 `https://<project-id>.supabase.co`
2. `supabase_key`: 访问密钥，可以是：
   - anon key：用于客户端应用（有限权限）
   - service role key：用于服务器端（完全权限）

```python
from supabase import create_client

# 初始化客户端
client = create_client("https://your-project-id.supabase.co", "your-service-role-key")
```

## 2. BioTools Agent 数据库结构

### 2.1 表结构

BioTools Agent 使用 `bio_analysis_results` 表来存储分析结果：

```sql
CREATE TABLE IF NOT EXISTS bio_analysis_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    repo_url TEXT UNIQUE NOT NULL,
    data JSONB NOT NULL
);
```

字段说明：
- `id`: UUID，主键，自动生成
- `analysis_timestamp`: TIMESTAMPTZ，分析时间戳，默认为当前时间
- `repo_url`: TEXT，仓库 URL，唯一，用于标识分析的项目
- `data`: JSONB，完整的分析数据，包含项目信息、作者信息、功能信息等

### 2.2 数据结构

`data` 字段包含完整的分析结果，结构如下：

```json
{
  "repository": {
    "name": "项目名称",
    "url": "项目URL",
    "description": "项目描述",
    "language": "主要编程语言",
    "stars": 100,
    "forks": 50,
    "license": "许可证"
  },
  "authors": [
    {
      "name": "作者姓名",
      "email": "作者邮箱"
    }
  ],
  "publications": [
    {
      "title": "文章标题",
      "authors": ["作者1", "作者2"],
      "journal": "期刊名称",
      "year": 2023,
      "doi": "DOI",
      "pmid": "PubMed ID"
    }
  ],
  "functionality": {
    "main_purpose": "主要用途",
    "key_features": ["功能1", "功能2"],
    "input_formats": ["输入格式1", "输入格式2"],
    "output_formats": ["输出格式1", "输出格式2"],
    "dependencies": ["依赖1", "依赖2"]
  },
  "usage": {
    "installation": "安装方法",
    "basic_usage": "基本用法",
    "examples": ["示例1", "示例2"],
    "parameters": ["参数说明1", "参数说明2"]
  },
  "analysis_timestamp": "分析时间戳"
}
```

## 3. 数据查询方法

### 3.1 查询所有记录

```python
# 查询所有分析结果
result = client.table('bio_analysis_results').select('*').execute()
for record in result.data:
    print(f"项目: {record['data']['repository']['name']}")
    print(f"URL: {record['repo_url']}")
    print(f"分析时间: {record['analysis_timestamp']}")
```

### 3.2 按项目URL查询

```python
# 查询特定项目的分析结果
repo_url = "https://github.com/user/repo"
result = client.table('bio_analysis_results').select('*').eq('repo_url', repo_url).execute()
if result.data:
    record = result.data[0]
    print(f"项目信息: {record['data']['repository']}")
    print(f"核心功能: {record['data']['functionality']['key_features']}")
```

### 3.3 按时间范围查询

```python
# 查询最近一周的分析结果
from datetime import datetime, timedelta

one_week_ago = (datetime.now() - timedelta(weeks=1)).isoformat()
result = client.table('bio_analysis_results').select('*').gte('analysis_timestamp', one_week_ago).execute()
print(f"最近一周分析了 {len(result.data)} 个项目")
```

### 3.4 查询特定语言的项目

```python
# 查询Python项目的分析结果
result = client.table('bio_analysis_results').select('*').contains('data->repository->>language', 'Python').execute()
for record in result.data:
    project_name = record['data']['repository']['name']
    print(f"Python项目: {project_name}")
```

### 3.5 查询具有特定功能的项目

```python
# 查询包含特定功能的项目
result = client.table('bio_analysis_results').select('*').contains('data->functionality->key_features', '数据分析').execute()
for record in result.data:
    project_name = record['data']['repository']['name']
    features = record['data']['functionality']['key_features']
    print(f"项目 {project_name} 的功能: {features}")
```

## 4. 高级查询方法

### 4.1 聚合查询

```python
# 统计分析项目的总数
result = client.table('bio_analysis_results').select('*', count="exact").execute()
total_count = result.count
print(f"总共分析了 {total_count} 个项目")

# 统计各编程语言的项目数量
result = client.table('bio_analysis_results').select('data->repository->>language', count="exact").group('data->repository->>language').execute()
for item in result.data:
    language = item['data->repository->>language']
    count = item['count']
    print(f"{language}: {count} 个项目")
```

### 4.2 排序和限制结果

```python
# 按星星数排序，获取前10个最受欢迎的项目
result = client.table('bio_analysis_results').select('*').order('data->repository->>stars', desc=True).limit(10).execute()
for record in result.data:
    project_name = record['data']['repository']['name']
    stars = record['data']['repository']['stars']
    print(f"{project_name}: {stars} 颗星")
```

## 5. 在其他项目中使用分析结果

### 5.1 创建一个简单的分析结果查看器

```python
from supabase import create_client
import json

class BioToolsResultViewer:
    def __init__(self, supabase_url, supabase_key):
        self.client = create_client(supabase_url, supabase_key)
    
    def get_all_projects(self):
        """获取所有分析的项目"""
        result = self.client.table('bio_analysis_results').select('data->repository->name, data->repository->url, data->repository->stars').execute()
        return result.data
    
    def get_project_details(self, repo_url):
        """获取特定项目的详细信息"""
        result = self.client.table('bio_analysis_results').select('*').eq('repo_url', repo_url).execute()
        if result.data:
            return result.data[0]['data']
        return None
    
    def search_projects_by_language(self, language):
        """按编程语言搜索项目"""
        result = self.client.table('bio_analysis_results').select('*').contains('data->repository->>language', language).execute()
        return [record['data'] for record in result.data]
    
    def get_recent_analyses(self, days=7):
        """获取最近分析的项目"""
        from datetime import datetime, timedelta
        since = (datetime.now() - timedelta(days=days)).isoformat()
        result = self.client.table('bio_analysis_results').select('*').gte('analysis_timestamp', since).execute()
        return [record['data'] for record in result.data]

# 使用示例
viewer = BioToolsResultViewer("https://your-project-id.supabase.co", "your-service-role-key")

# 查看所有项目
projects = viewer.get_all_projects()
for project in projects:
    print(f"项目: {project['data->repository->name']}, URL: {project['data->repository->url']}, 星星: {project['data->repository->stars']}")

# 查看特定项目详情
details = viewer.get_project_details("https://github.com/user/repo")
if details:
    print(json.dumps(details, indent=2, ensure_ascii=False))
```

### 5.2 创建一个项目比较工具

```python
class BioToolsComparator:
    def __init__(self, supabase_url, supabase_key):
        self.client = create_client(supabase_url, supabase_key)
    
    def compare_projects(self, repo_urls):
        """比较多个项目的功能"""
        results = []
        for url in repo_urls:
            result = self.client.table('bio_analysis_results').select('data').eq('repo_url', url).execute()
            if result.data:
                results.append(result.data[0]['data'])
        
        # 比较核心功能
        for i, data in enumerate(results):
            print(f"\n项目 {i+1}: {data['repository']['name']}")
            print("核心功能:")
            for feature in data['functionality']['key_features']:
                print(f"  - {feature}")
        
        return results

# 使用示例
comparator = BioToolsComparator("https://your-project-id.supabase.co", "your-service-role-key")
repo_urls = [
    "https://github.com/user/repo1",
    "https://github.com/user/repo2"
]
comparator.compare_projects(repo_urls)
```

## 6. 错误处理和最佳实践

### 6.1 错误处理

```python
try:
    result = client.table('bio_analysis_results').select('*').execute()
    if result.error:
        print(f"数据库错误: {result.error.message}")
    else:
        # 处理数据
        for record in result.data:
            # 处理每条记录
            pass
except Exception as e:
    print(f"请求异常: {e}")
```

### 6.2 最佳实践

1. **使用服务角色密钥**：在服务器端操作时使用服务角色密钥，确保有足够的权限。
2. **合理使用索引**：`repo_url` 字段已建立索引，对于频繁查询的字段可考虑建立更多索引。
3. **分页查询**：对于大量数据的查询，使用 `limit` 和 `offset` 进行分页。
4. **连接复用**：在应用中复用 Supabase 客户端实例，避免重复创建连接。

## 7. 安全注意事项

1. **密钥保护**：服务角色密钥具有完全访问权限，必须严格保护，不要在客户端代码中使用。
2. **环境变量**：将 Supabase 配置存储在环境变量中，不要硬编码在代码里。
3. **RLS 策略**：在生产环境中考虑使用行级安全策略来控制数据访问权限。

通过以上方法，您可以在其他项目中轻松地查询和使用 BioTools Agent 生成的分析结果。