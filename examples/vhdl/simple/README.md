# PyHDLio Simple VHDL Example

This directory contains a simple example demonstrating VHDL parsing with PyHDLio's consolidated API.

## Files

- **`simple.vhd`** - Sample VHDL entity with generics and ports
- **`simple_ast.py`** - Parse to PyHDLio AST using consolidated API
- **`simple_model.py`** - Parse to pyVHDLModel Document using consolidated API
- **`README.md`** - This documentation

## PyHDLio Consolidated API

PyHDLio provides a clean, consolidated API for VHDL parsing:

```python
from hdlio.vhdl.model import VHDLAST, Document

# Parse directly to PyHDLio AST
ast = VHDLAST.from_file("simple.vhd")

# Parse directly to pyVHDLModel Document (requires pyVHDLModel)
document = Document.from_file("simple.vhd")

# Convert existing AST to Document
document = Document.from_ast(ast)

# Parse from strings
ast = VHDLAST.from_string(vhdl_code)
document = Document.from_string(vhdl_code, filename="optional.vhd")
```

## Examples

### 1. PyHDLio AST Example (`simple_ast.py`)

Demonstrates parsing to PyHDLio's lightweight AST format:

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

### 2. pyVHDLModel Document Example (`simple_model.py`)

Demonstrates parsing to pyVHDLModel's rich object model:

```bash
python simple_model.py
```

**Note:** Requires `pyVHDLModel` to be installed:
```bash
pip install pyVHDLModel
```

## Key Features

### ✅ Consolidated API
- Single import: `from hdlio.vhdl.model import VHDLAST, Document`
- Class methods: `from_file()`, `from_string()`, `from_ast()`
- No manual chaining of functions required

### ✅ PyHDLio AST (Lightweight)
- Fast parsing and minimal dependencies
- Source-proximity port grouping preserved
- Perfect for quick analysis and reporting
- Simple dataclass structures

### ✅ pyVHDLModel Document (Rich Object Model)
- Standards-compliant VHDL representation
- Rich type system (Mode enums, Expression objects)
- Integration with pyVHDLModel ecosystem
- Advanced analysis capabilities

### ✅ Flexible Parsing
- Parse from files or strings
- Convert between representations
- Graceful error handling

## VHDL Sample

The `simple.vhd` file contains a basic counter entity:

```vhdl
entity counter is
  generic (
    WIDTH : integer := 8;
    DEPTH : integer := 16
  );
  port (
    clk   : in  STD_LOGIC;
    reset : in  STD_LOGIC;
    
    start : in  STD_LOGIC;
    count : out STD_LOGIC_VECTOR(WIDTH - 1 downto 0)
  );
end entity counter;
```

## Usage Recommendations

- **Use PyHDLio AST** (`simple_ast.py`) for:
  - Quick parsing and validation
  - Simple entity reporting
  - Lightweight tools and scripts
  - Educational purposes

- **Use pyVHDLModel Document** (`simple_model.py`) for:
  - Complex VHDL analysis
  - Integration with pyVHDLModel ecosystem
  - Standards-compliant processing
  - Advanced tool development

## Getting Started

1. **Run the AST example:**
   ```bash
   python simple_ast.py
   ```

2. **Install pyVHDLModel for Document example:**
   ```bash
   pip install pyVHDLModel
   python simple_model.py
   ```

3. **Explore the code** to see how the consolidated API works in practice.

## Migration from Legacy API

If you're using PyHDLio's older manual API, migration is straightforward:

```python
# Old approach (deprecated)
from hdlio.vhdl.parse_vhdl import parse_vhdl
from hdlio.vhdl.converters.pyvhdlmodel_converter import convert_to_pyvhdlmodel
ast = parse_vhdl("file.vhd", mode='ast')
document = convert_to_pyvhdlmodel(ast)

# New consolidated approach
from hdlio.vhdl.model import VHDLAST, Document
ast = VHDLAST.from_file("file.vhd")
document = Document.from_file("file.vhd")  # or Document.from_ast(ast)
```

The new API is cleaner, more Pythonic, and eliminates the need for manual function chaining. 