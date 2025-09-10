"""可视化文档生成器"""

import json
from pathlib import Path
from typing import Dict

from jinja2 import Template

from .models import BioToolAnalysis


class DocumentVisualizer:
    """文档可视化生成器"""

    def __init__(self, output_dir: str = "docs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def generate_html_report(self, analysis: BioToolAnalysis) -> Path:
        """生成HTML格式的分析报告"""

        # HTML模板
        html_template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ analysis.repository.name }} - 生物信息学工具分析报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f8f9fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 4px solid #667eea;
        }
        
        .card h2 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .info-item {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }
        
        .info-item strong {
            color: #2c3e50;
            display: block;
            margin-bottom: 5px;
        }
        
        .tag {
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            margin: 2px;
        }
        
        .feature-list {
            list-style: none;
        }
        
        .feature-list li {
            background: #f1f8e9;
            margin: 8px 0;
            padding: 12px;
            border-radius: 6px;
            border-left: 3px solid #4caf50;
        }
        
        .feature-list li::before {
            content: "✓";
            color: #4caf50;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .code-block {
            background: #263238;
            color: #fff;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Monaco', 'Consolas', monospace;
            margin: 15px 0;
        }
        
        .publication {
            background: #fff3e0;
            border: 1px solid #ffcc02;
            padding: 20px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .publication h3 {
            color: #e65100;
            margin-bottom: 10px;
        }
        
        .meta-info {
            font-size: 0.9em;
            color: #666;
            margin-top: 20px;
            text-align: center;
            padding: 15px;
            background: #f5f5f5;
            border-radius: 8px;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            text-align: center;
            margin: 20px 0;
        }
        
        .stat-item {
            flex: 1;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            display: block;
        }
        
        .stat-label {
            color: #666;
            font-size: 0.9em;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .card {
                padding: 20px;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>{{ analysis.repository.name }}</h1>
            <p>{{ analysis.repository.description or "生物信息学工具分析报告" }}</p>
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{{ analysis.repository.stars }}</span>
                    <span class="stat-label">Stars</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{{ analysis.repository.forks }}</span>
                    <span class="stat-label">Forks</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{{ analysis.authors|length }}</span>
                    <span class="stat-label">作者</span>
                </div>
            </div>
        </div>

        <!-- 基础信息 -->
        <div class="card">
            <h2>📊 基础信息</h2>
            <div class="info-grid">
                <div class="info-item">
                    <strong>项目名称</strong>
                    {{ analysis.repository.name }}
                </div>
                <div class="info-item">
                    <strong>项目地址</strong>
                    <a href="{{ analysis.repository.url }}" target="_blank">{{ analysis.repository.url }}</a>
                </div>
                <div class="info-item">
                    <strong>主要语言</strong>
                    {{ analysis.repository.language or "未知" }}
                </div>
                <div class="info-item">
                    <strong>许可证</strong>
                    {{ analysis.repository.license or "未指定" }}
                </div>
            </div>
        </div>

        <!-- 作者信息 -->
        <div class="card">
            <h2>👥 作者信息</h2>
            {% if analysis.authors %}
                <div class="info-grid">
                    {% for author in analysis.authors %}
                    <div class="info-item">
                        <strong>{{ author.name }}</strong>
                        {% if author.email %}
                            <br><small>{{ author.email }}</small>
                        {% endif %}
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <p>暂无作者信息</p>
            {% endif %}
        </div>

        <!-- 相关发表文章 -->
        <div class="card">
            <h2>📚 相关发表文章</h2>
            {% if analysis.publications %}
                {% for pub in analysis.publications %}
                <div class="publication">
                    <h3>{{ pub.title }}</h3>
                    <p><strong>作者:</strong> {{ pub.authors|join(", ") }}</p>
                    {% if pub.journal %}
                        <p><strong>期刊:</strong> {{ pub.journal }}</p>
                    {% endif %}
                    {% if pub.year %}
                        <p><strong>年份:</strong> {{ pub.year }}</p>
                    {% endif %}
                    {% if pub.doi %}
                        <p><strong>DOI:</strong> <a href="https://doi.org/{{ pub.doi }}" target="_blank">{{ pub.doi }}</a></p>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <p>暂无相关发表文章信息</p>
            {% endif %}
        </div>

        <!-- 功能特性 -->
        <div class="card">
            <h2>🔧 功能特性</h2>
            <div class="info-item">
                <strong>主要用途</strong>
                {{ analysis.functionality.main_purpose }}
            </div>
            
            {% if analysis.functionality.key_features %}
            <h3 style="margin-top: 25px; margin-bottom: 15px;">核心功能</h3>
            <ul class="feature-list">
                {% for feature in analysis.functionality.key_features %}
                <li>{{ feature }}</li>
                {% endfor %}
            </ul>
            {% endif %}

            <div class="info-grid" style="margin-top: 25px;">
                <div class="info-item">
                    <strong>输入格式</strong>
                    {% for format in analysis.functionality.input_formats %}
                        <span class="tag">{{ format }}</span>
                    {% endfor %}
                </div>
                <div class="info-item">
                    <strong>输出格式</strong>
                    {% for format in analysis.functionality.output_formats %}
                        <span class="tag">{{ format }}</span>
                    {% endfor %}
                </div>
            </div>

            {% if analysis.functionality.dependencies %}
            <div class="info-item" style="margin-top: 20px;">
                <strong>主要依赖</strong>
                {% for dep in analysis.functionality.dependencies %}
                    <span class="tag">{{ dep }}</span>
                {% endfor %}
            </div>
            {% endif %}
        </div>

        <!-- 项目架构 -->
        {% if analysis.architecture %}
        <div class="card">
            <h2>🏗️ 项目架构</h2>
            
            {% if analysis.architecture.programming_languages %}
            <div class="info-item">
                <strong>编程语言</strong>
                {% for lang in analysis.architecture.programming_languages %}
                    <span class="tag">{{ lang }}</span>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if analysis.architecture.frameworks %}
            <div class="info-item" style="margin-top: 20px;">
                <strong>框架/库</strong>
                {% for framework in analysis.architecture.frameworks %}
                    <span class="tag">{{ framework }}</span>
                {% endfor %}
            </div>
            {% endif %}
            
            {% if analysis.architecture.entry_points %}
            <div class="info-item" style="margin-top: 20px;">
                <strong>入口点</strong>
                <ul class="feature-list">
                    {% for entry in analysis.architecture.entry_points %}
                    <li>{{ entry }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
            
            {% if analysis.architecture.directory_structure %}
            <h3 style="margin-top: 25px; margin-bottom: 15px;">目录结构</h3>
            <div class="info-grid">
                {% for path, purpose in analysis.architecture.directory_structure.items() %}
                <div class="info-item">
                    <strong>{{ path }}</strong>
                    {{ purpose }}
                </div>
                {% endfor %}
            </div>
            {% endif %}
        </div>
        {% endif %}

        <!-- 代码质量 -->
        {% if analysis.code_quality %}
        <div class="card">
            <h2>💻 代码质量</h2>
            
            <div class="info-grid">
                <div class="info-item">
                    <strong>代码结构</strong>
                    {{ analysis.code_quality.code_structure }}
                </div>
                <div class="info-item">
                    <strong>文档质量</strong>
                    {{ analysis.code_quality.documentation_quality }}
                </div>
                <div class="info-item">
                    <strong>测试覆盖度</strong>
                    {{ analysis.code_quality.test_coverage }}
                </div>
                <div class="info-item">
                    <strong>代码风格</strong>
                    {{ analysis.code_quality.code_style }}
                </div>
            </div>
            
            {% if analysis.code_quality.best_practices %}
            <h3 style="margin-top: 25px; margin-bottom: 15px;">最佳实践</h3>
            <ul class="feature-list">
                {% for practice in analysis.code_quality.best_practices %}
                <li>{{ practice }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endif %}

        <!-- 性能特征 -->
        {% if analysis.performance %}
        <div class="card">
            <h2>⚡ 性能特征</h2>
            
            <div class="info-grid">
                <div class="info-item">
                    <strong>时间复杂度</strong>
                    {{ analysis.performance.time_complexity }}
                </div>
                <div class="info-item">
                    <strong>空间复杂度</strong>
                    {{ analysis.performance.space_complexity }}
                </div>
                <div class="info-item">
                    <strong>并行化支持</strong>
                    {{ analysis.performance.parallelization }}
                </div>
                <div class="info-item">
                    <strong>资源使用</strong>
                    {{ analysis.performance.resource_usage }}
                </div>
            </div>
            
            {% if analysis.performance.optimization_suggestions %}
            <h3 style="margin-top: 25px; margin-bottom: 15px;">优化建议</h3>
            <ul class="feature-list">
                {% for suggestion in analysis.performance.optimization_suggestions %}
                <li>{{ suggestion }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endif %}

        <!-- 生物信息学专业性 -->
        {% if analysis.bioinformatics_expertise %}
        <div class="card">
            <h2>🧬 生物信息学专业性</h2>
            
            <div class="info-grid">
                <div class="info-item">
                    <strong>算法准确性</strong>
                    {{ analysis.bioinformatics_expertise.algorithm_accuracy }}
                </div>
                <div class="info-item">
                    <strong>基准测试结果</strong>
                    {{ analysis.bioinformatics_expertise.benchmark_results }}
                </div>
                <div class="info-item">
                    <strong>工具比较</strong>
                    {{ analysis.bioinformatics_expertise.tool_comparison }}
                </div>
            </div>
            
            {% if analysis.bioinformatics_expertise.applicable_scenarios %}
            <h3 style="margin-top: 25px; margin-bottom: 15px;">适用场景</h3>
            <ul class="feature-list">
                {% for scenario in analysis.bioinformatics_expertise.applicable_scenarios %}
                <li>{{ scenario }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>
        {% endif %}

        <!-- 可用性 -->
        {% if analysis.usability %}
        <div class="card">
            <h2>👋 可用性</h2>
            
            <div class="info-grid">
                <div class="info-item">
                    <strong>文档完整性</strong>
                    {{ analysis.usability.documentation_completeness }}
                </div>
                <div class="info-item">
                    <strong>用户界面</strong>
                    {{ analysis.usability.user_interface }}
                </div>
                <div class="info-item">
                    <strong>错误处理</strong>
                    {{ analysis.usability.error_handling }}
                </div>
                <div class="info-item">
                    <strong>学习曲线</strong>
                    {{ analysis.usability.learning_curve }}
                </div>
            </div>
        </div>
        {% endif %}

        <!-- 安全风险分析 -->
        {% if analysis.security %}
        <div class="card">
            <h2>🔒 安全风险分析</h2>
            
            <div class="info-grid">
                <div class="info-item">
                    <strong>高风险漏洞</strong>
                    <span style="color: #d32f2f; font-size: 1.5em; font-weight: bold;">{{ analysis.security.total_high_risk }}</span>
                </div>
                <div class="info-item">
                    <strong>中风险漏洞</strong>
                    <span style="color: #f57c00; font-size: 1.5em; font-weight: bold;">{{ analysis.security.total_medium_risk }}</span>
                </div>
                <div class="info-item">
                    <strong>低风险漏洞</strong>
                    <span style="color: #388e3c; font-size: 1.5em; font-weight: bold;">{{ analysis.security.total_low_risk }}</span>
                </div>
                <div class="info-item">
                    <strong>扫描工具</strong>
                    {% for tool in analysis.security.scan_tools_used %}
                        <span class="tag">{{ tool }}</span>
                    {% endfor %}
                </div>
            </div>
            
            {% if analysis.security.vulnerabilities %}
            <h3 style="margin-top: 25px; margin-bottom: 15px;">发现的安全问题</h3>
            
            {% set high_vulns = analysis.security.vulnerabilities | selectattr("severity", "equalto", "HIGH") | list %}
            {% set medium_vulns = analysis.security.vulnerabilities | selectattr("severity", "equalto", "MEDIUM") | list %}  
            {% set low_vulns = analysis.security.vulnerabilities | selectattr("severity", "equalto", "LOW") | list %}
            
            {% if high_vulns %}
            <h4 style="color: #d32f2f; margin: 15px 0 10px;">🔴 高风险漏洞 ({{ high_vulns | length }})</h4>
            {% for vuln in high_vulns[:5] %}
            <div class="info-item" style="margin-bottom: 15px; border-left-color: #d32f2f; background: #ffebee;">
                <strong>{{ vuln.id }} <span style="color: #d32f2f; font-size: 0.9em;">[{{ vuln.severity }}]</span></strong><br>
                <small><strong>包:</strong> {{ vuln.package }} ({{ vuln.installed_version }})</small><br>
                <small>{{ vuln.description }}</small>
                {% if vuln.fixed_version %}
                <br><small style="color: #4caf50;"><strong>修复版本:</strong> {{ vuln.fixed_version }}</small>
                {% endif %}
            </div>
            {% endfor %}
            {% if high_vulns | length > 5 %}<p style="color: #d32f2f; font-size: 0.9em;">...还有 {{ high_vulns | length - 5 }} 个高风险漏洞</p>{% endif %}
            {% endif %}
            
            {% if medium_vulns %}
            <h4 style="color: #f57c00; margin: 15px 0 10px;">🟡 中风险漏洞 ({{ medium_vulns | length }})</h4>
            {% for vuln in medium_vulns[:3] %}
            <div class="info-item" style="margin-bottom: 15px; border-left-color: #f57c00; background: #fff3e0;">
                <strong>{{ vuln.id }} <span style="color: #f57c00; font-size: 0.9em;">[{{ vuln.severity }}]</span></strong><br>
                <small><strong>包:</strong> {{ vuln.package }} ({{ vuln.installed_version }})</small><br>
                <small>{{ vuln.description }}</small>
                {% if vuln.fixed_version %}
                <br><small style="color: #4caf50;"><strong>修复版本:</strong> {{ vuln.fixed_version }}</small>
                {% endif %}
            </div>
            {% endfor %}
            {% if medium_vulns | length > 3 %}<p style="color: #f57c00; font-size: 0.9em;">...还有 {{ medium_vulns | length - 3 }} 个中风险漏洞</p>{% endif %}
            {% endif %}
            
            {% if low_vulns %}
            <h4 style="color: #388e3c; margin: 15px 0 10px;">🟢 低风险漏洞 ({{ low_vulns | length }})</h4>
            {% if low_vulns | length <= 2 %}
                {% for vuln in low_vulns %}
                <div class="info-item" style="margin-bottom: 15px; border-left-color: #388e3c; background: #e8f5e8;">
                    <strong>{{ vuln.id }} <span style="color: #388e3c; font-size: 0.9em;">[{{ vuln.severity }}]</span></strong><br>
                    <small><strong>包:</strong> {{ vuln.package }} ({{ vuln.installed_version }})</small><br>
                    <small>{{ vuln.description }}</small>
                    {% if vuln.fixed_version %}
                    <br><small style="color: #4caf50;"><strong>修复版本:</strong> {{ vuln.fixed_version }}</small>
                    {% endif %}
                </div>
                {% endfor %}
            {% else %}
                <p style="color: #388e3c;">发现 {{ low_vulns | length }} 个低风险漏洞，建议在方便时进行修复</p>
            {% endif %}
            {% endif %}
            {% endif %}
            
            {% if analysis.security.recommendations %}
            <h3 style="margin-top: 25px; margin-bottom: 15px;">安全建议</h3>
            <ul class="feature-list">
                {% for rec in analysis.security.recommendations %}
                <li>{{ rec }}</li>
                {% endfor %}
            </ul>
            {% endif %}
            
            <div style="margin-top: 20px; font-size: 0.9em; color: #666;">
                <small>扫描时间: {{ analysis.security.scan_timestamp }}</small>
            </div>
        </div>
        {% endif %}

        <!-- 使用方法 -->
        <div class="card">
            <h2>💻 使用方法</h2>
            
            <h3>安装方法</h3>
            <div class="code-block">{{ analysis.usage.installation }}</div>
            
            <h3>基本用法</h3>
            <div class="code-block">{{ analysis.usage.basic_usage }}</div>
            
            {% if analysis.usage.examples %}
            <h3>使用示例</h3>
            {% for example in analysis.usage.examples %}
            <div class="code-block">{{ example }}</div>
            {% endfor %}
            {% endif %}

            {% if analysis.usage.parameters %}
            <h3>主要参数</h3>
            <ul class="feature-list">
                {% for param in analysis.usage.parameters %}
                <li>{{ param }}</li>
                {% endfor %}
            </ul>
            {% endif %}
        </div>

        <!-- 分析信息 -->
        <div class="meta-info">
            <p>分析时间: {{ analysis.analysis_timestamp }}</p>
            <p>报告由 BioTools Agent 自动生成</p>
        </div>
    </div>
</body>
</html>
        """

        template = Template(html_template)
        html_content = template.render(analysis=analysis)

        # 生成文件名
        safe_name = self._sanitize_filename(analysis.repository.name)
        output_file = self.output_dir / f"{safe_name}_analysis.html"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"✅ HTML报告已生成: {output_file}")
        return output_file

    def generate_markdown_report(self, analysis: BioToolAnalysis) -> Path:
        """生成Markdown格式的分析报告"""

        # Markdown模板
        md_template = """# {{ analysis.repository.name }} - 分析报告

> {{ analysis.repository.description or "生物信息学工具分析" }}

## 📊 基础信息

| 项目 | 信息 |
|------|------|
| **名称** | {{ analysis.repository.name }} |
| **地址** | [{{ analysis.repository.url }}]({{ analysis.repository.url }}) |
| **语言** | {{ analysis.repository.language or "未知" }} |
| **Stars** | {{ analysis.repository.stars }} |
| **Forks** | {{ analysis.repository.forks }} |
| **许可证** | {{ analysis.repository.license or "未指定" }} |

## 👥 作者信息

{% for author in analysis.authors %}
- **{{ author.name }}**{% if author.email %} ({{ author.email }}){% endif %}
{% endfor %}

## 📚 相关发表文章

{% if analysis.publications %}
{% for pub in analysis.publications %}
### {{ pub.title }}

- **作者**: {{ pub.authors|join(", ") }}
{% if pub.journal %}- **期刊**: {{ pub.journal }}{% endif %}
{% if pub.year %}- **年份**: {{ pub.year }}{% endif %}
{% if pub.doi %}- **DOI**: [{{ pub.doi }}](https://doi.org/{{ pub.doi }}){% endif %}

{% endfor %}
{% else %}
暂无相关发表文章信息。
{% endif %}

## 🔧 功能特性

### 主要用途
{{ analysis.functionality.main_purpose }}

### 核心功能
{% for feature in analysis.functionality.key_features %}
- {{ feature }}
{% endfor %}

### 支持格式

**输入格式**: {% for format in analysis.functionality.input_formats %}`{{ format }}`{% if not loop.last %}, {% endif %}{% endfor %}

**输出格式**: {% for format in analysis.functionality.output_formats %}`{{ format }}`{% if not loop.last %}, {% endif %}{% endfor %}

### 主要依赖
{% for dep in analysis.functionality.dependencies %}
- `{{ dep }}`
{% endfor %}

## 🏗️ 项目架构

{% if analysis.architecture %}
### 编程语言
{% for lang in analysis.architecture.programming_languages %}
- `{{ lang }}`
{% endfor %}

### 框架/库
{% for framework in analysis.architecture.frameworks %}
- `{{ framework }}`
{% endfor %}

### 入口点
{% for entry in analysis.architecture.entry_points %}
- {{ entry }}
{% endfor %}

### 目录结构
{% for path, purpose in analysis.architecture.directory_structure.items() %}
- **{{ path }}**: {{ purpose }}
{% endfor %}
{% endif %}

## 💻 代码质量

{% if analysis.code_quality %}
### 评估结果

- **代码结构**: {{ analysis.code_quality.code_structure }}
- **文档质量**: {{ analysis.code_quality.documentation_quality }}
- **测试覆盖度**: {{ analysis.code_quality.test_coverage }}
- **代码风格**: {{ analysis.code_quality.code_style }}

### 最佳实践
{% for practice in analysis.code_quality.best_practices %}
- {{ practice }}
{% endfor %}
{% endif %}

## ⚡ 性能特征

{% if analysis.performance %}
### 性能指标

- **时间复杂度**: {{ analysis.performance.time_complexity }}
- **空间复杂度**: {{ analysis.performance.space_complexity }}
- **并行化支持**: {{ analysis.performance.parallelization }}
- **资源使用**: {{ analysis.performance.resource_usage }}

### 优化建议
{% for suggestion in analysis.performance.optimization_suggestions %}
- {{ suggestion }}
{% endfor %}
{% endif %}

## 🧬 生物信息学专业性

{% if analysis.bioinformatics_expertise %}
### 专业评估

- **算法准确性**: {{ analysis.bioinformatics_expertise.algorithm_accuracy }}
- **基准测试结果**: {{ analysis.bioinformatics_expertise.benchmark_results }}
- **工具比较**: {{ analysis.bioinformatics_expertise.tool_comparison }}

### 适用场景
{% for scenario in analysis.bioinformatics_expertise.applicable_scenarios %}
- {{ scenario }}
{% endfor %}
{% endif %}

## 👋 可用性

{% if analysis.usability %}
### 可用性评估

- **文档完整性**: {{ analysis.usability.documentation_completeness }}
- **用户界面**: {{ analysis.usability.user_interface }}
- **错误处理**: {{ analysis.usability.error_handling }}
- **学习曲线**: {{ analysis.usability.learning_curve }}
{% endif %}

## 🔒 安全风险分析

{% if analysis.security %}
### 安全风险概览

| 风险级别 | 数量 |
|----------|------|
| **高风险** | {{ analysis.security.total_high_risk }} |
| **中风险** | {{ analysis.security.total_medium_risk }} |
| **低风险** | {{ analysis.security.total_low_risk }} |

**扫描工具**: {% for tool in analysis.security.scan_tools_used %}`{{ tool }}`{% if not loop.last %}, {% endif %}{% endfor %}

{% if analysis.security.vulnerabilities %}
### 发现的安全问题

{% set high_vulns = analysis.security.vulnerabilities | selectattr("severity", "equalto", "HIGH") | list %}
{% set medium_vulns = analysis.security.vulnerabilities | selectattr("severity", "equalto", "MEDIUM") | list %}
{% set low_vulns = analysis.security.vulnerabilities | selectattr("severity", "equalto", "LOW") | list %}

{% if high_vulns %}
#### 🔴 高风险漏洞 ({{ high_vulns | length }})

{% for vuln in high_vulns[:5] %}
**{{ vuln.id }}** [HIGH]
- 包名: {{ vuln.package }} ({{ vuln.installed_version }})
- 问题: {{ vuln.description }}
{% if vuln.fixed_version %}- 修复版本: {{ vuln.fixed_version }}{% endif %}

{% endfor %}
{% if high_vulns | length > 5 %}*...还有 {{ high_vulns | length - 5 }} 个高风险漏洞*

{% endif %}
{% endif %}

{% if medium_vulns %}
#### 🟡 中风险漏洞 ({{ medium_vulns | length }})

{% for vuln in medium_vulns[:3] %}
**{{ vuln.id }}** [MEDIUM] 
- 包名: {{ vuln.package }} ({{ vuln.installed_version }})
- 问题: {{ vuln.description }}
{% if vuln.fixed_version %}- 修复版本: {{ vuln.fixed_version }}{% endif %}

{% endfor %}
{% if medium_vulns | length > 3 %}*...还有 {{ medium_vulns | length - 3 }} 个中风险漏洞*

{% endif %}
{% endif %}

{% if low_vulns %}
#### 🟢 低风险漏洞 ({{ low_vulns | length }})

{% if low_vulns | length <= 2 %}
{% for vuln in low_vulns %}
**{{ vuln.id }}** [LOW]
- 包名: {{ vuln.package }} ({{ vuln.installed_version }})
- 问题: {{ vuln.description }}
{% if vuln.fixed_version %}- 修复版本: {{ vuln.fixed_version }}{% endif %}

{% endfor %}
{% else %}
发现 {{ low_vulns | length }} 个低风险漏洞，建议在方便时进行修复

{% endif %}
{% endif %}
{% endif %}

{% if analysis.security.recommendations %}
### 安全建议

{% for rec in analysis.security.recommendations %}
- {{ rec }}
{% endfor %}
{% endif %}

*扫描时间: {{ analysis.security.scan_timestamp }}*
{% else %}
暂未进行安全风险分析。
{% endif %}

## 💻 使用方法

### 安装方法
```bash
{{ analysis.usage.installation }}
```

### 基本用法
```bash
{{ analysis.usage.basic_usage }}
```

{% if analysis.usage.examples %}
### 使用示例
{% for example in analysis.usage.examples %}
```bash
{{ example }}
```
{% endfor %}
{% endif %}

{% if analysis.usage.parameters %}
### 主要参数
{% for param in analysis.usage.parameters %}
- {{ param }}
{% endfor %}
{% endif %}

---

*分析时间: {{ analysis.analysis_timestamp }}*  
*报告由 BioTools Agent 自动生成*
        """

        template = Template(md_template)
        md_content = template.render(analysis=analysis)

        # 生成文件名
        safe_name = self._sanitize_filename(analysis.repository.name)
        output_file = self.output_dir / f"{safe_name}_analysis.md"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"✅ Markdown报告已生成: {output_file}")
        return output_file

    def generate_json_report(self, analysis: BioToolAnalysis) -> Path:
        """生成JSON格式的分析数据"""

        # 生成文件名
        safe_name = self._sanitize_filename(analysis.repository.name)
        output_file = self.output_dir / f"{safe_name}_analysis.json"

        # 转换HttpUrl为字符串以便JSON序列化
        data = analysis.model_dump()
        if "repository" in data and "url" in data["repository"]:
            data["repository"]["url"] = str(data["repository"]["url"])

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ JSON数据已生成: {output_file}")
        return output_file

    def generate_all_reports(self, analysis: BioToolAnalysis) -> Dict[str, Path]:
        """生成所有格式的报告"""

        reports = {}

        try:
            reports["html"] = self.generate_html_report(analysis)
        except Exception as e:
            print(f"⚠️ HTML报告生成失败: {e}")

        try:
            reports["markdown"] = self.generate_markdown_report(analysis)
        except Exception as e:
            print(f"⚠️ Markdown报告生成失败: {e}")

        try:
            reports["json"] = self.generate_json_report(analysis)
        except Exception as e:
            print(f"⚠️ JSON数据生成失败: {e}")

        return reports

    def _sanitize_filename(self, filename: str) -> str:
        """清理文件名，移除不安全字符"""
        import re

        # 移除不安全字符，保留字母、数字、下划线和短横线
        safe_name = re.sub(r"[^\w\-_.]", "_", filename)
        # 移除多余的下划线
        safe_name = re.sub(r"_+", "_", safe_name)
        return safe_name.strip("_")
