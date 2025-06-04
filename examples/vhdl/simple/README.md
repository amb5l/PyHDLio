# PyHDLio Simple VHDL Examples

This directory contains simple examples of the AST and model APIs.

## Files

- **`simple.vhd`** - Sample VHDL entity with generics and ports
- **`simple_ast.py`** - Report entity details using AST API
- **`simple_model.py`** - Report entity details using model API
- **`README.md`** - This documentation

## Examples

### 1. Simple AST Example (`simple_ast.py`)

Demonstrates parsing to PyHDLio's lightweight AST (Abstract Syntax Tree):

```bash
python simple_ast.py
```

**Output:**
```
Entity:  counter
Generics:
  WIDTH: integer = 8
  DEPTH: integer = 16
Ports:
  clk: in STD_LOGIC
  reset: in STD_LOGIC
  start: in STD_LOGIC
  count: out STD_LOGIC_VECTOR(WIDTH - 1 downto 0)
Port Groups:
  Group 1:
    clk: in STD_LOGIC
    reset: in STD_LOGIC
  Group 2:
    start: in STD_LOGIC
    count: out STD_LOGIC_VECTOR(WIDTH - 1 downto 0)
```

### 2. Simple Model Example (`simple_model.py`)

Demonstrates parsing to pyVHDLModel's rich object model:

```bash
python simple_model.py
```

