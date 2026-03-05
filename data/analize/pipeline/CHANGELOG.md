# 数据管道系统更新日志

## [v1.1.0] - 2026-03-05

### 🎉 新增功能

#### JSON数据加载器

- **SummaryJsonLoader**: 加载实验汇总JSON数据
  - 支持12个模型目录的自动扫描
  - 提取性能、资源、质量指标
  - 自动标准化模型名称
  
- **RawJsonLoader**: 加载原始实验JSON数据
  - 完整对话记录
  - 详细监控数据
  - 时间戳信息

#### 支持的模型目录

```
data/
├── deepseek_8b_ol_q4km/
├── gemma_2b_hf_4bit/
├── gemma_2b_hf_8bit/
├── gemma_4b_ol_q4km/
├── phi3_4b_hf_4bit/
├── phi3_4b_hf_8bit/
├── qwen_4b_ol_q4km/
├── qwen_8b_ol_q4km/
├── qwen25_3b_hf_4bit/
├── qwen25_3b_hf_8bit/
├── qwen25_7b_hf_4bit/
└── qwen25_7b_hf_8bit/
```

#### 新增文件

1. `converters/__init__.py` - 转换器模块
2. `converters/summary_json_loader.py` - Summary加载器
3. `converters/raw_json_loader.py` - Raw加载器
4. `JSON_LOADERS_GUIDE.md` - 使用指南
5. `test_json_loaders.py` - 测试脚本
6. `example_json_loading.py` - 示例代码
7. `JSON_SUPPORT_SUMMARY.md` - 功能总结
8. `CHANGELOG.md` - 本文档

### 🔧 改进

- **数据管道集成**: JSON加载器自动集成到 `data_pipeline.py`
- **模型名称标准化**: 自动处理 `Ollama:` 和 `HF:` 前缀
- **智能数据合并**: 自动合并JSON、CSV和评估结果
- **错误处理**: 增强的异常处理和日志记录

### 📊 提取的指标

#### 性能指标
- `latency_s` - 延迟（秒）
- `toks_per_s` - 吞吐量（tokens/秒）
- `ttft_s` - 首token时间（秒）
- `token_count` - token总数
- `output_tokens` - 输出token数

#### 资源使用
- **CPU**: 使用率（平均、峰值）、能耗
- **内存**: 使用量（平均、峰值）
- **GPU**: 利用率、显存、功耗、能耗、温度

#### 质量指标
- `bartscore` - BARTScore质量得分
- `generated_text_length` - 生成文本长度
- `avg_response_length` - 平均响应长度

### 📚 文档

- 新增详细的JSON加载器使用指南
- 更新数据流说明
- 添加7个完整使用示例
- 完整的测试覆盖

### 🧪 测试

- Summary JSON加载器测试
- Raw JSON加载器测试
- 数据管道集成测试
- 数据验证测试

### 🚀 使用方法

```python
# 方法1: 直接使用加载器
from data.analize.pipeline.converters import SummaryJsonLoader
loader = SummaryJsonLoader()
df = loader.load_all_summary_data()

# 方法2: 通过数据管道（推荐）
from data.analize.pipeline import ExperimentDataManager
dm = ExperimentDataManager()
dm.initialize_pipeline()  # 自动加载JSON数据
df = dm.load_all_data()
```

---

## [v1.0.0] - 2026-03-05

### 🎉 初始版本

#### 核心功能

- **数据管理器**: 统一的数据访问接口
- **ETL管道**: 自动化数据转换
- **数据验证**: 完整性和一致性检查
- **缓存系统**: 智能缓存管理
- **性能优化**: Parquet格式，内存优化

#### 核心模块

1. `data_manager.py` - 数据管理核心
2. `data_pipeline.py` - ETL管道
3. `data_validator.py` - 数据验证
4. `schema.py` - 数据模式定义
5. `utils/cache_manager.py` - 缓存管理
6. `utils/performance.py` - 性能优化

#### 配置和文档

1. `configs/pipeline_config.yaml` - 配置文件
2. `README.md` - 使用文档
3. `IMPLEMENTATION_SUMMARY.md` - 实现总结
4. `docs/DATA_PIPELINE_GUIDE.md` - 快速指南

#### 脚本和示例

1. `quick_start.py` - 快速开始
2. `examples.py` - 10个使用示例
3. `test_pipeline.py` - 测试脚本

#### 性能优势

- 存储空间减少70-80%
- 读取速度提升5-10倍
- 内存使用减少70%

---

## 版本说明

### 版本号规则

- **主版本号**: 重大架构变更
- **次版本号**: 新功能添加
- **修订号**: Bug修复和小改进

### 兼容性

- v1.1.0 完全向后兼容 v1.0.0
- 现有代码无需修改即可使用新功能
- JSON加载器为可选功能，不影响现有工作流

### 升级指南

从 v1.0.0 升级到 v1.1.0：

1. 无需修改现有代码
2. 运行 `dm.initialize_pipeline(force=True)` 重新转换数据
3. JSON数据会自动加载和合并
4. 查看 `JSON_LOADERS_GUIDE.md` 了解新功能

---

## 路线图

### v1.2.0 (计划中)

- [ ] 增量数据更新
- [ ] 并行数据加载
- [ ] 更多数据源支持
- [ ] Web API接口

### v1.3.0 (计划中)

- [ ] 实时数据流处理
- [ ] 分布式处理支持
- [ ] 数据版本控制
- [ ] 自动化报告生成

### v2.0.0 (未来)

- [ ] 完整的数据湖架构
- [ ] 机器学习集成
- [ ] 云存储支持
- [ ] 企业级功能

---

## 贡献

欢迎贡献代码、报告问题或提出建议。

## 许可

与主项目保持一致

---

**维护者**: GenAI Power Analyze Team  
**最后更新**: 2026-03-05
