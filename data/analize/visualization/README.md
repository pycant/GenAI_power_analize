# 学术可视化系统

**版本**: 1.0  
**创建时间**: 2026-03-05

---

## 概述

本目录包含符合学术标准的可视化工具和脚本，用于生成高质量的论文图表。所有图表遵循主流AI/ML期刊标准（NeurIPS、ICML、ACL等）。

## 核心特性

- ✅ **学术标准**: 纯英文、300 DPI、矢量格式
- ✅ **色盲友好**: 使用Okabe-Ito配色方案
- ✅ **黑白可读**: 图表在黑白打印时仍可区分
- ✅ **一键生成**: 自动生成8种标准图表
- ✅ **可定制**: 灵活的工具库支持自定义图表

## 目录结构

```
visualization/
├── scripts/
│   ├── visualization_utils.py           # 核心工具库
│   └── generate_all_visualizations.py   # 主生成脚本
├── figures/                              # 输出目录
├── ACADEMIC_VISUALIZATION_STYLE_GUIDE.md # 完整风格指南
├── VISUALIZATION_QUICK_GUIDE.md          # 快速指南
└── README.md                             # 本文档
```

## 快速开始

### 1. 生成所有图表

```bash
conda activate bartscore
set PYTHONUTF8=1
cd data/analize/visualization/scripts
python generate_all_visualizations.py
```

### 2. 查看输出

生成的图表位于 `figures/` 目录，包括：
- PDF格式（矢量，推荐用于论文）
- PNG格式（位图，用于预览）

## 生成的图表

1. **质量-能耗散点图** - 展示质量和能耗的权衡关系
2. **吞吐量-延迟散点图** - 展示性能指标的关系
3. **质效比柱状图** - 对比各模型在不同任务上的表现
4. **综合能力雷达图** - 多维度能力对比（Top 5模型）
5. **帕累托前沿图** - 识别最优模型集合
6. **模型-任务热力图** - 展示模型在各任务上的质效比
7. **公平性分析图** - 评估模型跨任务的公平性
8. **成本效益分析图** - 分析成本和质量的关系

## 使用工具库

### 基础示例

```python
from visualization_utils import (
    setup_academic_style,
    get_academic_colors,
    save_academic_figure,
    create_scatter_plot
)

# 初始化
setup_academic_style()

# 创建散点图
fig, ax = create_scatter_plot(
    x_data=energy_data,
    y_data=quality_data,
    xlabel='Energy (J)',
    ylabel='Quality Score',
    title='Quality vs Energy'
)

# 保存
save_academic_figure(fig, 'my_figure', ['pdf', 'png'])
```

## 文档

- **快速指南**: `VISUALIZATION_QUICK_GUIDE.md` - 快速上手
- **风格指南**: `ACADEMIC_VISUALIZATION_STYLE_GUIDE.md` - 完整规范

## 依赖

- Python 3.8+
- matplotlib
- seaborn
- numpy
- pandas

## 学术标准

所有图表符合以下标准：
- 纯英文标签
- 300 DPI分辨率
- PDF矢量格式
- 色盲友好配色
- 黑白打印可读
- 适合主流期刊投稿

---

**维护者**: AI Assistant  
**最后更新**: 2026-03-05
