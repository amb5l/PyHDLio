# PyHDLio VHDL Examples

This directory contains examples demonstrating different approaches to VHDL parsing and modeling with PyHDLio.

## Files

### Current Examples (Enhanced API - Recommended)
- **`simple_ast_new.py`** - Parse to PyHDLio AST using enhanced API
- **`simple_model_new.py`** - Parse to pyVHDLModel Document using enhanced API  
- **`test_from_ast.py`** - Demonstrates the from_ast conversion method
- **`test_direct_ast_import.py`** - Shows direct import from ast module vs model convenience wrapper
- **`api_comparison.py`** - Comprehensive comparison of old vs new approaches
- **`test_string_parsing.py`** - Demonstrates string-based parsing

### Legacy Examples (For Reference)
- **`simple_ast.py`** - Parse to PyHDLio AST using manual approach
- **`simple_model.py`** - Parse to pyVHDLModel using manual conversion

### Test VHDL File
- **`simple.vhd`** - Sample VHDL entity with generics and ports

## Architecture Overview

PyHDLio now has a clean, well-organized architecture:

### 📁 `hdlio.vhdl.ast` - Core AST Module
Contains the fundamental AST classes and enhanced `VHDLAST` with parsing methods:
```python
from hdlio.vhdl.ast import VHDLAST

# Direct AST operations
ast = VHDLAST.from_file("file.vhd")
ast = VHDLAST.from_string(vhdl_code)
```

### 📁 `hdlio.vhdl.model` - Convenience Wrapper
Main entry point that re-exports AST classes and adds enhanced `Document`:
```python
from hdlio.vhdl.model import VHDLAST, Document

# Complete API in one import
ast = VHDLAST.from_file("file.vhd")  
document = Document.from_file("file.vhd")
document = Document.from_ast(ast)
```

**Recommendation**: Use `hdlio.vhdl.model` for most cases as it provides the complete API.

## API Comparison

### ❌ Old Manual Approach
```python
# Multiple imports and manual chaining required
from hdlio.vhdl.parse_vhdl import parse_vhdl
from hdlio.vhdl.converters.pyvhdlmodel_converter import convert_to_pyvhdlmodel

# Step 1: Parse to AST
ast = parse_vhdl("file.vhd", mode='ast')

# Step 2: Convert to pyVHDLModel (if needed)
document = convert_to_pyvhdlmodel(ast)
```

### ✅ New Enhanced API (Recommended)
```python
# Single import, direct parsing
from hdlio.vhdl.model import VHDLAST, Document

# Parse directly to desired format
ast = VHDLAST.from_file("file.vhd")
document = Document.from_file("file.vhd")

# Parse from strings
ast = VHDLAST.from_string(vhdl_code)
document = Document.from_string(vhdl_code, filename="optional.vhd")

# Convert existing AST to Document
document = Document.from_ast(ast)
```

### 🎯 Direct AST Import (For AST-only use)
```python
# If you only need AST functionality
from hdlio.vhdl.ast import VHDLAST

ast = VHDLAST.from_file("file.vhd")
ast = VHDLAST.from_string(vhdl_code)
```

## Key Benefits of Enhanced API

1. **Clean architecture** - `VHDLAST` lives in `ast.py` where it belongs
2. **Flexible imports** - Import from `ast` or `model` depending on needs
3. **Pythonic design** - Class methods like `from_file()`, `from_string()`, and `from_ast()`
4. **Less boilerplate** - No manual chaining of parsing and conversion
5. **String parsing** - Parse VHDL code directly from strings
6. **AST conversion** - Convert existing PyHDLio AST to pyVHDLModel Document
7. **Better error handling** - Unified exception handling
8. **Type safety** - Enhanced type hints and documentation
9. **Cleaner architecture** - `from_file` builds on `from_string` (not the reverse)

## Parsing Methods

The enhanced API provides three main parsing approaches:

### 1. Direct File Parsing
```python
# Parse file directly to AST
ast = VHDLAST.from_file("counter.vhd")

# Parse file directly to pyVHDLModel Document  
document = Document.from_file("counter.vhd")
```

### 2. String Parsing
```python
vhdl_code = "entity test is ... end entity;"

# Parse string to AST
ast = VHDLAST.from_string(vhdl_code)

# Parse string to pyVHDLModel Document
document = Document.from_string(vhdl_code, filename="test.vhd")
```

### 3. AST Conversion
```python
# If you already have a PyHDLio AST
ast = VHDLAST.from_file("counter.vhd")

# Convert it to pyVHDLModel Document
document = Document.from_ast(ast)
```

## Running the Examples

```bash
# Test the enhanced API
python simple_ast_new.py
python simple_model_new.py

# Test the from_ast conversion method
python test_from_ast.py

# Test direct AST import vs model wrapper
python test_direct_ast_import.py

# Compare old vs new approaches  
python api_comparison.py

# Test string parsing
python test_string_parsing.py

# Legacy examples (still work)
python simple_ast.py
python simple_model.py
```

## Migration Guide

If you're using the old approach, migration is simple:

### For PyHDLio AST:
```python
# Old
from hdlio.vhdl.parse_vhdl import parse_vhdl
ast = parse_vhdl("file.vhd", mode='ast')

# New (Option 1: Complete API)
from hdlio.vhdl.model import VHDLAST
ast = VHDLAST.from_file("file.vhd")

# New (Option 2: AST-only)  
from hdlio.vhdl.ast import VHDLAST
ast = VHDLAST.from_file("file.vhd")
```

### For pyVHDLModel:
```python
# Old
from hdlio.vhdl.parse_vhdl import parse_vhdl
from hdlio.vhdl.converters.pyvhdlmodel_converter import convert_to_pyvhdlmodel
ast = parse_vhdl("file.vhd", mode='ast') 
document = convert_to_pyvhdlmodel(ast)

# New (Option 1: Direct)
from hdlio.vhdl.model import Document  
document = Document.from_file("file.vhd")

# New (Option 2: Via AST)
from hdlio.vhdl.model import VHDLAST, Document
ast = VHDLAST.from_file("file.vhd")
document = Document.from_ast(ast)
```

## Output Example

All examples produce identical output, demonstrating that port grouping and type information are preserved:

```
Entity:  counter
Generics:
  WIDTH: integer = 8
  DEPTH: natural = 16
Ports:
  clk: in STD_LOGIC
  reset: in STD_LOGIC
  start: in STD_LOGIC_VECTOR(WIDTH - 1 downto 0)
  count: out STD_LOGIC_VECTOR(WIDTH - 1 downto 0)
Port Groups:
  Group 1:
    clk: in STD_LOGIC
    reset: in STD_LOGIC
  Group 2:
    start: in STD_LOGIC_VECTOR(WIDTH - 1 downto 0)
    count: out STD_LOGIC_VECTOR(WIDTH - 1 downto 0)
``` 