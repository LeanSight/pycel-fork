# Model Focusing en Pycel

## Resumen

Este documento analiza las capacidades **core** de Model Focusing en Pycel, enfocándose en las funcionalidades robustas y bien implementadas que están listas para uso en análisis industrial de planillas Excel.

## Capacidades Core Validadas ✅

### 1. Extracción Precisa de Sub-modelos

**Funcionalidad Principal: `trim_graph()`**

Pycel permite extraer sub-porciones específicas de modelos Excel complejos, manteniendo solo las celdas necesarias para el análisis.

```python
# Definir inputs y outputs del sub-modelo
input_addrs = ['Assumptions!GrowthRate', 'Assumptions!CostInflation']
output_addrs = ['Dashboard!KPI1', 'Dashboard!ROI']

# Extraer sub-modelo
excel.trim_graph(input_addrs=input_addrs, output_addrs=output_addrs)
```

**Algoritmo de Extracción:**
1. **Build Graph**: Construye el grafo para todas las salidas requeridas
2. **Walk Dependents**: Navega desde inputs hacia dependientes (`successors`)
3. **Walk Precedents**: Navega desde outputs hacia precedentes (`predecessors`)
4. **Identify Buried Inputs**: Detecta inputs que no son leaf nodes
5. **Prune Cells**: Elimina celdas innecesarias, convierte fórmulas a valores

**Beneficios:**
- Reduce significativamente el tamaño del modelo
- Mantiene precisión de cálculos
- Facilita análisis de sensibilidad
- Mejora performance de evaluación

### 2. Análisis Bidireccional de Dependencias

**Navegación del Grafo de Dependencias**

Pycel utiliza NetworkX para crear un grafo dirigido que modela las dependencias entre celdas, permitiendo análisis en ambas direcciones.

```python
# Análisis upstream (precedentes)
for precedent in excel.dep_graph.predecessors(cell):
    print(f"Precedent: {precedent.address}")

# Análisis downstream (dependientes)  
for dependent in excel.dep_graph.successors(cell):
    print(f"Dependent: {dependent.address}")
```

**Value Tree Analysis:**
```python
# Generar árbol de dependencias formateado
for line in excel.value_tree_str('Dashboard!ROI'):
    print(line)

# Output ejemplo:
# Dashboard!ROI = 0.15
#  Calculations!NetIncome = 1000000
#   Revenue!Total = 5000000
#    Assumptions!GrowthRate = 0.05
#   Costs!Total = 4000000
#    Assumptions!CostInflation = 0.03
```

**Detección de Ciclos:**
- Identifica referencias circulares automáticamente
- Marca ciclos en el value tree: `<- cycle`
- Soporte para evaluación iterativa con tolerancia configurable

### 3. Validación Robusta contra Excel

**Validación de Cálculos (`validate_calcs`)**

Compara sistemáticamente los valores calculados por Pycel contra los valores originales de Excel.

```python
# Validar todos los cálculos
validation_results = excel.validate_calcs()

# Validar outputs específicos
validation_results = excel.validate_calcs(output_addrs=['Dashboard!ROI'])

# Estructura de resultados
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

**Validación de Serialización (`validate_serialized`)**

Verifica que el modelo serializado/deserializado produce los mismos resultados que el original.

```python
# Validar round-trip de serialización
failed_cells = excel.validate_serialized(output_addrs=output_addrs)
assert failed_cells == {}  # Sin errores esperados
```

**Características de Validación:**
- **Tolerancia Configurable**: Maneja diferencias de precisión flotante
- **Categorización de Errores**: Separa mismatches, funciones no implementadas y excepciones
- **Tree Verification**: Valida precedentes automáticamente
- **Progress Tracking**: Reporta progreso en modelos grandes

### 4. Visualización y Exportación Flexible

**Múltiples Formatos de Exportación**

```python
# Exportar para análisis en Gephi
excel.export_to_gexf('model_graph.gexf')

# Exportar para Graphviz
excel.export_to_dot('model_graph.dot')

# Visualización interactiva con matplotlib
excel.plot_graph(layout_type='spring_layout')
```

**Serialización de Modelos**
```python
# Múltiples formatos soportados
excel.to_file('model.pkl')    # Pickle (más rápido)
excel.to_file('model.yml')    # YAML (legible)
excel.to_file('model.json')   # JSON (portable)

# Cargar modelo serializado
excel_loaded = ExcelCompiler.from_file('model.pkl')
```

**Beneficios de Visualización:**
- **Análisis Visual**: Identificar patrones y cuellos de botella
- **Documentación**: Generar diagramas de dependencias
- **Debugging**: Visualizar flujo de cálculos
- **Comunicación**: Explicar lógica de modelo a stakeholders

### 5. Manejo de Estructuras Excel Complejas

**Named Ranges y Defined Names**
```python
# Acceso a named ranges del workbook
defined_names = excel.excel.defined_names
for name, destinations in defined_names.items():
    print(f"Named range: {name} -> {destinations}")
```

**Tablas Estructuradas**
```python
# Soporte para tablas Excel
table, sheet_name = excel.excel.table('SalesData')
table_name = excel.excel.table_name_containing('Sheet1!B5')
```

**Referencias Circulares**
```python
# Configuración de evaluación iterativa
excel = ExcelCompiler(filename='model.xlsx', cycles={
    'iterations': 100,
    'tolerance': 0.001
})

# Evaluación con parámetros específicos
result = excel.evaluate('Sheet1!B2', iterations=50, tolerance=0.01)
```

**Multi-sheet Dependencies**
- Manejo automático de dependencias entre hojas
- Resolución de referencias cross-sheet
- Soporte para nombres de hojas con espacios y caracteres especiales

**Conditional Formatting**
```python
# Análisis de formatos condicionales
cf_rules = excel.excel.conditional_format('Sheet1!A1')
```

## Casos de Uso Típicos

### 1. Auditoría de Modelo Financiero
```python
# Cargar modelo completo
excel = ExcelCompiler('financial_model.xlsx')

# Extraer sub-modelo crítico
excel.trim_graph(
    input_addrs=['Assumptions!Revenue_Growth', 'Assumptions!COGS_Rate'],
    output_addrs=['Summary!EBITDA', 'Summary!FCF']
)

# Validar precisión
validation = excel.validate_calcs()
if validation:
    print("⚠️ Discrepancias encontradas:", validation)
else:
    print("✅ Modelo validado correctamente")
```

### 2. Análisis de Sensibilidad
```python
# Definir escenarios
scenarios = [
    {'Assumptions!Growth': 0.05, 'Assumptions!Margin': 0.15},
    {'Assumptions!Growth': 0.10, 'Assumptions!Margin': 0.20},
    {'Assumptions!Growth': 0.15, 'Assumptions!Margin': 0.25}
]

# Evaluar cada escenario
results = []
for scenario in scenarios:
    for addr, value in scenario.items():
        excel.set_value(addr, value)
    
    result = excel.evaluate('Dashboard!NPV')
    results.append(result)
    print(f"Scenario {scenario}: NPV = {result}")
```

### 3. Documentación de Dependencias
```python
# Generar documentación de dependencias
critical_outputs = ['KPI1', 'KPI2', 'ROI']

for output in critical_outputs:
    print(f"\n=== Dependencies for {output} ===")
    for line in excel.value_tree_str(output):
        print(line)

# Exportar para análisis visual
excel.export_to_gexf('model_dependencies.gexf')
```

## Limitaciones Conocidas

### Funciones Excel
- **VBA**: No soportado, requiere reimplementación manual
- **Funciones Dinámicas**: OFFSET, INDIRECT pueden fallar si celdas no están compiladas
- **Coverage**: Solo implementa funciones según necesidad del proyecto

### Performance
- **Escalabilidad**: Adecuado para modelos medianos (~10K fórmulas)
- **Memory**: Mantiene modelo completo en memoria
- **Optimización**: No optimizado para casos masivos

### Análisis Avanzado
- **Métricas**: No incluye métricas de complejidad automáticas
- **Impact Analysis**: Análisis de impacto limitado
- **Risk Assessment**: No hay análisis de riesgo integrado

## Conclusión

Las capacidades core de Model Focusing en Pycel proporcionan una base sólida para:

✅ **Extracción y análisis de sub-modelos Excel complejos**  
✅ **Validación rigurosa contra Excel original**  
✅ **Análisis bidireccional de dependencias**  
✅ **Visualización y documentación de modelos**  
✅ **Manejo de estructuras Excel avanzadas**  

Estas funcionalidades son **robustas, bien testadas y listas para uso industrial** en auditorías de modelos financieros, análisis de sensibilidad y extracción de lógica de negocio de spreadsheets complejos.

## Nota de Compatibilidad NumPy

### ⚠️ **Limitación con NumPy 2.0+**
La exportación GEXF (`export_to_gexf()`) requiere **NumPy < 2.0** debido a una incompatibilidad en NetworkX que usa el tipo deprecado `np.float_`.

**Instalación recomendada:**
```bash
pip install "numpy<2.0" pycel
```

**Funcionalidades por versión de NumPy:**
- ✅ **NumPy 1.x**: Todas las funcionalidades incluyendo GEXF export
- ⚠️ **NumPy 2.0+**: Todas las funcionalidades excepto GEXF export

**Alternativas para visualización con NumPy 2.0+:**
- `export_to_dot()` - Para Graphviz
- `plot_graph()` - Para matplotlib
- Serialización en otros formatos (PKL, YAML, JSON)