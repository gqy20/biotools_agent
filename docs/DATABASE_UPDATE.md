# 数据库更新说明

为了支持每次测试都有不同的项目ID，我们需要更新数据库表结构。

## 更新步骤

1. 登录到Supabase控制台
2. 进入SQL Editor
3. 执行以下SQL脚本:

```sql
-- SQL 语句：创建 bio_analysis_results 表

CREATE TABLE IF NOT EXISTS bio_analysis_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    test_id UUID DEFAULT gen_random_uuid() NOT NULL,
    analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    repo_url TEXT NOT NULL,
    data JSONB NOT NULL
);

-- 为 test_id 创建索引以提高查询速度
CREATE INDEX IF NOT EXISTS idx_analysis_results_test_id ON bio_analysis_results (test_id);

-- 为 repo_url 创建索引以提高查询速度
CREATE INDEX IF NOT EXISTS idx_analysis_results_repo_url ON bio_analysis_results (repo_url);

-- 启用行级安全策略 (RLS)
ALTER TABLE bio_analysis_results ENABLE ROW LEVEL SECURITY;

-- 创建策略允许服务角色对表进行所有操作
-- 注意：这需要在 Supabase SQL Editor 中以管理员身份执行
-- 允许 service_role 用户 SELECT, INSERT, UPDATE, DELETE
CREATE POLICY "Allow service role full access" ON bio_analysis_results
FOR ALL TO service_role USING (true) WITH CHECK (true);

-- 授予服务角色对表的权限
GRANT ALL PRIVILEGES ON TABLE bio_analysis_results TO service_role;
```

4. 应用更改后，每次测试将生成唯一的test_id，允许对同一项目进行多次测试并保存所有结果。