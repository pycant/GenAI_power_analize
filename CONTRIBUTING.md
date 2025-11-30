# 贡献指南

感谢您对GenAI模型能效评级体系项目的关注！我们欢迎各种形式的贡献，共同推进AI模型评估技术的发展。

## 🎯 贡献类型

我们欢迎以下类型的贡献：

### 🐛 问题报告
- 报告系统Bug或错误
- 提交功能异常问题
- 反馈用户体验问题
- 报告安全漏洞

### 💡 功能建议
- 提出新功能想法
- 建议功能改进
- 推荐技术方案
- 分享使用场景

### 🔧 代码贡献
- 修复Bug
- 实现新功能
- 优化性能
- 改进代码质量
- 添加测试用例

### 📖 文档贡献
- 完善技术文档
- 更新使用说明
- 翻译文档内容
- 添加示例代码

### 🧪 实验贡献
- 提供测试数据
- 参与实验验证
- 分享评估结果
- 贡献评估模型

## 🚀 快速开始

### 环境准备

1. **Fork项目仓库**
```bash
# 在GitHub上点击Fork按钮，然后克隆您的fork
git clone https://github.com/YOUR_USERNAME/genai-power-evaluation.git
cd genai-power-evaluation
```

2. **添加上游仓库**
```bash
git remote add upstream https://github.com/original-org/genai-power-evaluation.git
```

3. **创建开发分支**
```bash
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/issue-description
```

### 开发环境搭建

1. **安装依赖**
```bash
# 后端依赖
cd backend
pip install -r requirements-dev.txt

# 前端依赖
cd frontend
npm install
```

2. **配置环境**
```bash
cp .env.example .env
# 编辑.env文件，配置必要参数
```

3. **运行测试**
```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

## 📋 贡献流程

### 1. 问题识别

#### 1.1 查找现有问题
- 浏览 [GitHub Issues](https://github.com/your-org/genai-power-evaluation/issues)
- 查看 [项目路线图](docs/roadmap.md)
- 关注 [讨论区](https://github.com/your-org/genai-power-evaluation/discussions)

#### 1.2 报告新问题
- 使用相应的Issue模板
- 提供详细的复现步骤
- 包含环境和版本信息
- 添加相关标签

### 2. 开始贡献

#### 2.1 认领任务
- 在Issue中评论认领
- 等待确认分配
- 开始开发工作

#### 2.2 开发规范
- 遵循代码规范（见下文）
- 编写必要的测试
- 更新相关文档
- 确保所有测试通过

### 3. 提交贡献

#### 3.1 提交前检查
```bash
# 运行代码检查
cd backend
flake8 .
black .
isort .

# 运行测试
pytest

# 检查测试覆盖率
pytest --cov=.
```

#### 3.2 提交代码
```bash
git add .
git commit -m "feat(module): 描述你的变更

详细说明变更内容、原因和影响

Closes #123"
```

#### 3.3 推送和创建PR
```bash
git push origin feature/your-feature-name
```

在GitHub上创建Pull Request，填写PR模板。

### 4. 代码审查

- 等待审查者反馈
- 根据意见修改代码
- 及时响应审查意见
- 保持沟通礼貌和专业

## 📝 代码规范

### Python代码规范

我们遵循PEP 8规范，并使用以下工具：

#### 代码格式化
```python
# 使用Black进行代码格式化
black --line-length 88 .

# 使用isort进行导入排序
isort --profile black .
```

#### 代码检查
```python
# 使用flake8进行代码检查
flake8 --max-line-length=88 --extend-ignore=E203,W503 .

# 使用mypy进行类型检查
mypy --ignore-missing-imports .
```

#### 代码风格示例
```python
"""模块级文档字符串."""

from typing import List, Optional

import numpy as np
from pydantic import BaseModel


class ModelEvaluator:
    """模型评估器类."""
    
    def __init__(self, model_name: str, config: dict):
        """初始化评估器.
        
        Args:
            model_name: 模型名称
            config: 配置字典
        """
        self.model_name = model_name
        self.config = config
    
    def evaluate_performance(
        self, 
        test_data: np.ndarray,
        metrics: Optional[List[str]] = None
    ) -> dict:
        """评估模型性能.
        
        Args:
            test_data: 测试数据
            metrics: 评估指标列表
            
        Returns:
            评估结果字典
            
        Raises:
            ValueError: 当输入数据无效时
        """
        if metrics is None:
            metrics = ["accuracy", "precision", "recall"]
            
        # 实现评估逻辑
        results = {}
        for metric in metrics:
            results[metric] = self._calculate_metric(test_data, metric)
            
        return results
    
    def _calculate_metric(self, data: np.ndarray, metric: str) -> float:
        """计算单个指标."""
        # 具体实现
        pass
```

### JavaScript/TypeScript代码规范

#### 代码格式化
```bash
# 使用Prettier进行代码格式化
npm run format

# 使用ESLint进行代码检查
npm run lint
```

#### 代码风格示例
```typescript
// 接口定义
interface ModelConfig {
  name: string;
  version: string;
  parameters: Record<string, any>;
}

// 组件示例
import React, { useState, useEffect } from 'react';

interface ModelCardProps {
  model: ModelConfig;
  onEvaluate: (model: ModelConfig) => void;
}

export const ModelCard: React.FC<ModelCardProps> = ({ model, onEvaluate }) => {
  const [isEvaluating, setIsEvaluating] = useState(false);
  
  const handleEvaluate = async () => {
    setIsEvaluating(true);
    try {
      await onEvaluate(model);
    } catch (error) {
      console.error('Evaluation failed:', error);
    } finally {
      setIsEvaluating(false);
    }
  };
  
  return (
    <div className="model-card">
      <h3>{model.name}</h3>
      <p>Version: {model.version}</p>
      <button 
        onClick={handleEvaluate}
        disabled={isEvaluating}
      >
        {isEvaluating ? 'Evaluating...' : 'Evaluate'}
      </button>
    </div>
  );
};
```

## 🧪 测试规范

### 测试类型

#### 单元测试
```python
# 后端单元测试示例
def test_model_evaluator():
    """测试模型评估器."""
    from evaluator import ModelEvaluator
    
    # 准备测试数据
    config = {"threshold": 0.8}
    evaluator = ModelEvaluator("test_model", config)
    
    # 执行测试
    result = evaluator.evaluate_performance(test_data)
    
    # 验证结果
    assert "accuracy" in result
    assert 0 <= result["accuracy"] <= 1
```

#### 集成测试
```python
# API集成测试示例
def test_evaluation_api(client):
    """测试评估API."""
    payload = {
        "model_name": "test_model",
        "test_data": [[1, 2, 3], [4, 5, 6]]
    }
    
    response = client.post("/api/evaluate", json=payload)
    
    assert response.status_code == 200
    assert "results" in response.json()
```

#### 前端测试
```typescript
// React组件测试示例
import { render, screen, fireEvent } from '@testing-library/react';
import { ModelCard } from './ModelCard';

test('renders model card', () => {
  const mockModel = {
    name: 'Test Model',
    version: '1.0.0',
    parameters: {}
  };
  
  const mockOnEvaluate = jest.fn();
  
  render(
    <ModelCard 
      model={mockModel} 
      onEvaluate={mockOnEvaluate}
    />
  );
  
  expect(screen.getByText('Test Model')).toBeInTheDocument();
  expect(screen.getByText('Version: 1.0.0')).toBeInTheDocument();
});
```

### 测试覆盖率要求
- **单元测试覆盖率**: ≥ 85%
- **集成测试覆盖率**: ≥ 70%
- **关键模块覆盖率**: ≥ 95%

## 📖 文档规范

### 文档类型

#### 代码文档
```python
def calculate_efficiency_score(
    performance_metrics: dict,
    resource_usage: dict,
    cost_data: dict
) -> float:
    """计算模型效率评分.
    
    基于性能指标、资源使用和成本数据综合计算模型的效率评分。
    
    Args:
        performance_metrics: 性能指标字典，包含准确性、速度等
            - accuracy (float): 模型准确性 (0-1)
            - inference_speed (float): 推理速度 (samples/second)
            - memory_usage (float): 内存使用量 (MB)
        resource_usage: 资源使用数据
            - cpu_hours (float): CPU使用时长
            - gpu_hours (float): GPU使用时长
            - energy_kwh (float): 能耗 (kWh)
        cost_data: 成本数据
            - training_cost (float): 训练成本 ($)
            - deployment_cost (float): 部署成本 ($)
            
    Returns:
        float: 效率评分 (0-100)，越高表示效率越好
        
    Raises:
        ValueError: 当输入数据格式不正确时
        KeyError: 当缺少必要字段时
        
    Example:
        >>> metrics = {"accuracy": 0.95, "inference_speed": 100.0}
        >>> resources = {"cpu_hours": 10.5, "energy_kwh": 2.3}
        >>> costs = {"training_cost": 500.0}
        >>> score = calculate_efficiency_score(metrics, resources, costs)
        >>> print(f"效率评分: {score}")
        效率评分: 78.5
    """
```

#### API文档
```markdown
## POST /api/models/evaluate

评估指定模型的性能。

### 请求参数

| 参数 | 类型 | 必需 | 描述 |
|------|------|------|------|
| model_id | string | 是 | 模型唯一标识符 |
| test_dataset | string | 是 | 测试数据集名称 |
| metrics | array | 否 | 评估指标列表，默认使用所有指标 |

### 请求示例

```json
{
  "model_id": "gpt-3.5-turbo",
  "test_dataset": "glue-sst2",
  "metrics": ["accuracy", "f1_score", "inference_speed"]
}
```

### 响应示例

```json
{
  "status": "success",
  "data": {
    "evaluation_id": "eval_123456",
    "results": {
      "accuracy": 0.945,
      "f1_score": 0.932,
      "inference_speed": 45.2
    },
    "duration": 120.5,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```
```

## 🔍 提交规范

### 提交信息格式

遵循Conventional Commits规范：

```
<类型>(<范围>): <简短描述>

<详细描述>

<脚注>
```

### 提交类型

| 类型 | 描述 | 使用场景 |
|------|------|----------|
| feat | 新功能 | 添加新功能或特性 |
| fix | Bug修复 | 修复系统缺陷 |
| docs | 文档 | 更新文档内容 |
| style | 样式 | 代码格式调整 |
| refactor | 重构 | 代码重构但不改变功能 |
| test | 测试 | 添加或修改测试 |
| chore | 杂项 | 构建过程或辅助工具的变动 |
| perf | 性能 | 性能优化 |
| ci | CI/CD | 持续集成配置 |
| revert | 回退 | 撤销之前的提交 |

### 提交范围

常见范围：
- `api`: API接口相关
- `ui`: 用户界面相关
- `db`: 数据库相关
- `eval`: 评估引擎相关
- `auth`: 认证授权相关
- `docs`: 文档相关
- `config`: 配置相关

### 提交示例

```bash
# 好的提交示例
git commit -m "feat(eval): 添加模型碳排放评估功能

实现了基于能耗数据的碳排放计算功能，包括：
- 电力碳排放因子配置
- 训练和推理过程碳排放计算
- 碳排放可视化图表

Closes #234"

# 不好的提交示例
git commit -m "update files"
git commit -m "fix bug"
```

## 🏷️ 分支管理

### 分支命名规范

#### 功能分支
```
feature/功能描述
示例: feature/model-comparison, feature/carbon-calculation
```

#### Bug修复分支
```
bugfix/问题描述
示例: bugfix/api-timeout, bugfix/memory-leak
```

#### 文档分支
```
docs/文档描述
示例: docs/api-guide, docs/deployment-guide
```

### 分支生命周期

1. **创建**: 从develop分支创建
2. **开发**: 在分支上进行开发
3. **测试**: 完成开发和测试
4. **审查**: 提交Pull Request
5. **合并**: 审查通过后合并
6. **清理**: 删除已合并的分支

## 📊 质量标准

### 代码质量要求

- **测试覆盖率**: ≥ 85%
- **代码规范**: 零警告
- **性能要求**: 不降低系统性能
- **安全要求**: 通过安全扫描

### 文档要求

- **代码注释**: 关键代码必须有注释
- **API文档**: 所有API必须有文档
- **变更记录**: 重要变更需要记录
- **用户文档**: 新功能需要用户文档

### 审查标准

#### 必须检查项
- [ ] 代码功能正确性
- [ ] 代码风格和规范
- [ ] 测试用例完整性
- [ ] 文档更新完整性
- [ ] 性能影响评估
- [ ] 安全性检查

#### 可选检查项
- [ ] 代码可读性
- [ ] 设计模式应用
- [ ] 重构机会识别
- [ ] 性能优化建议

## 🚨 重要提醒

### 禁止事项
- ❌ 不要提交敏感信息（密码、密钥等）
- ❌ 不要提交大型二进制文件
- ❌ 不要强制推送（force push）到共享分支
- ❌ 不要直接提交到master/main分支
- ❌ 不要忽视测试失败

### 最佳实践
- ✅ 经常提交小的、逻辑完整的变更
- ✅ 写清晰的提交信息
- ✅ 及时同步上游代码
- ✅ 主动沟通协作
- ✅ 保持学习和改进

## 📞 获取帮助

如果您在贡献过程中遇到问题：

1. **查看文档**: 先查看相关文档和FAQ
2. **搜索问题**: 在Issue中搜索类似问题
3. **创建Issue**: 创建新的Issue描述问题
4. **参与讨论**: 在Discussion中发起讨论
5. **联系维护者**: 通过邮件或即时通讯联系

### 联系方式
- 📧 **项目邮箱**: genai-power@university.edu
- 💬 **讨论区**: [GitHub Discussions](https://github.com/your-org/genai-power-evaluation/discussions)
- 🐛 **问题报告**: [GitHub Issues](https://github.com/your-org/genai-power-evaluation/issues)

## 🙏 致谢

感谢所有贡献者对本项目的支持和贡献！您的每一份贡献都在推动AI评估技术的发展。

<div align="center">

**让我们一起构建更好的AI评估体系！** 🚀

</div>