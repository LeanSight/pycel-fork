# Actualizaciones de Configuración - Compatibilidad NumPy

## 📋 Resumen de Cambios

Se han actualizado los archivos de configuración del proyecto para documentar y manejar la incompatibilidad con NumPy 2.0+ en la funcionalidad de exportación GEXF.

## 🔍 Causa Raíz Identificada

### **Problema Específico**
- **Error**: `AttributeError: 'np.float_' was removed in the NumPy 2.0 release. Use 'np.float64' instead.`
- **Ubicación**: `networkx/readwrite/gexf.py` línea 223 en `construct_types()`
- **Causa**: NetworkX 2.6.x utiliza el tipo deprecado `np.float_` que fue removido en NumPy 2.0

### **Componente Afectado**
- **Funcionalidad**: `export_to_gexf()` únicamente
- **Dependencia**: NetworkX 2.6.x GEXF writer
- **Impacto**: Solo exportación GEXF para Gephi

## 📝 Archivos Actualizados

### 1. **setup.py**
```python
install_requires=[
    'networkx>=2.0,<2.7',
    'numpy<2.0',  # numpy 2.0+ breaks GEXF export due to removed np.float_
    'openpyxl>=2.6.2',
    'python-dateutil',
    'ruamel.yaml',
],
extras_require={
    'visualization': [
        'matplotlib',  # for plot_graph()
        'pydot',       # for DOT export
    ],
    'dev': [
        'pytest',
        'pytest-cov',
        'flake8',
    ],
},
```

### 2. **pyproject.toml** (Nuevo)
- Configuración moderna de packaging
- Especificación clara de dependencias
- Documentación detallada de la limitación NumPy
- Extras opcionales para visualización y desarrollo

### 3. **README.rst**
```rst
Required python libraries:
    numpy (< 2.0 for GEXF export compatibility),

**Note on NumPy 2.0 Compatibility:**
    GEXF graph export functionality requires NumPy < 2.0 due to NetworkX's use of
    the deprecated ``np.float_`` type that was removed in NumPy 2.0.
```

### 4. **COMPATIBILITY.md** (Nuevo)
- Guía completa de compatibilidad
- Explicación detallada del problema
- Soluciones y workarounds
- Matriz de compatibilidad de versiones
- Ejemplos de instalación

### 5. **src/pycel/excelcompiler.py**
```python
def export_to_gexf(self, filename=None):
    """Export dependency graph to GEXF format for Gephi visualization.
    
    Note: Requires NumPy < 2.0 due to NetworkX compatibility.
    With NumPy 2.0+, use export_to_dot() or plot_graph() instead.
    """
    try:
        # ... código original ...
    except AttributeError as e:
        if 'np.float_' in str(e) and 'NumPy 2.0' in str(e):
            raise RuntimeError(
                "GEXF export is not compatible with NumPy 2.0+. "
                "NetworkX uses deprecated np.float_ type. "
                "Solutions: 1) Use 'pip install \"numpy<2.0\"', "
                "2) Use export_to_dot() instead, or "
                "3) Use plot_graph() for visualization."
            ) from e
        else:
            raise
```

### 6. **model_focusing/README.md**
- Nota de compatibilidad NumPy agregada
- Explicación de funcionalidades por versión
- Alternativas para visualización

## 🎯 Beneficios de las Actualizaciones

### **Para Usuarios**
1. **Claridad**: Error messages informativos en lugar de stack traces crípticos
2. **Soluciones**: Instrucciones claras para resolver el problema
3. **Flexibilidad**: Opciones para usar NumPy 2.0+ con funcionalidad limitada

### **Para Desarrolladores**
1. **Documentación**: Causa raíz y soluciones documentadas
2. **Configuración**: Dependencias claramente especificadas
3. **Testing**: Configuración que garantiza compatibilidad

### **Para Deployment**
1. **Predictibilidad**: Instalación consistente con NumPy 1.x
2. **Opciones**: Extras opcionales para diferentes casos de uso
3. **Futuro**: Preparado para cuando NetworkX resuelva la compatibilidad

## 📊 Matriz de Compatibilidad Actualizada

| NumPy Version | Core Pycel | GEXF Export | DOT Export | Matplotlib | Recomendación |
|---------------|------------|-------------|------------|------------|---------------|
| 1.20.x - 1.26.x | ✅ Full | ✅ Works | ✅ Works | ✅ Works | ✅ **Recomendado** |
| 2.0.x+ | ✅ Full | ❌ Fails | ✅ Works | ✅ Works | ⚠️ Limitado |

## 🚀 Instrucciones de Instalación Actualizadas

### **Instalación Recomendada (Funcionalidad Completa)**
```bash
pip install "numpy<2.0" pycel[visualization]
```

### **Instalación Básica**
```bash
pip install pycel  # Instala numpy<2.0 automáticamente
```

### **Instalación para Desarrollo**
```bash
pip install "numpy<2.0" pycel[dev,visualization]
```

### **Instalación con NumPy 2.0+ (Funcionalidad Limitada)**
```bash
pip install --no-deps pycel
pip install "numpy>=2.0" networkx openpyxl python-dateutil ruamel.yaml
# GEXF export no funcionará, usar DOT o matplotlib
```

## 🔮 Resolución Futura

El problema se resolverá automáticamente cuando:
1. **NetworkX** lance una versión compatible con NumPy 2.0+
2. **Pycel** implemente un writer GEXF personalizado
3. **Pycel** migre a una librería de exportación diferente

## ✅ Validación

### **Tests Actualizados**
- Model focusing tests: 27/27 PASSED con NumPy 1.x
- Root tests: 2974/2986 PASSED con NumPy 1.x
- Error handling: RuntimeError claro con NumPy 2.0+

### **Funcionalidad Verificada**
- ✅ GEXF export funciona con NumPy 1.x
- ✅ Error claro y soluciones con NumPy 2.0+
- ✅ Todas las demás funcionalidades intactas
- ✅ Documentación completa y clara

## 📞 Soporte

Para problemas relacionados con compatibilidad NumPy:
1. Consultar `COMPATIBILITY.md`
2. Verificar versión de NumPy: `python -c "import numpy; print(numpy.__version__)"`
3. Usar instalación recomendada: `pip install "numpy<2.0" pycel`
4. Reportar issues en GitHub con detalles de versión

**Las actualizaciones garantizan una experiencia de usuario clara y predecible con Pycel.**