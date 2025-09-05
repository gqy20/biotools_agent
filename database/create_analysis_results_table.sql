-- SQL 语句：创建 bio_analysis_results 表
-- 文件路径: database/create_analysis_results_table.sql

CREATE TABLE IF NOT EXISTS bio_analysis_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    analysis_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    repo_url TEXT UNIQUE NOT NULL,
    data JSONB NOT NULL
);

-- 可选：为 repo_url 创建索引以提高查询速度
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
