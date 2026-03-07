# Design Document: QE Research Scripts Refactoring

## Overview

This design refactors the `analysis/qe_research/scripts` directory from a collection of loosely organized scripts into a well-structured, modular analysis framework. The refactoring eliminates code duplication, establishes clear architectural patterns, and provides reusable components while maintaining backward compatibility.

## Architecture

### High-Level Structure

```
analysis/qe_research/scripts/
├── core/                      # Core analysis modules
│   ├── __init__.py
│   ├── base_analyzer.py       # Base analyzer class
│   ├── data_loader.py         # Data loading utilities
│   ├── metrics.py             # Metric calculations
│   ├── visualization.py       # Visualization utilities
│   └── report_generator.py    # Report generation
├── analyzers/                 # Specific analyzer implementations
│   ├── __init__.py
│   ├── pareto_analyzer.py     # Pareto frontier analysis
│   ├── quality_analyzer.py    # Quality analysis
│   ├── raw_data_analyzer.py   # Raw data analysis
│   ├── power_analyzer.py      # Power/energy analysis
│   └── comprehensive_analyzer.py  # Comprehensive analysis
├── pareto/                    # Pareto-specific modules
│   ├── __init__.py
│   ├── frontier.py            # Frontier identification
│   ├── metrics_calculator.py  # Quantitative metrics
│   ├── robustness.py          # Robustness analysis
│   └── entropy_weight.py      # Entropy weight method
├── utils/                     # Utility functions
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── logging_utils.py       # Logging setup
│   ├── file_utils.py          # File operations
│   └── model_mapping.py       # Model name mapping
├── cli/                       # Command-line interfaces
│   ├── __init__.py
│   ├── analyze_pareto.py      # Pareto analysis CLI
│   ├── analyze_quality.py     # Quality analysis CLI
│   ├── analyze_raw.py         # Raw data analysis CLI
│   ├── analyze_comprehensive.py  # Comprehensive analysis CLI
│   └── common_args.py         # Common CLI arguments
├── batch/                     # Batch execution scripts
│   ├── run_pareto_analysis.bat
│   ├── run_quality_analysis.bat
│   ├── run_raw_analysis.bat
│   └── run_all_analyses.bat
├── tests/                     # Test files
│   ├── __init__.py
│   ├── test_analyzers.py
│   ├── test_pareto.py
│   ├── test_data_loader.py
│   └── fixtures/
└── README.md                  # Documentation
```

## Components and Interfaces

### 1. Core Module (`core/`)

#### 1.1 Base Analyzer (`base_analyzer.py`)

```python
class BaseAnalyzer:
    """Base class for all analyzers"""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration"""
        self.config = config
        self.data = None
        self.results = {}
        self.logger = setup_logger(self.__class__.__name__)
    
    def load_data(self, **kwargs) -> pd.DataFrame:
        """Load data - to be implemented by subclasses"""
        raise NotImplementedError
    
    def analyze(self) -> Dict[str, Any]:
        """Perform analysis - to be implemented by subclasses"""
        raise NotImplementedError
    
    def visualize(self, output_dir: Path) -> List[Path]:
        """Generate visualizations - to be implemented by subclasses"""
        raise NotImplementedError
    
    def generate_report(self, output_dir: Path) -> Path:
        """Generate analysis report"""
        raise NotImplementedError
    
    def run(self, output_dir: Path = None) -> Dict[str, Any]:
        """Complete analysis pipeline"""
        self.logger.info(f"Starting {self.__class__.__name__}")
        
        # Load data
        self.load_data()
        
        # Perform analysis
        self.results = self.analyze()
        
        # Generate outputs
        if output_dir:
            self.visualize(output_dir)
            self.generate_report(output_dir)
        
        return self.results
```

#### 1.2 Data Loader (`data_loader.py`)

```python
class DataLoader:
    """Unified data loading interface"""
    
    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.model_mapper = ModelNameMapper()
    
    def load_quality_data(self, task: str) -> pd.DataFrame:
        """Load quality evaluation data for a task"""
        pass
    
    def load_energy_data(self, task: str = None) -> pd.DataFrame:
        """Load energy consumption data"""
        pass
    
    def load_speed_data(self, task: str = None) -> pd.DataFrame:
        """Load token speed data"""
        pass
    
    def load_raw_results(self, experiment_dir: Path) -> pd.DataFrame:
        """Load raw experimental results"""
        pass
    
    def merge_datasets(self, *dfs: pd.DataFrame, on: str = 'model') -> pd.DataFrame:
        """Merge multiple datasets"""
        pass
```

#### 1.3 Metrics Calculator (`metrics.py`)

```python
class MetricsCalculator:
    """Calculate various metrics"""
    
    @staticmethod
    def normalize(data: pd.Series, method: str = 'minmax') -> pd.Series:
        """Normalize data"""
        pass
    
    @staticmethod
    def calculate_efficiency_score(throughput: pd.Series, 
                                   latency: pd.Series,
                                   energy: pd.Series,
                                   weights: Dict[str, float] = None) -> pd.Series:
        """Calculate efficiency score"""
        pass
    
    @staticmethod
    def calculate_qe_ratio(quality: pd.Series, 
                          efficiency: pd.Series) -> pd.Series:
        """Calculate quality-efficiency ratio"""
        pass
    
    @staticmethod
    def calculate_fairness_gap(data: pd.DataFrame, 
                              group_col: str,
                              metric_col: str) -> float:
        """Calculate fairness gap across groups"""
        pass
```

#### 1.4 Visualization (`visualization.py`)

```python
class Visualizer:
    """Unified visualization interface"""
    
    def __init__(self, style: str = 'academic'):
        self.setup_style(style)
    
    def setup_style(self, style: str):
        """Setup matplotlib style"""
        pass
    
    def plot_scatter(self, x: pd.Series, y: pd.Series, 
                    labels: pd.Series = None, **kwargs) -> plt.Figure:
        """Create scatter plot"""
        pass
    
    def plot_bar(self, data: pd.DataFrame, **kwargs) -> plt.Figure:
        """Create bar plot"""
        pass
    
    def plot_radar(self, data: pd.DataFrame, **kwargs) -> plt.Figure:
        """Create radar chart"""
        pass
    
    def plot_heatmap(self, data: pd.DataFrame, **kwargs) -> plt.Figure:
        """Create heatmap"""
        pass
    
    def save_figure(self, fig: plt.Figure, path: Path, **kwargs):
        """Save figure with consistent settings"""
        pass
```

#### 1.5 Report Generator (`report_generator.py`)

```python
class ReportGenerator:
    """Generate markdown reports"""
    
    def __init__(self, template_dir: Path = None):
        self.template_dir = template_dir
    
    def generate_report(self, 
                       title: str,
                       sections: List[Dict[str, Any]],
                       output_path: Path):
        """Generate complete report"""
        pass
    
    def add_section(self, title: str, content: str) -> Dict[str, Any]:
        """Create report section"""
        pass
    
    def add_table(self, df: pd.DataFrame, caption: str = None) -> str:
        """Format dataframe as markdown table"""
        pass
    
    def add_figure(self, figure_path: Path, caption: str = None) -> str:
        """Add figure reference"""
        pass
```

### 2. Analyzers Module (`analyzers/`)

#### 2.1 Pareto Analyzer (`pareto_analyzer.py`)

```python
class ParetoAnalyzer(BaseAnalyzer):
    """Pareto frontier analysis"""
    
    def __init__(self, task: str, config: Dict[str, Any]):
        super().__init__(config)
        self.task = task
        self.frontier_identifier = ParetoFrontierIdentifier()
        self.metrics_calc = QuantitativeMetricsCalculator()
        self.robustness = RobustnessAnalyzer()
    
    def load_data(self, quality_file: Path = None, 
                  energy_file: Path = None,
                  speed_file: Path = None):
        """Load data for pareto analysis"""
        loader = DataLoader(self.config['data_root'])
        
        # Load and merge datasets
        quality_df = loader.load_quality_data(self.task) if not quality_file else pd.read_csv(quality_file)
        energy_df = loader.load_energy_data(self.task) if not energy_file else pd.read_csv(energy_file)
        speed_df = loader.load_speed_data(self.task) if not speed_file else pd.read_csv(speed_file)
        
        self.data = loader.merge_datasets(quality_df, energy_df, speed_df)
        return self.data
    
    def analyze(self) -> Dict[str, Any]:
        """Perform pareto analysis"""
        results = {}
        
        # 2D Pareto frontier (quality vs energy)
        results['pareto_2d'] = self.frontier_identifier.identify_2d(
            self.data, 'quality', 'energy'
        )
        
        # 3D Pareto frontier (quality vs energy vs speed)
        if 'speed' in self.data.columns:
            results['pareto_3d'] = self.frontier_identifier.identify_3d(
                self.data, 'quality', 'energy', 'speed'
            )
        
        # Quantitative metrics
        results['metrics'] = self.metrics_calc.calculate_all(
            self.data, results['pareto_2d']
        )
        
        # Robustness analysis
        results['robustness'] = self.robustness.analyze(
            self.data, results['pareto_2d']
        )
        
        return results
    
    def visualize(self, output_dir: Path) -> List[Path]:
        """Generate visualizations"""
        figures = []
        visualizer = Visualizer(self.config.get('style', 'academic'))
        
        # 2D Pareto plot
        fig = visualizer.plot_pareto_2d(
            self.data, self.results['pareto_2d']
        )
        path = output_dir / 'figures' / f'{self.task}_pareto_2d.png'
        visualizer.save_figure(fig, path)
        figures.append(path)
        
        # 3D Pareto plot (if available)
        if 'pareto_3d' in self.results:
            fig = visualizer.plot_pareto_3d(
                self.data, self.results['pareto_3d']
            )
            path = output_dir / 'figures' / f'{self.task}_pareto_3d.png'
            visualizer.save_figure(fig, path)
            figures.append(path)
        
        return figures
    
    def generate_report(self, output_dir: Path) -> Path:
        """Generate analysis report"""
        generator = ReportGenerator()
        
        sections = [
            generator.add_section("Overview", self._generate_overview()),
            generator.add_section("Pareto Frontier", self._generate_frontier_section()),
            generator.add_section("Quantitative Metrics", self._generate_metrics_section()),
            generator.add_section("Robustness Analysis", self._generate_robustness_section())
        ]
        
        report_path = output_dir / 'reports' / f'{self.task}_pareto_report.md'
        generator.generate_report(
            title=f"Pareto Analysis: {self.task.title()}",
            sections=sections,
            output_path=report_path
        )
        
        return report_path
```

#### 2.2 Quality Analyzer (`quality_analyzer.py`)

```python
class QualityAnalyzer(BaseAnalyzer):
    """Quality evaluation analysis"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.task_types = []
        self.quality_data = {}
    
    def load_data(self, tasks: List[str] = None):
        """Load quality data for specified tasks"""
        loader = DataLoader(self.config['data_root'])
        
        if tasks is None:
            # Auto-discover available tasks
            tasks = self._discover_tasks()
        
        for task in tasks:
            self.quality_data[task] = loader.load_quality_data(task)
            self.task_types.append(task)
        
        return self.quality_data
    
    def analyze(self) -> Dict[str, Any]:
        """Perform quality analysis"""
        results = {}
        
        # Exploratory analysis
        results['exploratory'] = self._exploratory_analysis()
        
        # Model comparison
        results['comparison'] = self._model_comparison()
        
        # Task-specific analysis
        results['task_specific'] = self._task_specific_analysis()
        
        # Submetric correlation
        results['correlation'] = self._submetric_correlation()
        
        # Stability analysis
        results['stability'] = self._stability_analysis()
        
        # Cross-task evaluation
        results['cross_task'] = self._cross_task_evaluation()
        
        return results
```

#### 2.3 Raw Data Analyzer (`raw_data_analyzer.py`)

```python
class RawDataAnalyzer(BaseAnalyzer):
    """Raw experimental data analysis"""
    
    def __init__(self, experiment_dir: Path, config: Dict[str, Any]):
        super().__init__(config)
        self.experiment_dir = experiment_dir
    
    def load_data(self):
        """Load raw experimental results"""
        loader = DataLoader(self.config['data_root'])
        self.data = loader.load_raw_results(self.experiment_dir)
        return self.data
    
    def analyze(self) -> Dict[str, Any]:
        """Analyze raw data"""
        results = {}
        
        # Basic statistics
        results['statistics'] = self._calculate_statistics()
        
        # Performance metrics
        results['performance'] = self._analyze_performance()
        
        # Energy analysis
        results['energy'] = self._analyze_energy()
        
        # Quality metrics
        results['quality'] = self._analyze_quality()
        
        return results
```

### 3. Pareto Module (`pareto/`)

#### 3.1 Frontier Identifier (`frontier.py`)

```python
class ParetoFrontierIdentifier:
    """Identify Pareto-optimal solutions"""
    
    def identify_2d(self, data: pd.DataFrame, 
                   objective1: str, objective2: str,
                   maximize: List[bool] = [True, False]) -> pd.DataFrame:
        """Identify 2D Pareto frontier"""
        pass
    
    def identify_3d(self, data: pd.DataFrame,
                   objective1: str, objective2: str, objective3: str,
                   maximize: List[bool] = [True, False, True]) -> pd.DataFrame:
        """Identify 3D Pareto frontier"""
        pass
    
    def is_dominated(self, point: np.ndarray, 
                    other_points: np.ndarray,
                    maximize: List[bool]) -> bool:
        """Check if a point is dominated"""
        pass
```

#### 3.2 Quantitative Metrics Calculator (`metrics_calculator.py`)

```python
class QuantitativeMetricsCalculator:
    """Calculate quantitative metrics for Pareto analysis"""
    
    def calculate_all(self, data: pd.DataFrame, 
                     pareto_front: pd.DataFrame) -> Dict[str, float]:
        """Calculate all metrics"""
        return {
            'hypervolume': self.calculate_hypervolume(pareto_front),
            'spacing': self.calculate_spacing(pareto_front),
            'spread': self.calculate_spread(pareto_front),
            'marginal_benefit': self.calculate_marginal_benefit(pareto_front),
            'knee_point': self.identify_knee_point(pareto_front)
        }
    
    def calculate_hypervolume(self, pareto_front: pd.DataFrame) -> float:
        """Calculate hypervolume indicator"""
        pass
    
    def calculate_spacing(self, pareto_front: pd.DataFrame) -> float:
        """Calculate spacing metric"""
        pass
    
    def calculate_spread(self, pareto_front: pd.DataFrame) -> float:
        """Calculate spread metric"""
        pass
    
    def calculate_marginal_benefit(self, pareto_front: pd.DataFrame) -> pd.DataFrame:
        """Calculate marginal benefit between consecutive points"""
        pass
    
    def identify_knee_point(self, pareto_front: pd.DataFrame) -> Dict[str, Any]:
        """Identify knee point (best trade-off)"""
        pass
```

#### 3.3 Robustness Analyzer (`robustness.py`)

```python
class RobustnessAnalyzer:
    """Analyze robustness of Pareto frontier"""
    
    def analyze(self, data: pd.DataFrame, 
               pareto_front: pd.DataFrame) -> Dict[str, Any]:
        """Complete robustness analysis"""
        return {
            'perturbation': self.perturbation_analysis(data, pareto_front),
            'weight_sensitivity': self.weight_sensitivity_analysis(data),
            'cross_validation': self.cross_validation_analysis(data)
        }
    
    def perturbation_analysis(self, data: pd.DataFrame,
                            pareto_front: pd.DataFrame,
                            noise_levels: List[float] = [0.05, 0.10, 0.15]) -> Dict:
        """Analyze stability under data perturbation"""
        pass
    
    def weight_sensitivity_analysis(self, data: pd.DataFrame,
                                   weight_range: tuple = (0.3, 0.7)) -> Dict:
        """Analyze sensitivity to weight changes"""
        pass
    
    def cross_validation_analysis(self, data: pd.DataFrame,
                                 n_folds: int = 5) -> Dict:
        """Cross-validation analysis"""
        pass
```

#### 3.4 Entropy Weight Calculator (`entropy_weight.py`)

```python
class EntropyWeightCalculator:
    """Calculate weights using entropy method"""
    
    def calculate_weights(self, data: pd.DataFrame,
                         quality_columns: List[str]) -> Dict[str, float]:
        """Calculate entropy weights for quality dimensions"""
        pass
    
    def calculate_composite_score(self, data: pd.DataFrame,
                                 weights: Dict[str, float]) -> pd.Series:
        """Calculate composite quality score"""
        pass
```

### 4. Utils Module (`utils/`)

#### 4.1 Configuration Manager (`config.py`)

```python
class ConfigManager:
    """Manage configuration"""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path('analysis/qe_research/configs/analysis_config.yaml')
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML"""
        pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        pass
    
    def validate(self) -> bool:
        """Validate configuration"""
        pass
```

#### 4.2 Model Name Mapper (`model_mapping.py`)

```python
class ModelNameMapper:
    """Map between different model naming conventions"""
    
    def __init__(self):
        self.mapping = self._load_mapping()
    
    def _load_mapping(self) -> Dict[str, str]:
        """Load model name mapping"""
        return {
            'deepseek_8b_ol_q4km': 'deepseek-r1:8b',
            'gemma_2b_hf_4bit': 'google--gemma-2b-it:4bit',
            # ... more mappings
        }
    
    def to_full_name(self, short_name: str) -> str:
        """Convert short name to full name"""
        pass
    
    def to_short_name(self, full_name: str) -> str:
        """Convert full name to short name"""
        pass
    
    def normalize(self, name: str) -> str:
        """Normalize model name"""
        pass
```

### 5. CLI Module (`cli/`)

#### 5.1 Common Arguments (`common_args.py`)

```python
def add_common_arguments(parser: argparse.ArgumentParser):
    """Add common CLI arguments"""
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--output-dir', type=str, help='Output directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--log-file', type=str, help='Log file path')
    return parser
```

#### 5.2 Pareto Analysis CLI (`analyze_pareto.py`)

```python
def main():
    parser = argparse.ArgumentParser(description='Pareto Frontier Analysis')
    parser.add_argument('--task', required=True, choices=['code', 'creative', 'qa', 'reasoning', 'summary', 'translation', 'math'])
    parser.add_argument('--quality-file', type=str, help='Quality data file')
    parser.add_argument('--energy-file', type=str, help='Energy data file')
    parser.add_argument('--speed-file', type=str, help='Speed data file')
    parser = add_common_arguments(parser)
    
    args = parser.parse_args()
    
    # Load configuration
    config = ConfigManager(args.config).config
    
    # Create analyzer
    analyzer = ParetoAnalyzer(args.task, config)
    
    # Run analysis
    analyzer.run(output_dir=Path(args.output_dir or config['output_dir']))
```

## Data Models

### Analysis Configuration

```yaml
# analysis_config.yaml
data_root: "data/analize"
output_root: "analysis/qe_research/results"

normalization:
  method: "minmax"  # minmax, zscore, robust

efficiency_weights:
  throughput: 0.4
  latency: 0.3
  energy: 0.3

visualization:
  style: "academic"
  dpi: 300
  format: "png"
  colors:
    - "#0173B2"
    - "#DE8F05"
    - "#029E73"
    - "#CC78BC"

pareto:
  perturbation_levels: [0.05, 0.10, 0.15]
  weight_sensitivity_range: [0.3, 0.7]
  cross_validation_folds: 5

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Analyzer Results Schema

```python
@dataclass
class AnalysisResults:
    """Standard results structure"""
    analyzer_name: str
    timestamp: datetime
    data_summary: Dict[str, Any]
    metrics: Dict[str, float]
    figures: List[Path]
    tables: List[Path]
    report_path: Path
    metadata: Dict[str, Any]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Property 1: Module Initialization
*For any* module directory in the refactored structure, it should contain an `__init__.py` file that exports the expected public symbols.
**Validates: Requirements 1.2**

### Property 2: Separation of CLI and Logic
*For any* file in the `cli/` directory, it should not contain analysis logic (class definitions for analyzers), but should only contain argument parsing and analyzer invocation.
**Validates: Requirements 1.3**

### Property 3: Data Loading Separation
*For any* analyzer class, its analysis methods should not directly read files using `pd.read_csv()` or similar, but should use the `DataLoader` class.
**Validates: Requirements 1.4**

### Property 4: Visualization Separation
*For any* analyzer's `analyze()` method, it should return data structures (DataFrames, dicts) and not create matplotlib figures directly.
**Validates: Requirements 1.5**

### Property 5: Analyzer Inheritance
*For any* analyzer class in the `analyzers/` module, it should inherit from `BaseAnalyzer`.
**Validates: Requirements 2.2**

### Property 6: Unified Analyzer Interface
*For any* analyzer class, it should implement the methods: `load_data()`, `analyze()`, `visualize()`, `generate_report()`, and `run()`.
**Validates: Requirements 2.5**

### Property 7: Snake Case Naming
*For any* Python file in the refactored structure, its filename should follow snake_case convention (lowercase with underscores).
**Validates: Requirements 4.1**

### Property 8: No Version Suffixes
*For any* Python file in the refactored structure, its filename should not contain version suffixes like "_enhanced", "_v2", "_complete", or similar patterns.
**Validates: Requirements 4.3**

### Property 9: CLI Naming Convention
*For any* file in the `cli/` directory, its filename should start with a verb prefix like "analyze_", "compute_", or "run_".
**Validates: Requirements 4.4, 4.5**

### Property 10: Unified Configuration Loading
*For any* analyzer instance, when it loads configuration, it should load from the path specified in `configs/analysis_config.yaml`.
**Validates: Requirements 5.1, 5.2**

### Property 11: Configuration Defaults
*For any* configuration key, if it's missing from the config file, the system should provide a sensible default value rather than raising an error.
**Validates: Requirements 5.3**

### Property 12: Configuration Validation
*For any* invalid configuration value (e.g., negative weights, invalid paths), the ConfigManager should raise a `ValueError` with a descriptive message.
**Validates: Requirements 5.4**

### Property 13: Analyzer Composition
*For any* two analyzers A and B, if A produces output in the standard `AnalysisResults` format, then B should be able to consume that output as input.
**Validates: Requirements 6.3**

### Property 14: Test Structure Mirroring
*For any* module file `core/module_name.py`, there should exist a corresponding test file `tests/test_module_name.py`.
**Validates: Requirements 7.2**

### Property 15: CLI Argparse Usage
*For any* CLI script in the `cli/` directory, it should import `argparse` and use `ArgumentParser` for command-line argument handling.
**Validates: Requirements 8.1**

### Property 16: Common CLI Arguments
*For any* CLI script, it should accept the common arguments: `--config`, `--output-dir`, and `--verbose`.
**Validates: Requirements 8.2, 8.3**

### Property 17: CLI Help Documentation
*For any* CLI script, running it with the `--help` flag should display usage information without raising an error.
**Validates: Requirements 8.5**

### Property 18: Output Location Consistency
*For any* analyzer, when it generates outputs (figures, tables, reports), they should be written to subdirectories under the configured `output_root` path.
**Validates: Requirements 9.3**

### Property 19: Deprecation Warnings
*For any* deprecated function or class, calling it should emit a `DeprecationWarning` with information about the replacement.
**Validates: Requirements 9.4**

### Property 20: Docstring Coverage
*For any* public function or class (not starting with underscore), it should have a docstring that describes its purpose, parameters, and return value.
**Validates: Requirements 10.2, 10.4**

## Error Handling

### Error Categories

1. **Configuration Errors**
   - Missing configuration file
   - Invalid configuration values
   - Missing required configuration keys

2. **Data Loading Errors**
   - Missing data files
   - Malformed data files
   - Incompatible data schemas

3. **Analysis Errors**
   - Insufficient data for analysis
   - Numerical errors (division by zero, NaN values)
   - Algorithm convergence failures

4. **I/O Errors**
   - Permission denied for output directories
   - Disk space issues
   - File system errors

### Error Handling Strategy

```python
class AnalysisError(Exception):
    """Base exception for analysis errors"""
    pass

class ConfigurationError(AnalysisError):
    """Configuration-related errors"""
    pass

class DataLoadingError(AnalysisError):
    """Data loading errors"""
    pass

class InsufficientDataError(AnalysisError):
    """Not enough data for analysis"""
    pass
```

All analyzers should:
1. Catch specific exceptions and provide helpful error messages
2. Log errors with full context
3. Clean up resources (close files, clear memory) on error
4. Provide suggestions for fixing common errors

## Testing Strategy

### Unit Tests

Unit tests verify specific components in isolation:

- **Core Module Tests**: Test each utility function and class
  - `test_base_analyzer.py`: Test BaseAnalyzer interface
  - `test_data_loader.py`: Test data loading with mock files
  - `test_metrics.py`: Test metric calculations with known inputs
  - `test_visualization.py`: Test plot generation
  - `test_report_generator.py`: Test report formatting

- **Analyzer Tests**: Test each analyzer type
  - `test_pareto_analyzer.py`: Test pareto analysis logic
  - `test_quality_analyzer.py`: Test quality analysis
  - `test_raw_data_analyzer.py`: Test raw data processing

- **Pareto Module Tests**: Test pareto-specific functionality
  - `test_frontier.py`: Test frontier identification algorithms
  - `test_metrics_calculator.py`: Test quantitative metrics
  - `test_robustness.py`: Test robustness analysis
  - `test_entropy_weight.py`: Test entropy weight calculation

- **Utils Tests**: Test utility functions
  - `test_config.py`: Test configuration loading and validation
  - `test_model_mapping.py`: Test model name mapping
  - `test_file_utils.py`: Test file operations

### Property-Based Tests

Property tests verify universal properties across many generated inputs:

- **Property 1: Module Initialization** (100 iterations)
  - Generate random module structures
  - Verify all contain `__init__.py`
  - **Feature: qe-research-scripts-refactoring, Property 1: Module Initialization**

- **Property 2: Analyzer Inheritance** (100 iterations)
  - Test all analyzer classes
  - Verify they inherit from BaseAnalyzer
  - **Feature: qe-research-scripts-refactoring, Property 5: Analyzer Inheritance**

- **Property 3: Configuration Defaults** (100 iterations)
  - Generate configs with random missing keys
  - Verify system provides defaults
  - **Feature: qe-research-scripts-refactoring, Property 11: Configuration Defaults**

- **Property 4: Analyzer Composition** (100 iterations)
  - Generate random analyzer chains
  - Verify outputs can be chained as inputs
  - **Feature: qe-research-scripts-refactoring, Property 13: Analyzer Composition**

- **Property 5: Docstring Coverage** (100 iterations)
  - Scan all public symbols
  - Verify they have docstrings
  - **Feature: qe-research-scripts-refactoring, Property 20: Docstring Coverage**

### Integration Tests

Integration tests verify end-to-end workflows:

- **Test Complete Pareto Analysis**: Run full pareto analysis pipeline
- **Test Complete Quality Analysis**: Run full quality analysis pipeline
- **Test Batch Processing**: Run multiple analyses in sequence
- **Test CLI Interfaces**: Test all CLI scripts with various arguments
- **Test Backward Compatibility**: Verify old batch files still work

### Test Configuration

All property-based tests should:
- Run minimum 100 iterations
- Use deterministic random seeds for reproducibility
- Log failing examples for debugging
- Reference design document properties in comments

### Test Execution

```bash
# Run all tests
pytest tests/ -v

# Run unit tests only
pytest tests/test_*.py -v

# Run property tests only
pytest tests/ -v -m property

# Run integration tests only
pytest tests/ -v -m integration

# Run with coverage
pytest tests/ --cov=analysis/qe_research/scripts --cov-report=html
```

## Migration Strategy

### Phase 1: Create New Structure (Week 1)

1. Create new directory structure
2. Implement core modules (base_analyzer, data_loader, etc.)
3. Implement utils modules (config, logging, model_mapping)
4. Write unit tests for core functionality

### Phase 2: Migrate Analyzers (Week 2)

1. Implement ParetoAnalyzer using new architecture
2. Implement QualityAnalyzer using new architecture
3. Implement RawDataAnalyzer using new architecture
4. Write tests for each analyzer

### Phase 3: Create CLI Interfaces (Week 3)

1. Implement CLI scripts for each analyzer
2. Create batch files that call new CLI scripts
3. Add backward compatibility layer
4. Test all CLI interfaces

### Phase 4: Documentation and Testing (Week 4)

1. Write comprehensive README files
2. Create migration guide
3. Write integration tests
4. Perform end-to-end testing

### Phase 5: Deprecation (Week 5-6)

1. Add deprecation warnings to old scripts
2. Update all documentation to reference new structure
3. Notify users of changes
4. Monitor for issues

### Backward Compatibility

Old batch files will be updated to call new CLI scripts:

```batch
@echo off
REM run_pareto_analysis.bat - Backward compatibility wrapper
echo [DEPRECATED] This script is deprecated. Use: python cli/analyze_pareto.py
python analysis/qe_research/scripts/cli/analyze_pareto.py %*
```

Old Python scripts will remain but emit deprecation warnings:

```python
# pareto_analysis_code.py - Deprecated
import warnings
warnings.warn(
    "pareto_analysis_code.py is deprecated. Use: python cli/analyze_pareto.py --task code",
    DeprecationWarning,
    stacklevel=2
)

# Import and run new implementation
from cli.analyze_pareto import main
main()
```

## Performance Considerations

1. **Lazy Loading**: Load data only when needed
2. **Caching**: Cache expensive computations (entropy weights, pareto frontiers)
3. **Parallel Processing**: Use multiprocessing for independent analyses
4. **Memory Management**: Process large datasets in chunks
5. **Profiling**: Include profiling hooks for performance monitoring

## Security Considerations

1. **Path Validation**: Validate all file paths to prevent directory traversal
2. **Input Sanitization**: Sanitize user inputs in CLI arguments
3. **Configuration Validation**: Validate configuration values
4. **Resource Limits**: Set limits on memory and computation time
5. **Logging**: Avoid logging sensitive information

## Future Extensions

1. **Plugin System**: Allow users to register custom analyzers
2. **Web Interface**: Create web-based dashboard for analysis
3. **Real-time Analysis**: Support streaming data analysis
4. **Distributed Computing**: Support distributed analysis across multiple machines
5. **Export Formats**: Support additional export formats (JSON, Excel, LaTeX)
