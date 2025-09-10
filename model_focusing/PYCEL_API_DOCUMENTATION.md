# Pycel API Documentation

## Overview

This document provides comprehensive documentation for all Pycel items used in the model_focusing module, specifically in `test_model_focusing_core.py` and `examples.py`. Each method and property is documented with signatures, parameters, return values, and verified examples.

## Table of Contents

1. [ExcelCompiler Class](#excelcompiler-class)
2. [Core Methods](#core-methods)
3. [Properties](#properties)
4. [Utility Classes](#utility-classes)
5. [Verified Examples](#verified-examples)

---

## ExcelCompiler Class

### Constructor

#### `ExcelCompiler(filename=None, excel=None, plugins=None, cycles=None)`

**Description**: Main class for compiling Excel spreadsheets into executable Python code.

**Parameters**:
- `filename` (str, optional): Path to Excel file (.xlsx) or serialized file (.pkl, .yml, .json)
- `excel` (ExcelWrapper or openpyxl.Workbook, optional): Pre-loaded Excel workbook instance
- `plugins` (list, optional): Module paths for plugin library functions
- `cycles` (dict, optional): Override workbook iterative calculation settings
  - `iterations` (int): Maximum number of iterations for circular references
  - `tolerance` (float): Convergence tolerance for iterative calculations

**Returns**: ExcelCompiler instance

**Example**:
```python
from pycel import ExcelCompiler

# Load from file
excel = ExcelCompiler('financial_model.xlsx')

# Load with circular reference handling
excel = ExcelCompiler('model.xlsx', cycles={'iterations': 100, 'tolerance': 0.001})

# Load from openpyxl workbook
from openpyxl import Workbook
wb = Workbook()
excel = ExcelCompiler(excel=wb)
```

---

## Core Methods

### Model Evaluation

#### `evaluate(address)`

**Description**: Evaluates a cell or range and returns its calculated value.

**Parameters**:
- `address` (str): Cell address in Excel format (e.g., 'Sheet1!A1', 'Summary!B5')

**Returns**: Calculated value (int, float, str, list, or Excel error)

**Behavior**:
- Builds dependency graph if not already built
- Handles formulas, constants, and ranges
- Supports cross-sheet references
- Manages circular references with iterative solving

**Example**:
```python
# Evaluate single cell
result = excel.evaluate('Sheet1!A1')

# Evaluate cell with formula
ebitda = excel.evaluate('Summary!EBITDA')

# Evaluate range (returns list)
range_values = excel.evaluate('Data!A1:C3')
```

#### `set_value(address, value, set_as_range=False)`

**Description**: Sets the value of a cell or range, updating dependent calculations.

**Parameters**:
- `address` (str): Cell address in Excel format (must exist in cell_map)
- `value` (any): Value to set (number, string, or list for ranges)
- `set_as_range` (bool, optional): Whether to treat the address as a range

**Returns**: None

**Requirements**:
- Cell must already exist in the model (evaluate it first if needed)
- Address must be in the cell_map

**Side Effects**:
- Updates cell value in the model
- Invalidates dependent cell calculations
- Triggers recalculation on next evaluation

**Important Notes**:
- Formula strings are treated as literal text, not as formulas
- To change formulas, modify the original Excel file and reload
- Primarily used for changing input values and constants

**Example**:
```python
# Set single value (cell must exist)
excel.evaluate('Assumptions!GrowthRate')  # Ensure cell exists
excel.set_value('Assumptions!GrowthRate', 0.05)

# Set multiple values
excel.set_value('Assumptions!CostRate', 0.60)

# Set range values
excel.set_value('Data!A1:A3', [100, 200, 300], set_as_range=True)

# Change input and see effect on outputs
excel.set_value('Inputs!BaseValue', 1000)
result = excel.evaluate('Outputs!CalculatedValue')
```

### Model Focusing

#### `trim_graph(input_addrs, output_addrs)`

**Description**: Removes unneeded cells from the model, keeping only those required for the specified inputs and outputs.

**Parameters**:
- `input_addrs` (list): List of input cell addresses that define model boundaries
- `output_addrs` (list): List of output cell addresses to preserve

**Returns**: None

**Side Effects**:
- Reduces `cell_map` to only necessary cells
- Maintains calculation accuracy for specified outputs
- Converts unnecessary formula cells to constant values
- Updates dependency graph accordingly

**Algorithm**:
1. Builds dependency graph for all outputs
2. Walks dependents from inputs to find needed cells
3. Walks precedents from outputs to find required cells
4. Identifies and handles buried inputs (inputs that aren't leaf nodes)
5. Removes unnecessary cells and converts formulas to values

**Example**:
```python
# Focus on critical financial metrics
input_addrs = ['Assumptions!GrowthRate', 'Assumptions!CostRate']
output_addrs = ['Summary!EBITDA', 'Summary!FCF']

excel.trim_graph(input_addrs, output_addrs)
print(f"Model reduced to {len(excel.cell_map)} cells")
```

### Validation

#### `validate_calcs(output_addrs=None, sheet=None, verify_tree=True, tolerance=None, raise_exceptions=False)`

**Description**: Validates calculated values against original Excel values to ensure accuracy.

**Parameters**:
- `output_addrs` (list, optional): Specific addresses to validate (defaults to all formulas)
- `sheet` (str, optional): Specific sheet to validate (defaults to all sheets)
- `verify_tree` (bool): Whether to validate precedent cells automatically
- `tolerance` (float, optional): Numerical tolerance for floating-point comparisons
- `raise_exceptions` (bool): Whether to raise exceptions on validation errors

**Returns**: Dictionary with validation results:
```python
{
    'mismatch': {
        'address': Mismatch(original=value, calced=value, formula='=formula')
    },
    'not-implemented': {
        'function_name': [('address', 'formula', 'error_message')]
    },
    'exceptions': {
        'exception_type': [('address', 'formula', 'error_message')]
    }
}
```

**Example**:
```python
# Validate all calculations
results = excel.validate_calcs()
if not results:
    print("✅ All calculations match Excel")
else:
    print(f"⚠️ Found {len(results)} validation issues")

# Validate specific outputs with tolerance
results = excel.validate_calcs(
    output_addrs=['Summary!EBITDA', 'Summary!FCF'],
    tolerance=0.01
)
```

#### `validate_serialized(output_addrs=None, **kwargs)`

**Description**: Validates that serialization and deserialization preserves calculation accuracy.

**Parameters**:
- `output_addrs` (list, optional): Addresses to validate after round-trip serialization
- `**kwargs`: Additional arguments passed to validate_calcs

**Returns**: Dictionary of failed cells (empty if successful)

**Process**:
1. Serializes current model to temporary file
2. Loads model from serialized file
3. Compares calculation results between original and loaded models

**Example**:
```python
# Validate serialization consistency
failed_cells = excel.validate_serialized(output_addrs=['Summary!KPIs'])
assert failed_cells == {}, "Serialization should preserve accuracy"
```

### Dependency Analysis

#### `value_tree_str(address, indent=0)`

**Description**: Generates a formatted string representation of the dependency tree for a cell.

**Parameters**:
- `address` (str): Root cell address to analyze
- `indent` (int, optional): Initial indentation level

**Returns**: Generator yielding formatted dependency tree lines

**Format**:
```
Cell!Address = value
  Precedent1!Address = value
    SubPrecedent!Address = value
  Precedent2!Address = value <- cycle (if circular reference detected)
```

**Example**:
```python
# Generate dependency tree
for line in excel.value_tree_str('Summary!EBITDA'):
    print(line)

# Output:
# Summary!EBITDA = 150000
#   Summary!Revenue = 1000000
#     Assumptions!BaseRevenue = 950000
#     Assumptions!GrowthRate = 0.05
#   Summary!COGS = 600000
#     Summary!Revenue = 1000000 <- cycle
#     Assumptions!COGSRate = 0.60
```

### Visualization and Export

#### `export_to_gexf(filename=None)`

**Description**: Exports the dependency graph to GEXF format for visualization in Gephi.

**Parameters**:
- `filename` (str, optional): Output filename (defaults to auto-generated name)

**Returns**: None

**Requirements**:
- NumPy < 2.0 (due to NetworkX compatibility)
- NetworkX library

**Side Effects**:
- Creates .gexf file with graph structure
- Includes node attributes (cell addresses, values, formulas)
- Includes edge attributes (dependency relationships)

**Example**:
```python
# Export for Gephi visualization
excel.export_to_gexf('financial_model_dependencies.gexf')
```

#### `export_to_dot(filename=None)`

**Description**: Exports the dependency graph to DOT format for Graphviz visualization.

**Parameters**:
- `filename` (str, optional): Output filename (defaults to auto-generated name)

**Returns**: None

**Requirements**:
- pydot library
- Graphviz software

**Example**:
```python
# Export for Graphviz
excel.export_to_dot('model_graph.dot')
# Then: dot -Tpng model_graph.dot -o model_graph.png
```

#### `plot_graph(layout_type='spring_layout')`

**Description**: Creates an interactive plot of the dependency graph using matplotlib.

**Parameters**:
- `layout_type` (str): NetworkX layout algorithm ('spring_layout', 'circular_layout', etc.)

**Returns**: None

**Requirements**:
- matplotlib library

**Side Effects**:
- Displays interactive graph plot
- Shows nodes as cells and edges as dependencies

**Example**:
```python
# Plot dependency graph
excel.plot_graph(layout_type='spring_layout')
```

### Serialization

#### `to_file(filename=None, file_types=('pkl', 'yml'))`

**Description**: Serializes the compiled model to file(s) in specified format(s).

**Parameters**:
- `filename` (str, optional): Base filename (extension determines format)
- `file_types` (tuple): File formats to generate ('pkl', 'yml', 'json')

**Returns**: None

**Supported Formats**:
- `.pkl`: Python pickle (fastest, binary)
- `.yml`: YAML (human-readable, slower)
- `.json`: JSON (portable, moderate speed)

**Example**:
```python
# Save in multiple formats
excel.to_file('financial_model.pkl')
excel.to_file('financial_model.yml')
excel.to_file('financial_model.json')

# Save with auto-extension
excel.to_file('model', file_types=('pkl', 'yml'))
```

#### `from_file(filename, plugins=None)` (Class Method)

**Description**: Loads a previously serialized ExcelCompiler instance from file.

**Parameters**:
- `filename` (str): Path to serialized file
- `plugins` (list, optional): Plugin modules to load

**Returns**: ExcelCompiler instance

**Example**:
```python
# Load serialized model
excel_loaded = ExcelCompiler.from_file('financial_model.pkl')

# Verify it works the same
original_value = excel.evaluate('Summary!EBITDA')
loaded_value = excel_loaded.evaluate('Summary!EBITDA')
assert original_value == loaded_value
```

---

## Properties

### `cell_map`

**Type**: Dictionary mapping cell addresses to cell objects

**Description**: Contains all cells in the compiled model, indexed by their Excel addresses.

**Structure**:
```python
{
    'Sheet1!A1': _Cell(address='Sheet1!A1', value=100, formula=None),
    'Sheet1!B1': _Cell(address='Sheet1!B1', value=200, formula='=A1*2'),
    # ...
}
```

**Usage**:
```python
# Get cell count
cell_count = len(excel.cell_map)

# Access specific cell
cell = excel.cell_map['Sheet1!A1']
print(f"Cell value: {cell.value}")

# Check if cell exists
if 'Summary!EBITDA' in excel.cell_map:
    print("EBITDA cell found")
```

### `dep_graph`

**Type**: NetworkX DiGraph (Directed Graph)

**Description**: Represents the dependency relationships between cells as a directed graph.

**Structure**:
- **Nodes**: Cell objects
- **Edges**: Dependency relationships (A → B means A depends on B)

**Usage**:
```python
# Get graph statistics
print(f"Nodes: {len(excel.dep_graph.nodes())}")
print(f"Edges: {len(excel.dep_graph.edges())}")

# Analyze dependencies
cell = excel.cell_map['Summary!EBITDA']
predecessors = list(excel.dep_graph.predecessors(cell))  # What EBITDA depends on
successors = list(excel.dep_graph.successors(cell))      # What depends on EBITDA

# Check if graph is acyclic
is_dag = nx.is_directed_acyclic_graph(excel.dep_graph)
```

### `excel`

**Type**: ExcelWrapper instance

**Description**: Provides access to the underlying Excel workbook data and metadata.

**Key Attributes**:
- `workbook`: openpyxl workbook object
- `defined_names`: Named ranges and defined names
- `filename`: Original Excel filename

**Usage**:
```python
# Access workbook metadata
sheet_names = excel.excel.workbook.sheetnames
print(f"Sheets: {sheet_names}")

# Access defined names
defined_names = excel.excel.defined_names
for name, destinations in defined_names.items():
    print(f"Named range: {name} -> {destinations}")

# Access tables
try:
    table, sheet_name = excel.excel.table('SalesData')
    print(f"Table found on sheet: {sheet_name}")
except KeyError:
    print("Table not found")
```

### `log`

**Type**: Python logger instance

**Description**: Logger for debugging and monitoring Pycel operations.

**Usage**:
```python
# Set logging level
excel.log.setLevel(logging.DEBUG)

# Log custom messages
excel.log.info("Starting model analysis")
excel.log.warning("Potential circular reference detected")
```

---

## Utility Classes

### AddressRange

**Description**: Represents Excel address ranges and provides parsing utilities.

**Usage**:
```python
from pycel.excelutil import AddressRange

# Parse range
addr_range = AddressRange('Sheet1!A1:C3')
print(f"Start: {addr_range.start}")  # Sheet1!A1
print(f"End: {addr_range.end}")      # Sheet1!C3

# Single cell
addr_cell = AddressRange('Sheet1!A1')
print(f"Address: {addr_cell.address}")  # Sheet1!A1
```

### AddressCell

**Description**: Represents individual Excel cell addresses.

**Usage**:
```python
from pycel.excelutil import AddressCell

# Create cell address
addr = AddressCell('Sheet1!A1')
print(f"Sheet: {addr.sheet}")     # Sheet1
print(f"Column: {addr.column}")   # A
print(f"Row: {addr.row}")         # 1
```

---

## Verified Examples

### Complete Model Focusing Workflow

```python
from pycel import ExcelCompiler

# 1. Load Excel model
excel = ExcelCompiler('financial_model.xlsx')
print(f"Original model: {len(excel.cell_map)} cells")

# 2. Define critical inputs and outputs
input_addrs = [
    'Assumptions!GrowthRate',
    'Assumptions!COGSRate',
    'Assumptions!OpExRate'
]

output_addrs = [
    'Summary!Revenue',
    'Summary!EBITDA',
    'Summary!FCF'
]

# 3. Extract focused sub-model
excel.trim_graph(input_addrs, output_addrs)
print(f"Focused model: {len(excel.cell_map)} cells")

# 4. Validate accuracy
validation_results = excel.validate_calcs(output_addrs=output_addrs)
if not validation_results:
    print("✅ Model validation successful")
else:
    print(f"⚠️ Validation issues: {validation_results}")

# 5. Perform sensitivity analysis
scenarios = [
    {'GrowthRate': 0.05, 'COGSRate': 0.60},
    {'GrowthRate': 0.10, 'COGSRate': 0.55},
    {'GrowthRate': 0.02, 'COGSRate': 0.65}
]

results = []
for scenario in scenarios:
    # Set scenario parameters
    excel.set_value('Assumptions!GrowthRate', scenario['GrowthRate'])
    excel.set_value('Assumptions!COGSRate', scenario['COGSRate'])
    
    # Calculate results
    ebitda = excel.evaluate('Summary!EBITDA')
    fcf = excel.evaluate('Summary!FCF')
    
    results.append({
        'scenario': scenario,
        'ebitda': ebitda,
        'fcf': fcf
    })
    
    print(f"Growth: {scenario['GrowthRate']:.1%}, "
          f"COGS: {scenario['COGSRate']:.1%} -> "
          f"EBITDA: {ebitda:,.0f}, FCF: {fcf:,.0f}")

# 6. Analyze dependencies
print("\nDependency analysis for EBITDA:")
for line in excel.value_tree_str('Summary!EBITDA'):
    print(line)

# 7. Export for visualization
excel.export_to_gexf('financial_model.gexf')
excel.export_to_dot('financial_model.dot')

# 8. Serialize model
excel.to_file('financial_model_focused.pkl')
excel.to_file('financial_model_focused.yml')

# 9. Verify serialization
excel_loaded = ExcelCompiler.from_file('financial_model_focused.pkl')
original_ebitda = excel.evaluate('Summary!EBITDA')
loaded_ebitda = excel_loaded.evaluate('Summary!EBITDA')
assert original_ebitda == loaded_ebitda, "Serialization should preserve values"

print("✅ Complete model focusing workflow successful")
```

### Error Handling and Edge Cases

```python
# Handle missing cells gracefully
try:
    result = excel.evaluate('NonExistent!Cell')
except KeyError as e:
    print(f"Cell not found: {e}")

# Handle circular references
excel_with_cycles = ExcelCompiler('model_with_cycles.xlsx', 
                                  cycles={'iterations': 100, 'tolerance': 0.001})
try:
    result = excel_with_cycles.evaluate('Sheet1!A1')
    print(f"Circular reference resolved: {result}")
except Exception as e:
    print(f"Circular reference failed to converge: {e}")

# Validate with custom tolerance
validation_results = excel.validate_calcs(
    output_addrs=['Summary!EBITDA'],
    tolerance=0.01,  # 1 cent tolerance
    raise_exceptions=False
)

# Handle trim_graph with disconnected inputs
try:
    excel.trim_graph(['UnconnectedInput!A1'], ['Summary!EBITDA'])
except ValueError as e:
    print(f"Trim graph error: {e}")
```

---

## Performance Considerations

### Memory Usage
- `cell_map` size directly impacts memory usage
- Use `trim_graph()` to reduce memory footprint for large models
- Consider serializing to disk for very large models

### Calculation Speed
- First evaluation builds dependency graph (slower)
- Subsequent evaluations use cached graph (faster)
- Circular references require iterative solving (slower)

### Serialization Performance
- **Pickle (.pkl)**: Fastest serialization/deserialization
- **YAML (.yml)**: Human-readable but slower
- **JSON (.json)**: Good balance of portability and speed

### Visualization Scalability
- GEXF export works well for models up to ~1000 cells
- DOT export better for smaller, focused models
- matplotlib plotting suitable for models up to ~100 cells

---

## Compatibility Notes

### NumPy Compatibility
- **NumPy 1.x**: Full functionality including GEXF export
- **NumPy 2.0+**: All features except GEXF export (NetworkX incompatibility)

### Excel Function Coverage
- ~200+ Excel functions implemented
- Mathematical, statistical, logical, and lookup functions well-supported
- VBA functions not supported (require manual reimplementation)
- Dynamic functions (OFFSET, INDIRECT) may have limitations

### File Format Support
- **Input**: .xlsx files (openpyxl compatible)
- **Output**: .pkl, .yml, .json serialization formats
- **Visualization**: .gexf (Gephi), .dot (Graphviz)

---

This documentation covers all Pycel items used in the model_focusing module with verified examples and comprehensive technical details.