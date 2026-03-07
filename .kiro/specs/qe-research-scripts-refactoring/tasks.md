# Implementation Plan: QE Research Scripts Refactoring

## Overview

This implementation plan refactors the `analysis/qe_research/scripts` directory into a well-structured, modular analysis framework. Tasks are organized to build incrementally, with testing integrated throughout.

## Tasks

- [ ] 1. Setup new directory structure and core infrastructure
  - Create new directory structure (core/, analyzers/, pareto/, utils/, cli/, batch/, tests/)
  - Setup logging configuration
  - Create base __init__.py files for all modules
  - _Requirements: 1.1, 3.1, 3.2_

- [ ] 2. Implement core utilities module
  - [ ] 2.1 Implement ConfigManager class
    - Load YAML configuration
    - Provide default values for missing keys
    - Validate configuration values
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 2.2 Write property test for ConfigManager
    - **Property 11: Configuration Defaults**
    - **Validates: Requirements 5.3**

  - [ ]* 2.3 Write property test for configuration validation
    - **Property 12: Configuration Validation**
    - **Validates: Requirements 5.4**

  - [ ] 2.4 Implement ModelNameMapper class
    - Load model name mappings
    - Convert between naming conventions
    - Normalize model names
    - _Requirements: 2.3_

  - [ ]* 2.5 Write unit tests for ModelNameMapper
    - Test name conversions
    - Test normalization
    - _Requirements: 2.3_

  - [ ] 2.6 Implement logging utilities
    - Setup logger with file and console handlers
    - Configure log formatting
    - _Requirements: 1.1_

  - [ ] 2.7 Implement file utilities
    - Path validation functions
    - Directory creation helpers
    - _Requirements: 1.1_

- [ ] 3. Implement core analysis module
  - [ ] 3.1 Implement BaseAnalyzer class
    - Define abstract interface (load_data, analyze, visualize, generate_report, run)
    - Implement common initialization
    - Implement run() pipeline method
    - _Requirements: 2.2, 6.1_

  - [ ]* 3.2 Write property test for analyzer interface
    - **Property 6: Unified Analyzer Interface**
    - **Validates: Requirements 2.5**

  - [ ] 3.3 Implement DataLoader class
    - Load quality data by task
    - Load energy data
    - Load speed data
    - Load raw experimental results
    - Merge datasets with model name mapping
    - _Requirements: 1.4_

  - [ ]* 3.4 Write property test for data loading separation
    - **Property 3: Data Loading Separation**
    - **Validates: Requirements 1.4**

  - [ ]* 3.5 Write unit tests for DataLoader
    - Test loading each data type
    - Test dataset merging
    - Test error handling for missing files
    - _Requirements: 1.4_

  - [ ] 3.6 Implement MetricsCalculator class
    - Normalization methods (minmax, zscore, robust)
    - Efficiency score calculation
    - QE ratio calculation
    - Fairness gap calculation
    - _Requirements: 1.1_

  - [ ]* 3.7 Write unit tests for MetricsCalculator
    - Test normalization with known inputs
    - Test efficiency score calculation
    - Test QE ratio calculation
    - _Requirements: 1.1_

  - [ ] 3.8 Implement Visualizer class
    - Setup matplotlib style
    - Scatter plot method
    - Bar plot method
    - Radar chart method
    - Heatmap method
    - Figure saving with consistent settings
    - _Requirements: 1.5_

  - [ ]* 3.9 Write property test for visualization separation
    - **Property 4: Visualization Separation**
    - **Validates: Requirements 1.5**

  - [ ]* 3.10 Write unit tests for Visualizer
    - Test each plot type generation
    - Test figure saving
    - _Requirements: 1.5_

  - [ ] 3.11 Implement ReportGenerator class
    - Generate markdown reports from sections
    - Format dataframes as markdown tables
    - Add figure references
    - _Requirements: 1.1_

  - [ ]* 3.12 Write unit tests for ReportGenerator
    - Test report generation
    - Test table formatting
    - Test figure references
    - _Requirements: 1.1_

- [ ] 4. Checkpoint - Core modules complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Implement pareto analysis module
  - [ ] 5.1 Implement ParetoFrontierIdentifier class
    - 2D pareto frontier identification
    - 3D pareto frontier identification
    - Dominance checking
    - _Requirements: 6.2_

  - [ ]* 5.2 Write unit tests for ParetoFrontierIdentifier
    - Test 2D frontier with known data
    - Test 3D frontier with known data
    - Test dominance checking
    - _Requirements: 6.2_

  - [ ] 5.3 Implement QuantitativeMetricsCalculator class
    - Hypervolume calculation
    - Spacing metric
    - Spread metric
    - Marginal benefit calculation
    - Knee point identification
    - _Requirements: 6.2_

  - [ ]* 5.4 Write unit tests for QuantitativeMetricsCalculator
    - Test each metric with known inputs
    - Test knee point identification
    - _Requirements: 6.2_

  - [ ] 5.5 Implement RobustnessAnalyzer class
    - Perturbation analysis
    - Weight sensitivity analysis
    - Cross-validation analysis
    - _Requirements: 6.2_

  - [ ]* 5.6 Write unit tests for RobustnessAnalyzer
    - Test perturbation analysis
    - Test weight sensitivity
    - Test cross-validation
    - _Requirements: 6.2_

  - [ ] 5.7 Implement EntropyWeightCalculator class
    - Calculate entropy weights
    - Calculate composite scores
    - _Requirements: 6.2_

  - [ ]* 5.8 Write unit tests for EntropyWeightCalculator
    - Test weight calculation
    - Test composite score calculation
    - _Requirements: 6.2_

- [ ] 6. Implement analyzer classes
  - [ ] 6.1 Implement ParetoAnalyzer class
    - Inherit from BaseAnalyzer
    - Implement load_data() using DataLoader
    - Implement analyze() using pareto modules
    - Implement visualize() using Visualizer
    - Implement generate_report() using ReportGenerator
    - _Requirements: 6.2, 2.2_

  - [ ]* 6.2 Write property test for analyzer inheritance
    - **Property 5: Analyzer Inheritance**
    - **Validates: Requirements 2.2**

  - [ ]* 6.3 Write unit tests for ParetoAnalyzer
    - Test data loading
    - Test analysis execution
    - Test visualization generation
    - Test report generation
    - _Requirements: 6.2_

  - [ ] 6.4 Implement QualityAnalyzer class
    - Inherit from BaseAnalyzer
    - Implement load_data() for multiple tasks
    - Implement analyze() with exploratory, comparison, correlation analyses
    - Implement visualize() for quality metrics
    - Implement generate_report()
    - _Requirements: 6.2, 2.2_

  - [ ]* 6.5 Write unit tests for QualityAnalyzer
    - Test multi-task data loading
    - Test analysis methods
    - _Requirements: 6.2_

  - [ ] 6.6 Implement RawDataAnalyzer class
    - Inherit from BaseAnalyzer
    - Implement load_data() for raw experimental results
    - Implement analyze() for statistics, performance, energy, quality
    - Implement visualize() and generate_report()
    - _Requirements: 6.2, 2.2_

  - [ ]* 6.7 Write unit tests for RawDataAnalyzer
    - Test raw data loading
    - Test analysis methods
    - _Requirements: 6.2_

  - [ ] 6.8 Implement ComprehensiveAnalyzer class
    - Inherit from BaseAnalyzer
    - Compose multiple analyzers
    - Generate comprehensive report
    - _Requirements: 6.2, 6.3_

  - [ ]* 6.9 Write property test for analyzer composition
    - **Property 13: Analyzer Composition**
    - **Validates: Requirements 6.3**

- [ ] 7. Checkpoint - Analyzers complete
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement CLI interfaces
  - [ ] 8.1 Implement common_args module
    - Define add_common_arguments() function
    - Add --config, --output-dir, --verbose, --log-file arguments
    - _Requirements: 8.2, 8.3_

  - [ ] 8.2 Implement analyze_pareto.py CLI
    - Parse arguments using argparse
    - Load configuration
    - Create and run ParetoAnalyzer
    - Handle errors gracefully
    - _Requirements: 8.1, 1.3_

  - [ ]* 8.3 Write property test for CLI separation
    - **Property 2: Separation of CLI and Logic**
    - **Validates: Requirements 1.3**

  - [ ]* 8.4 Write property test for CLI argparse usage
    - **Property 15: CLI Argparse Usage**
    - **Validates: Requirements 8.1**

  - [ ]* 8.5 Write property test for common CLI arguments
    - **Property 16: Common CLI Arguments**
    - **Validates: Requirements 8.2, 8.3**

  - [ ]* 8.6 Write property test for CLI help documentation
    - **Property 17: CLI Help Documentation**
    - **Validates: Requirements 8.5**

  - [ ] 8.7 Implement analyze_quality.py CLI
    - Parse arguments
    - Create and run QualityAnalyzer
    - _Requirements: 8.1, 1.3_

  - [ ] 8.8 Implement analyze_raw.py CLI
    - Parse arguments
    - Create and run RawDataAnalyzer
    - _Requirements: 8.1, 1.3_

  - [ ] 8.9 Implement analyze_comprehensive.py CLI
    - Parse arguments
    - Create and run ComprehensiveAnalyzer
    - _Requirements: 8.1, 1.3_

  - [ ]* 8.10 Write integration tests for all CLI scripts
    - Test each CLI with various arguments
    - Test error handling
    - Test output generation
    - _Requirements: 8.1, 8.2, 8.3_

- [ ] 9. Implement batch scripts and backward compatibility
  - [ ] 9.1 Create new batch scripts in batch/ directory
    - run_pareto_analysis.bat
    - run_quality_analysis.bat
    - run_raw_analysis.bat
    - run_comprehensive_analysis.bat
    - run_all_analyses.bat
    - _Requirements: 3.2, 9.1_

  - [ ] 9.2 Update old batch scripts with deprecation warnings
    - Add deprecation messages
    - Call new CLI scripts
    - _Requirements: 9.1, 9.4_

  - [ ]* 9.3 Write property test for deprecation warnings
    - **Property 19: Deprecation Warnings**
    - **Validates: Requirements 9.4**

  - [ ] 9.4 Create compatibility wrappers for old Python scripts
    - Add deprecation warnings
    - Import and call new implementations
    - _Requirements: 9.1, 9.2, 9.4_

  - [ ]* 9.5 Write property test for output location consistency
    - **Property 18: Output Location Consistency**
    - **Validates: Requirements 9.3**

- [ ] 10. Implement code quality checks
  - [ ]* 10.1 Write property test for module initialization
    - **Property 1: Module Initialization**
    - **Validates: Requirements 1.2**

  - [ ]* 10.2 Write property test for snake_case naming
    - **Property 7: Snake Case Naming**
    - **Validates: Requirements 4.1**

  - [ ]* 10.3 Write property test for no version suffixes
    - **Property 8: No Version Suffixes**
    - **Validates: Requirements 4.3**

  - [ ]* 10.4 Write property test for CLI naming convention
    - **Property 9: CLI Naming Convention**
    - **Validates: Requirements 4.4, 4.5**

  - [ ]* 10.5 Write property test for unified configuration loading
    - **Property 10: Unified Configuration Loading**
    - **Validates: Requirements 5.1, 5.2**

  - [ ]* 10.6 Write property test for test structure mirroring
    - **Property 14: Test Structure Mirroring**
    - **Validates: Requirements 7.2**

  - [ ]* 10.7 Write property test for docstring coverage
    - **Property 20: Docstring Coverage**
    - **Validates: Requirements 10.2, 10.4**

- [ ] 11. Documentation and examples
  - [ ] 11.1 Write main README.md
    - Architecture overview
    - Quick start guide
    - Module descriptions
    - _Requirements: 10.1_

  - [ ] 11.2 Write README for each subdirectory
    - core/README.md
    - analyzers/README.md
    - pareto/README.md
    - utils/README.md
    - cli/README.md
    - tests/README.md
    - _Requirements: 3.5_

  - [ ] 11.3 Write migration guide
    - Old vs new structure mapping
    - Command migration examples
    - Breaking changes
    - _Requirements: 9.2, 10.5_

  - [ ] 11.4 Add docstrings to all public functions and classes
    - Document parameters and return values
    - Add usage examples
    - _Requirements: 10.4_

  - [ ] 11.5 Create usage examples
    - Example: Running pareto analysis
    - Example: Running quality analysis
    - Example: Composing analyzers
    - Example: Custom analyzer
    - _Requirements: 10.3_

- [ ] 12. Integration testing and validation
  - [ ]* 12.1 Write integration test for complete pareto analysis
    - Test full pipeline from data loading to report generation
    - _Requirements: 7.4_

  - [ ]* 12.2 Write integration test for complete quality analysis
    - Test full pipeline
    - _Requirements: 7.4_

  - [ ]* 12.3 Write integration test for batch processing
    - Test running multiple analyses in sequence
    - _Requirements: 7.4_

  - [ ]* 12.4 Write integration test for backward compatibility
    - Test old batch files still work
    - Test deprecation warnings are emitted
    - _Requirements: 9.1, 9.4_

  - [ ] 12.5 Run all tests and verify coverage
    - Run pytest with coverage
    - Ensure >80% coverage
    - Fix any failing tests
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 13. Final checkpoint - Complete refactoring
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties (100+ iterations each)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows
- All tests should reference design document properties in comments
