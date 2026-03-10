# Pareto Analysis V3 索引生成器使用说明

## 📋 概述

`generate_pareto_v3_index.py` 是一个自动化脚本，用于扫描 `pareto_analysis_v3` 目录结构并生成完整的文档索引。该索引帮助快速导航和查阅所有帕累托分析结果。

## 🎯 功能特性

### 自动扫描
- 遍历所有任务类型目录（code, creative, math, qa, reasoning, summary, translation）
- 识别主报告、PCA 分析报告、图表和数据文件
- 统计各类资源数量

### 智能提取
- 从报告文件中提取标题和摘要
- 计算文件大小和统计信息
- 生成相对路径链接

### 结构化输出
- 生成 Markdown 格式的索引文档
- 按任务类型组织内容
- 包含使用指南和相关文档链接

## 🚀 快速开始

### 方法 1: 使用批处理脚本（推荐 Windows 用户）

双击运行或在命令行执行：

```bash
analysis\qe_research\scripts\generate_pareto_v3_index.bat
```

### 方法 2: 直接运行 Python 脚本

```bash
# 在项目根目录下执行
python analysis/qe_research/scripts/generate_pareto_v3_index.py
```

### 方法 3: 在 Conda 环境中运行

```bash
conda activate bartscore
python analysis/qe_research/scripts/generate_pareto_v3_index.py
```

## 📂 输出文件

脚本会在以下位置生成索引文档：

```
analysis/qe_research/results/pareto_analysis_v3/INDEX.md
```

## 📊 生成的索引内容

索引文档包含以下部分：

1. **概述**: 分析方法和任务类型覆盖情况
2. **综合报告**: 链接到总体分析报告
3. **资源统计**: 报告、图表、数据文件的数量统计
4. **任务详细索引**: 每个任务类型的详细资源列表
   - 主报告链接和摘要
   - PCA 分析报告链接和摘要
   - 图表文件列表
   - 数据文件列表（含大小）
5. **使用指南**: 如何查看和使用分析结果
6. **相关文档**: 其他相关文档的链接

## 🔍 索引结构示例

```markdown
### CODE 任务

📊 **资源统计**: 1 个主报告 | 1 个PCA报告 | 7 张图表 | 1 个数据文件

#### 📄 主报告
**[代码生成任务帕累托前沿分析报告](path/to/report.md)**
> 报告摘要...

#### 🔬 PCA 分析报告
**[PCA降维分析报告](path/to/pca_report.md)**
> PCA 分析摘要...

#### 📈 主要图表
- [pareto_quality_speed.png](path/to/chart.png)
- [pareto_quality_energy.png](path/to/chart.png)

#### 💾 数据文件
- [merged_data.csv](path/to/data.csv) (1.1 KB)
```

## 🛠️ 脚本工作原理

### 1. 目录扫描
```python
# 扫描 pareto_analysis_v3 目录
results_dir = script_dir.parent / "results" / "pareto_analysis_v3"
```

### 2. 文件分类
- `.md` 文件 → 报告文件
- `.png/.jpg/.svg` 文件 → 图表文件
- `.csv/.json/.xlsx` 文件 → 数据文件

### 3. 内容提取
```python
def extract_report_summary(report_path, max_lines=10):
    # 提取第一个 # 标题
    # 提取第一段非空文本作为摘要
    # 限制摘要长度为 200 字符
```

### 4. 文档生成
- 生成 Markdown 格式内容
- 使用相对路径创建链接
- 添加 emoji 图标增强可读性

## 📝 自定义配置

### 修改摘要长度

在 `extract_report_summary` 函数中修改：

```python
summary = summary.strip()[:200]  # 修改为你想要的长度
```

### 修改扫描深度

在 `count_files_by_type` 函数中修改：

```python
for file in directory.rglob('*'):  # rglob 递归扫描所有子目录
```

### 添加新的文件类型

在 `count_files_by_type` 函数中添加：

```python
counts = {
    'reports': 0,
    'images': 0,
    'data': 0,
    'pca_reports': 0,
    'your_new_type': 0  # 添加新类型
}
```

## 🔧 故障排除

### 问题 1: 找不到 Python

**错误信息**: `未找到 Python`

**解决方案**:
- 确保 Python 已安装
- 将 Python 添加到系统 PATH
- 或使用完整路径运行脚本

### 问题 2: 编码错误

**错误信息**: `UnicodeDecodeError`

**解决方案**:
- 确保终端使用 UTF-8 编码
- Windows 用户运行 `chcp 65001`
- 或在脚本开头设置 `PYTHONUTF8=1`

### 问题 3: 目录不存在

**错误信息**: `目录不存在`

**解决方案**:
- 确认在项目根目录下运行脚本
- 检查 `pareto_analysis_v3` 目录是否存在
- 验证目录路径是否正确

### 问题 4: 权限错误

**错误信息**: `Permission denied`

**解决方案**:
- 以管理员身份运行
- 检查文件和目录权限
- 确保输出目录可写

## 📈 输出示例

运行成功后，你会看到：

```
📂 扫描目录: F:\all_proj\GenAI_power_analize\analysis\qe_research\results\pareto_analysis_v3
📝 生成索引文档...
✅ 索引文档已生成: ...\INDEX.md
📄 文档大小: 13.1 KB

📊 资源统计:
  - 报告文件: 8 个
  - PCA 分析报告: 6 个
  - 图表文件: 44 张
  - 数据文件: 7 个
```

## 🔄 更新索引

当添加新的分析结果或修改现有报告后，重新运行脚本即可更新索引：

```bash
python analysis/qe_research/scripts/generate_pareto_v3_index.py
```

索引文档会自动更新时间戳和内容。

## 📚 相关文档

- [PCA 功能完整说明](pareto_core/PCA_FEATURE_COMPLETE.md)
- [帕累托分析快速参考](pareto_core/QUICK_REFERENCE.md)
- [质量分析指南](../COMPREHENSIVE_QUALITY_ANALYSIS_GUIDE.md)

## 🤝 贡献

如需改进脚本功能，请：

1. 修改 `generate_pareto_v3_index.py`
2. 测试生成的索引文档
3. 更新本说明文档
4. 提交更改

## 📄 许可

本脚本是 GenAI 模型能效评级体系项目的一部分。

---

*最后更新: 2026-03-09*
