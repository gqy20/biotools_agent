"""安全风险分析器 - MVP实现"""

import json
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import SecurityAnalysis, SecurityVulnerability


class SecurityAnalyzer:
    """安全分析器 - 专注最核心的安全问题"""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        
    def analyze_security(self) -> Optional[SecurityAnalysis]:
        """执行安全分析 - MVP版本，并行优化"""
        print(f"🔍 开始安全分析: {self.repo_path}")
        
        vulnerabilities = []
        tools_used = []
        recommendations = []
        scan_success = True
        
        # 并行执行依赖检查和代码质量检查
        with ThreadPoolExecutor(max_workers=2) as executor:
            # 提交两个任务
            dep_future = executor.submit(self._run_dependency_check)
            code_future = executor.submit(self._run_code_quality_check)
            
            # 收集结果
            for future in as_completed([dep_future, code_future]):
                try:
                    result = future.result()
                    if result:
                        vulnerabilities.extend(result['vulnerabilities'])
                        tools_used.extend(result['tools_used'])
                        print(f"✅ {result['check_type']}检查完成，发现 {len(result['vulnerabilities'])} 个问题")
                except Exception as e:
                    print(f"⚠️ 并行检查出错: {e}")
                    scan_success = False
        
        # 生成建议
        if vulnerabilities:
            recommendations = self._generate_recommendations(vulnerabilities)
        else:
            recommendations.append("未发现明显的安全问题，建议定期进行安全检查")
        
        # 统计风险等级
        high_risk = len([v for v in vulnerabilities if v.severity == "HIGH"])
        medium_risk = len([v for v in vulnerabilities if v.severity == "MEDIUM"])
        low_risk = len([v for v in vulnerabilities if v.severity == "LOW"])
        
        print(f"📊 安全分析完成: {high_risk} 高风险, {medium_risk} 中风险, {low_risk} 低风险")
        
        return SecurityAnalysis(
            scan_timestamp=datetime.now().isoformat(),
            vulnerabilities=vulnerabilities,
            total_high_risk=high_risk,
            total_medium_risk=medium_risk,
            total_low_risk=low_risk,
            scan_tools_used=tools_used,
            recommendations=recommendations,
            scan_success=scan_success
        )
    
    def _run_dependency_check(self) -> dict:
        """执行依赖漏洞检查（并行任务）"""
        try:
            vulnerabilities = self._check_python_vulnerabilities()
            tools_used = []
            
            if vulnerabilities or self._has_python_dependencies():
                # 根据实际使用的工具确定工具名
                if (self.repo_path / "uv.lock").exists():
                    tools_used.append("uv-audit")
                elif (self.repo_path / "poetry.lock").exists():
                    tools_used.append("safety")
                elif any((self.repo_path / f).exists() for f in ["environment.yml", "environment.yaml"]):
                    tools_used.append("conda-pip-audit")
                else:
                    tools_used.append("pip-audit")
            
            return {
                'check_type': '依赖漏洞',
                'vulnerabilities': vulnerabilities,
                'tools_used': tools_used
            }
        except Exception as e:
            print(f"⚠️ 依赖检查失败: {e}")
            return {'check_type': '依赖漏洞', 'vulnerabilities': [], 'tools_used': []}
    
    def _run_code_quality_check(self) -> dict:
        """执行代码质量检查（并行任务）"""
        try:
            vulnerabilities = self._check_basic_code_quality()
            tools_used = []
            
            if vulnerabilities or self._has_python_code():
                tools_used.append("bandit")
            
            return {
                'check_type': '代码质量',
                'vulnerabilities': vulnerabilities,
                'tools_used': tools_used
            }
        except Exception as e:
            print(f"⚠️ 代码质量检查失败: {e}")
            return {'check_type': '代码质量', 'vulnerabilities': [], 'tools_used': []}
    
    def _has_python_dependencies(self) -> bool:
        """检查是否有Python依赖文件"""
        dep_files = [
            "requirements.txt", "requirements-dev.txt", "requirements-test.txt",
            "setup.py", "pyproject.toml", "Pipfile", "poetry.lock"
        ]
        return any((self.repo_path / f).exists() for f in dep_files)
    
    def _has_python_code(self) -> bool:
        """检查是否有Python代码"""
        return len(list(self.repo_path.glob("**/*.py"))) > 0
    
    def _check_python_vulnerabilities(self) -> List[SecurityVulnerability]:
        """检查Python包漏洞 - 智能选择最佳工具"""
        vulnerabilities = []
        
        # 按优先级检测依赖管理工具
        if (self.repo_path / "uv.lock").exists() and shutil.which("uv"):
            return self._check_with_uv()
        elif (self.repo_path / "poetry.lock").exists() and shutil.which("poetry"):
            return self._check_with_poetry()
        elif any((self.repo_path / f).exists() for f in ["environment.yml", "environment.yaml"]) and shutil.which("conda"):
            return self._check_with_conda()
        else:
            return self._check_with_pip_audit()
    
    def _check_with_uv(self) -> List[SecurityVulnerability]:
        """使用uv audit检查漏洞"""
        print("🔍 使用 uv audit 检查依赖漏洞")
        try:
            result = subprocess.run(
                ["uv", "audit", "--format", "json"],
                capture_output=True, text=True, timeout=120, cwd=self.repo_path
            )
            if result.returncode == 0 and result.stdout:
                # uv audit的JSON格式需要适配
                data = json.loads(result.stdout)
                return self._parse_uv_vulnerabilities(data)
        except Exception as e:
            print(f"⚠️ uv audit失败，回退到pip-audit: {e}")
            return self._check_with_pip_audit()
        return []
    
    def _check_with_poetry(self) -> List[SecurityVulnerability]:
        """使用poetry audit检查漏洞"""
        print("🔍 使用 poetry audit 检查依赖漏洞")
        try:
            # poetry没有内置audit，使用safety
            if shutil.which("safety"):
                result = subprocess.run(
                    ["safety", "check", "--json"],
                    capture_output=True, text=True, timeout=120, cwd=self.repo_path
                )
                if result.stdout:
                    data = json.loads(result.stdout)
                    return self._parse_safety_vulnerabilities(data)
        except Exception as e:
            print(f"⚠️ poetry安全检查失败，回退到pip-audit: {e}")
            return self._check_with_pip_audit()
        return []
    
    def _check_with_conda(self) -> List[SecurityVulnerability]:
        """检查conda环境安全性"""
        print("🔍 检查conda环境文件")
        # conda没有内置安全检查，转换为pip格式检查
        try:
            env_files = list(self.repo_path.glob("environment.y*ml"))
            if env_files:
                print(f"📋 发现conda环境文件: {env_files[0].name}")
                # 简单的依赖提取和pip-audit检查
                return self._check_conda_environment(env_files[0])
        except Exception as e:
            print(f"⚠️ conda环境检查失败: {e}")
        return []
    
    def _check_with_pip_audit(self) -> List[SecurityVulnerability]:
        """使用pip-audit检查漏洞（后备方案）"""
        vulnerabilities = []
        
        # 检查pip-audit是否可用
        if not shutil.which("pip-audit"):
            print("⚠️ pip-audit未安装，跳过依赖漏洞检查")
            return vulnerabilities
        
        # 查找requirements文件
        req_files = []
        for pattern in ["*requirements*.txt", "setup.py", "pyproject.toml"]:
            req_files.extend(list(self.repo_path.glob(pattern)))
        
        if not req_files:
            print("📋 未发现Python依赖文件")
            return vulnerabilities
            
        try:
            # 选择第一个requirements文件
            req_file = req_files[0]
            print(f"🔍 使用 pip-audit 检查: {req_file.name}")
            
            # 执行pip-audit命令
            cmd = ["pip-audit", "--format=json", "--requirement", str(req_file)]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=120,  # 2分钟超时
                cwd=self.repo_path
            )
            
            if result.returncode == 0 and result.stdout:
                # 解析JSON输出
                try:
                    data = json.loads(result.stdout)
                    for dep in data.get("dependencies", []):
                        for vuln in dep.get("vulns", []):
                            vulnerabilities.append(SecurityVulnerability(
                                id=vuln.get("id", "UNKNOWN"),
                                severity=self._map_severity(vuln.get("severity")),
                                package=dep.get("name", "unknown"),
                                installed_version=dep.get("version", "unknown"),
                                fixed_version=", ".join(vuln.get("fix_versions", [])) or None,
                                description=vuln.get("description", "")[:200]  # 限制长度
                            ))
                except json.JSONDecodeError:
                    print("⚠️ pip-audit输出格式解析失败")
            
        except subprocess.TimeoutExpired:
            print("⚠️ pip-audit检查超时")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ pip-audit执行失败: {e}")
        except Exception as e:
            print(f"⚠️ pip-audit检查出错: {e}")
            
        return vulnerabilities
    
    def _parse_uv_vulnerabilities(self, data: dict) -> List[SecurityVulnerability]:
        """解析uv audit的输出"""
        vulnerabilities = []
        # uv audit格式适配
        for vuln in data.get("vulnerabilities", []):
            vulnerabilities.append(SecurityVulnerability(
                id=vuln.get("id", "UV-UNKNOWN"),
                severity=self._map_severity(vuln.get("severity")),
                package=vuln.get("package", "unknown"),
                installed_version=vuln.get("installed_version", "unknown"),
                fixed_version=vuln.get("fixed_version"),
                description=vuln.get("summary", "")[:200]
            ))
        return vulnerabilities
    
    def _parse_safety_vulnerabilities(self, data: list) -> List[SecurityVulnerability]:
        """解析safety输出"""
        vulnerabilities = []
        for vuln in data:
            vulnerabilities.append(SecurityVulnerability(
                id=vuln.get("id", "SAFETY-UNKNOWN"),
                severity="HIGH",  # safety默认都是高危
                package=vuln.get("package", "unknown"),
                installed_version=vuln.get("installed_version", "unknown"),
                fixed_version=vuln.get("fixed_version"),
                description=vuln.get("vulnerability", "")[:200]
            ))
        return vulnerabilities
    
    def _check_conda_environment(self, env_file: Path) -> List[SecurityVulnerability]:
        """检查conda环境文件的安全性"""
        vulnerabilities = []
        try:
            import yaml
            with open(env_file) as f:
                env_data = yaml.safe_load(f)
            
            pip_deps = []
            dependencies = env_data.get("dependencies", [])
            for dep in dependencies:
                if isinstance(dep, dict) and "pip" in dep:
                    pip_deps.extend(dep["pip"])
            
            if pip_deps:
                print(f"🔍 conda环境中发现 {len(pip_deps)} 个pip依赖")
                # 创建临时requirements文件
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write('\n'.join(pip_deps))
                    temp_req = f.name
                
                try:
                    if shutil.which("pip-audit"):
                        cmd = ["pip-audit", "--format=json", "--requirement", temp_req]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                        # pip-audit在发现漏洞时会返回非0退出码，但仍有有效输出
                        if result.stdout:
                            try:
                                data = json.loads(result.stdout)
                                vulnerabilities = self._parse_pip_audit_output(data)
                                print(f"✅ conda pip依赖检查完成，发现 {len(vulnerabilities)} 个漏洞")
                            except json.JSONDecodeError:
                                print(f"⚠️ conda pip依赖输出解析失败")
                        elif result.returncode == 0:
                            print(f"✅ conda pip依赖检查完成，未发现漏洞")
                        else:
                            print(f"⚠️ conda pip依赖检查出错: {result.stderr}")
                    else:
                        print("⚠️ pip-audit未安装，跳过conda pip依赖检查")
                finally:
                    Path(temp_req).unlink(missing_ok=True)
            else:
                print("📋 conda环境文件中没有pip依赖")
        except ImportError:
            print("⚠️ PyYAML未安装，无法解析conda环境文件")
        except Exception as e:
            print(f"⚠️ conda环境检查失败: {e}")
        return vulnerabilities
    
    def _parse_pip_audit_output(self, data: dict) -> List[SecurityVulnerability]:
        """解析pip-audit标准输出"""
        vulnerabilities = []
        for dep in data.get("dependencies", []):
            for vuln in dep.get("vulns", []):
                vulnerabilities.append(SecurityVulnerability(
                    id=vuln.get("id", "UNKNOWN"),
                    severity=self._map_severity(vuln.get("severity")),
                    package=dep.get("name", "unknown"),
                    installed_version=dep.get("version", "unknown"),
                    fixed_version=", ".join(vuln.get("fix_versions", [])) or None,
                    description=vuln.get("description", "")[:200]
                ))
        return vulnerabilities
    
    def _check_basic_code_quality(self) -> List[SecurityVulnerability]:
        """基础代码质量检查 - 使用bandit"""
        vulnerabilities = []
        
        # 检查bandit是否可用
        if not shutil.which("bandit"):
            print("⚠️ bandit未安装，跳过代码质量检查")
            return vulnerabilities
        
        # 查找Python文件
        py_files = list(self.repo_path.glob("**/*.py"))
        if not py_files:
            print("📋 未发现Python代码文件")
            return vulnerabilities
            
        try:
            print(f"🔍 检查 {len(py_files)} 个Python文件")
            
            # 执行bandit命令
            cmd = ["bandit", "-f", "json", "-r", str(self.repo_path)]
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=60,  # 1分钟超时
                cwd=self.repo_path
            )
            
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    # 只取前5个最严重的问题
                    issues = data.get("results", [])
                    high_issues = [i for i in issues if i.get("issue_severity") == "HIGH"]
                    medium_issues = [i for i in issues if i.get("issue_severity") == "MEDIUM"]
                    
                    # 优先显示高危问题，最多5个
                    selected_issues = (high_issues + medium_issues)[:5]
                    
                    for issue in selected_issues:
                        vulnerabilities.append(SecurityVulnerability(
                            id=issue.get("test_id", "BANDIT-UNKNOWN"),
                            severity=issue.get("issue_severity", "LOW").upper(),
                            package="code-quality",
                            installed_version="current",
                            fixed_version=None,
                            description=f"文件 {issue.get('filename', 'unknown')} 第{issue.get('line_number', '?')}行: {issue.get('issue_text', '')}"[:200]
                        ))
                except json.JSONDecodeError:
                    print("⚠️ bandit输出格式解析失败")
            
        except subprocess.TimeoutExpired:
            print("⚠️ bandit检查超时")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ bandit执行失败: {e}")
        except Exception as e:
            print(f"⚠️ bandit检查出错: {e}")
            
        return vulnerabilities
    
    def _map_severity(self, severity: str) -> str:
        """映射严重程度"""
        if not severity:
            return "LOW"
        severity = severity.upper()
        if severity in ["CRITICAL", "HIGH"]:
            return "HIGH"
        elif severity in ["MEDIUM", "MODERATE"]:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_recommendations(self, vulnerabilities: List[SecurityVulnerability]) -> List[str]:
        """生成修复建议"""
        recommendations = []
        
        # 统计问题类型
        dep_vulns = [v for v in vulnerabilities if v.package != "code-quality"]
        code_vulns = [v for v in vulnerabilities if v.package == "code-quality"]
        high_priority = [v for v in vulnerabilities if v.severity == "HIGH"]
        
        if high_priority:
            recommendations.append(f"🚨 发现 {len(high_priority)} 个高风险安全问题，建议立即处理")
        
        if dep_vulns:
            fixable = [v for v in dep_vulns if v.fixed_version]
            if fixable:
                recommendations.append(f"📦 更新 {len(fixable)} 个存在漏洞的依赖包到安全版本")
            recommendations.append("🔄 建议定期运行 `pip-audit` 检查新的安全漏洞")
            
        if code_vulns:
            recommendations.append(f"🔧 修复 {len(code_vulns)} 个代码安全问题")
            recommendations.append("🚀 建议在CI/CD中集成bandit安全检查")
        
        if not vulnerabilities:
            recommendations.append("✅ 未发现明显安全问题，继续保持良好的安全实践")
            
        return recommendations
