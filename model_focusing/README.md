# Model Focusing in Pycel

## Overview

This document analyzes the **core** Model Focusing capabilities in Pycel, focusing on robust and well-implemented functionalities that are ready for industrial use in Excel spreadsheet analysis.

## Documentation Files

- **[README.md](README.md)** - This overview of Model Focusing capabilities
- **[VERIFIED_PYCEL_API_DOCUMENTATION.md](VERIFIED_PYCEL_API_DOCUMENTATION.md)** - Complete verified API reference (100% tested)
- **[examples.py](examples.py)** - Practical usage examples
- **[test_model_focusing_core.py](test_model_focusing_core.py)** - Core functionality tests
- **[test_documentation_verification.py](test_documentation_verification.py)** - API documentation verification tests

## Validated Core Capabilities ✅

### 1. Precise Sub-model Extraction

**Main Functionality: `trim_graph()`**

Pycel allows extracting specific sub-portions of complex Excel models, keeping only the cells necessary for analysis.

```python
# Define sub-model inputs and outputs
input_addrs = ['Assumptions!GrowthRate', 'Assumptions!CostInflation']
output_addrs = ['Dashboard!KPI1', 'Dashboard!ROI']

# Extract sub-model
excel.trim_graph(input_addrs=input_addrs, output_addrs=output_addrs)
```

**Extraction Algorithm:**
1. **Build Graph**: Constructs the graph for all required outputs
2. **Walk Dependents**: Navigates from inputs to dependents (`successors`)
3. **Walk Precedents**: Navigates from outputs to precedents (`predecessors`)
4. **Identify Buried Inputs**: Detects inputs that are not leaf nodes
5. **Prune Cells**: Removes unnecessary cells, converts formulas to values

**Benefits:**
- Significantly reduces model size
- Maintains calculation precision
- Facilitates sensitivity analysis
- Improves evaluation performance

### 2. Bidirectional Dependency Analysis

**Dependency Graph Navigation**

Pycel uses NetworkX to create a directed graph that models cell dependencies, enabling analysis in both directions.

```python
# Upstream analysis (precedents)
for precedent in excel.dep_graph.predecessors(cell):
    print(f"Precedent: {precedent.address}")

# Downstream analysis (dependents)  
for dependent in excel.dep_graph.successors(cell):
    print(f"Dependent: {dependent.address}")
```

**Value Tree Analysis:**
```python
# Generate formatted dependency tree
for line in excel.value_tree_str('Dashboard!ROI'):
    print(line)

# Example output:
# Dashboard!ROI = 0.15
#  Calculations!NetIncome = 1000000
#   Revenue!Total = 5000000
#    Assumptions!GrowthRate = 0.05
#   Costs!Total = 4000000
#    Assumptions!CostInflation = 0.03
```

**Cycle Detection:**
- Automatically identifies circular references
- Marks cycles in the value tree: `<- cycle`
- Support for iterative evaluation with configurable tolerance

### 3. Robust Validation Against Excel

**Calculation Validation (`validate_calcs`)**

Systematically compares values calculated by Pycel against original Excel values.

```python
# Validate all calculations
validation_results = excel.validate_calcs()

# Validate specific outputs
validation_results = excel.validate_calcs(output_addrs=['Dashboard!ROI'])

# Results structure
{
    'mismatch': {
        'Sheet1!B2': Mismatch(original=100, calced=99.99, formula='=A1*A2')
    },
    'not-implemented': {
        'XLOOKUP': [('Sheet1!C3', '=XLOOKUP(...)', 'Function not implemented')]
    },
    'exceptions': {
        'ValueError': [('Sheet1!D4', '=1/0', 'Division by zero')]
    }
}
```

**Serialization Validation (`validate_serialized`)**

Verifies that the serialized/deserialized model produces the same results as the original.

```python
# Validate serialization round-trip
failed_cells = excel.validate_serialized(output_addrs=output_addrs)
assert failed_cells == {}  # No errors expected
```

**Validation Features:**
- **Configurable Tolerance**: Handles floating-point precision differences
- **Error Categorization**: Separates mismatches, unimplemented functions, and exceptions
- **Tree Verification**: Automatically validates precedents
- **Progress Tracking**: Reports progress on large models

### 4. Flexible Visualization and Export

**Multiple Export Formats**

```python
# Export for Gephi analysis
excel.export_to_gexf('model_graph.gexf')

# Export for Graphviz
excel.export_to_dot('model_graph.dot')

# Interactive visualization with matplotlib
excel.plot_graph(layout_type='spring_layout')
```

**Model Serialization**
```python
# Multiple supported formats
excel.to_file('model.pkl')    # Pickle (fastest)
excel.to_file('model.yml')    # YAML (readable)
excel.to_file('model.json')   # JSON (portable)

# Load serialized model
excel_loaded = ExcelCompiler.from_file('model.pkl')
```

**Visualization Benefits:**
- **Visual Analysis**: Identify patterns and bottlenecks
- **Documentation**: Generate dependency diagrams
- **Debugging**: Visualize calculation flow
- **Communication**: Explain model logic to stakeholders

### 5. Complex Excel Structure Handling

**Named Ranges and Defined Names**
```python
# Access workbook named ranges
defined_names = excel.excel.defined_names
for name, destinations in defined_names.items():
    print(f"Named range: {name} -> {destinations}")
```

**Structured Tables**
```python
# Excel table support
table, sheet_name = excel.excel.table('SalesData')
table_name = excel.excel.table_name_containing('Sheet1!B5')
```

**Circular References**
```python
# Iterative evaluation configuration
excel = ExcelCompiler(filename='model.xlsx', cycles={
    'iterations': 100,
    'tolerance': 0.001
})

# Evaluation with specific parameters
result = excel.evaluate('Sheet1!B2', iterations=50, tolerance=0.01)
```

**Multi-sheet Dependencies**
- Automatic handling of inter-sheet dependencies
- Cross-sheet reference resolution
- Support for sheet names with spaces and special characters

**Conditional Formatting**
```python
# Conditional format analysis
cf_rules = excel.excel.conditional_format('Sheet1!A1')
```

## Typical Use Cases

### 1. Financial Model Audit
```python
# Load complete model
excel = ExcelCompiler('financial_model.xlsx')

# Extract critical sub-model
excel.trim_graph(
    input_addrs=['Assumptions!Revenue_Growth', 'Assumptions!COGS_Rate'],
    output_addrs=['Summary!EBITDA', 'Summary!FCF']
)

# Validate accuracy
validation = excel.validate_calcs()
if validation:
    print("⚠️ Discrepancies found:", validation)
else:
    print("✅ Model validated correctly")
```

### 2. Sensitivity Analysis
```python
# Define scenarios
scenarios = [
    {'Assumptions!Growth': 0.05, 'Assumptions!Margin': 0.15},
    {'Assumptions!Growth': 0.10, 'Assumptions!Margin': 0.20},
    {'Assumptions!Growth': 0.15, 'Assumptions!Margin': 0.25}
]

# Evaluate each scenario
results = []
for scenario in scenarios:
    for addr, value in scenario.items():
        excel.set_value(addr, value)
    
    result = excel.evaluate('Dashboard!NPV')
    results.append(result)
    print(f"Scenario {scenario}: NPV = {result}")
```

### 3. Dependency Documentation
```python
# Generate dependency documentation
critical_outputs = ['KPI1', 'KPI2', 'ROI']

for output in critical_outputs:
    print(f"\n=== Dependencies for {output} ===")
    for line in excel.value_tree_str(output):
        print(line)

# Export for visual analysis
excel.export_to_gexf('model_dependencies.gexf')
```

## Known Limitations

### Excel Functions
- **VBA**: Not supported, requires manual reimplementation
- **Dynamic Functions**: OFFSET, INDIRECT may fail if cells are not compiled
- **Coverage**: Only implements functions based on project needs

### Performance
- **Scalability**: Suitable for medium-sized models (~10K formulas)
- **Memory**: Keeps complete model in memory
- **Optimization**: Not optimized for massive cases

### Advanced Analysis
- **Metrics**: Does not include automatic complexity metrics
- **Impact Analysis**: Limited impact analysis
- **Risk Assessment**: No integrated risk analysis

## Conclusion

The core Model Focusing capabilities in Pycel provide a solid foundation for:

✅ **Extraction and analysis of complex Excel sub-models**  
✅ **Rigorous validation against original Excel**  
✅ **Bidirectional dependency analysis**  
✅ **Model visualization and documentation**  
✅ **Advanced Excel structure handling**  

These functionalities are **robust, well-tested and ready for industrial use** in financial model audits, sensitivity analysis, and business logic extraction from complex spreadsheets.

## NumPy Compatibility Note

### ⚠️ **Limitation with NumPy 2.0+**
GEXF export (`export_to_gexf()`) requires **NumPy < 2.0** due to a NetworkX incompatibility that uses the deprecated `np.float_` type.

**Recommended installation:**
```bash
pip install "numpy<2.0" pycel
```

**Functionality by NumPy version:**
- ✅ **NumPy 1.x**: All functionalities including GEXF export
- ⚠️ **NumPy 2.0+**: All functionalities except GEXF export

**Visualization alternatives with NumPy 2.0+:**
- `export_to_dot()` - For Graphviz
- `plot_graph()` - For matplotlib
- Serialization in other formats (PKL, YAML, JSON)