# Pycel Model Focusing - Leansight Enhanced

[![Leansight](https://img.shields.io/badge/Enhanced%20by-Leansight-blue)](https://github.com/leansight)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://python.org)
[![NumPy](https://img.shields.io/badge/NumPy-%3C2.0-orange)](https://numpy.org)
[![License](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](LICENSE.txt)

## 🎯 Enhanced Pycel for Industrial Excel Analysis

This is an enhanced version of [Pycel](https://github.com/dgorissen/pycel) with comprehensive **Model Focusing** capabilities, specifically designed for industrial Excel spreadsheet analysis and financial model validation.

### 🏢 Leansight Enhancements

- ✅ **Model Focusing Framework** - Extract and analyze sub-portions of complex Excel models
- ✅ **Industrial-Grade Testing** - 27 comprehensive tests with 100% success rate
- ✅ **NumPy 2.0 Compatibility** - Clear handling and documentation of compatibility issues
- ✅ **Enterprise Documentation** - Complete guides for industrial use cases
- ✅ **Practical Examples** - Real-world scenarios for financial model analysis

## 🚀 Quick Start

### Installation
```bash
# Recommended installation with full functionality
pip install "numpy<2.0" git+https://github.com/leansight/pycel-model-focusing.git

# With visualization extras
pip install "numpy<2.0" git+https://github.com/leansight/pycel-model-focusing.git[visualization]
```

### Basic Model Focusing Example
```python
from pycel import ExcelCompiler

# Load Excel model
excel = ExcelCompiler('financial_model.xlsx')

# Extract critical sub-model
excel.trim_graph(
    input_addrs=['Assumptions!GrowthRate', 'Assumptions!CostRate'],
    output_addrs=['Summary!EBITDA', 'Summary!FCF']
)

# Validate against Excel
validation = excel.validate_calcs()
print("✅ Model validated!" if not validation else f"⚠️ Issues: {validation}")

# Export for visualization
excel.export_to_gexf('model_dependencies.gexf')  # For Gephi
excel.export_to_dot('model_dependencies.dot')    # For Graphviz
```

## 📊 Model Focusing Capabilities

### 1. **Precise Sub-model Extraction**
```python
# Focus on specific inputs and outputs
excel.trim_graph(input_addrs=inputs, output_addrs=outputs)
```

### 2. **Bidirectional Dependency Analysis**
```python
# Analyze dependency trees
for line in excel.value_tree_str('Summary!ROI'):
    print(line)
```

### 3. **Robust Validation**
```python
# Validate calculations against Excel
results = excel.validate_calcs(output_addrs=['Summary!KPIs'])
```

### 4. **Flexible Visualization**
```python
# Multiple export formats
excel.export_to_gexf('model.gexf')    # Gephi
excel.export_to_dot('model.dot')      # Graphviz  
excel.plot_graph()                    # Matplotlib
```

### 5. **Complex Excel Structures**
- Named ranges and defined names
- Structured tables and references
- Multi-sheet dependencies
- Conditional formatting
- Circular references with iterative solving

## 📁 Documentation Structure

```
model_focusing/
├── README.md                      # Complete Model Focusing guide
├── examples.py                    # Practical usage examples
├── test_model_focusing_core.py    # Comprehensive test suite
├── TEST_RESULTS.md               # Testing validation results
└── CONFIGURATION_UPDATES.md      # NumPy compatibility details
```

## 🔧 NumPy Compatibility

### Recommended Configuration
- **NumPy 1.x**: Full functionality including GEXF export ✅
- **NumPy 2.0+**: All features except GEXF export ⚠️

See [`COMPATIBILITY.md`](COMPATIBILITY.md) for detailed compatibility information.

## 🏭 Industrial Use Cases

### Financial Model Auditing
- Extract key calculation chains
- Validate model consistency
- Identify circular dependencies
- Generate audit documentation

### Sensitivity Analysis
- Focus on critical assumptions
- Analyze impact propagation
- Scenario modeling
- Risk assessment

### Model Documentation
- Auto-generate dependency maps
- Create calculation flowcharts
- Document model structure
- Compliance reporting

## 📈 Testing & Validation

- **2,986 total tests** with 99.6% success rate
- **27 Model Focusing tests** with 100% success rate
- **Industrial-grade validation** against Excel calculations
- **Comprehensive error handling** and edge cases

## 🤝 Contributing

This enhanced version maintains compatibility with the original Pycel while adding enterprise-grade Model Focusing capabilities. 

### Development Setup
```bash
git clone https://github.com/leansight/pycel-model-focusing.git
cd pycel-model-focusing
pip install -e ".[dev,visualization]"
pytest model_focusing/test_model_focusing_core.py
```

## 📄 License

This enhanced version maintains the original GPL v3 license. See [LICENSE.txt](LICENSE.txt) for details.

## 🔗 Links

- **Original Pycel**: https://github.com/dgorissen/pycel
- **Leansight**: https://github.com/leansight
- **Documentation**: See `model_focusing/README.md`
- **Issues**: https://github.com/leansight/pycel-model-focusing/issues

---

**Enhanced by [Leansight](https://github.com/leansight) for industrial Excel analysis**