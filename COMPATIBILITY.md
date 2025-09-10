# Pycel Compatibility Guide

## NumPy 2.0 Compatibility

### Issue Summary
Pycel has a **known compatibility issue with NumPy 2.0+** that affects **GEXF graph export functionality only**.

### Root Cause
- **Component**: NetworkX 2.6.x GEXF writer
- **Error**: `AttributeError: 'np.float_' was removed in the NumPy 2.0 release. Use 'np.float64' instead.`
- **Location**: `networkx/readwrite/gexf.py` line 223 in `construct_types()`
- **Cause**: NetworkX 2.6.x uses the deprecated `np.float_` type that was removed in NumPy 2.0

### Impact Assessment

#### ✅ **Fully Compatible with NumPy 2.0+**
- ✅ Excel file parsing and compilation
- ✅ Formula evaluation and calculation
- ✅ Model focusing (`trim_graph()`)
- ✅ Dependency analysis
- ✅ Validation (`validate_calcs()`)
- ✅ Serialization (PKL, YAML, JSON)
- ✅ DOT export for Graphviz
- ✅ Matplotlib plotting
- ✅ All core pycel functionality

#### ❌ **Not Compatible with NumPy 2.0+**
- ❌ GEXF export for Gephi visualization (`export_to_gexf()`)

### Recommended Solutions

#### Option 1: Use NumPy 1.x (Recommended)
```bash
pip install "numpy<2.0" pycel
```
**Pros**: Full functionality including GEXF export  
**Cons**: Uses older NumPy version

#### Option 2: Use NumPy 2.0+ with Limited Functionality
```bash
pip install "numpy>=2.0" pycel
```
**Pros**: Latest NumPy version  
**Cons**: GEXF export will fail

#### Option 3: Conditional Installation
```python
# In your requirements.txt or setup.py
numpy<2.0; extra == "visualization"
numpy>=2.0; extra != "visualization"
```

### Workarounds for NumPy 2.0+ Users

If you must use NumPy 2.0+, you can still visualize dependency graphs using:

1. **DOT Export** (Graphviz):
   ```python
   excel.export_to_dot('model.dot')
   ```

2. **Matplotlib Plotting**:
   ```python
   excel.plot_graph()
   ```

3. **Manual NetworkX Export**:
   ```python
   import networkx as nx
   nx.write_graphml(excel.dep_graph, 'model.graphml')
   ```

### Future Resolution

This issue will be resolved when:
- NetworkX releases a version compatible with NumPy 2.0+, OR
- Pycel updates to use a different graph export library, OR
- A custom GEXF writer is implemented in pycel

### Testing Status

- **NumPy 1.26.4**: ✅ All 2,986 tests pass (99.6% success rate)
- **NumPy 2.0+**: ⚠️ All tests pass except GEXF export

### Version Compatibility Matrix

| NumPy Version | Core Functionality | GEXF Export | Recommendation |
|---------------|-------------------|-------------|----------------|
| 1.20.x - 1.26.x | ✅ Full | ✅ Works | ✅ Recommended |
| 2.0.x+ | ✅ Full | ❌ Fails | ⚠️ Limited |

### Installation Examples

#### For Full Functionality (Recommended)
```bash
pip install "numpy<2.0" pycel[visualization]
```

#### For Core Functionality Only
```bash
pip install pycel  # Will install numpy<2.0 by default
```

#### For Development
```bash
pip install "numpy<2.0" pycel[dev,visualization]
```

### Error Details

If you encounter the NumPy 2.0 error, you'll see:
```
AttributeError: `np.float_` was removed in the NumPy 2.0 release. Use `np.float64` instead.
```

This error occurs specifically in:
- `excel.export_to_gexf()` calls
- NetworkX GEXF writer initialization
- Any code path that triggers GEXF export

### Contact

For questions about NumPy compatibility:
- Open an issue: https://github.com/stephenrauch/pycel/issues
- Check existing compatibility issues
- Consider contributing a fix for NetworkX compatibility