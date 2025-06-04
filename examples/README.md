# PyHDLio Examples

This directory demonstrates PyHDLio's capabilities for VHDL parsing and analysis.

## Simple Example (`simple/`)

The simple example demonstrates both PyHDLio AST and pyVHDLModel approaches in a single comprehensive script:

- **File**: `simple/simple.py`
- **Features**: 
  - PyHDLio AST parsing (lightweight, currently available)
  - pyVHDLModel integration preview (rich semantics, future)
  - Direct comparison of both approaches
  - Programmatic access examples
  - Error handling demonstration

### Running the Example

```bash
cd PyHDLio/examples/vhdl/simple
python simple.py
```

### Expected Output

The example produces detailed output showing both approaches:

1. **PyHDLio AST Approach**: Current implementation with formatted reports and programmatic access
2. **pyVHDLModel Approach**: Preview of planned integration with rich object hierarchy
3. **Comparison**: Side-by-side analysis of benefits and use cases

### Features Demonstrated

- **Entity Parsing**: Extract entity names, generics, and ports
- **Port Grouping**: Group ports based on source code proximity (blank lines)
- **Dual Access**: Both lightweight AST and rich object model approaches
- **Error Handling**: Graceful handling of file and syntax errors
- **Programmatic Access**: Direct manipulation of parsed structures
- **Comparison**: Clear guidance on when to use each approach

### VHDL Test File

The example uses `simple.vhd` with:
- Entity with generics (WIDTH, DEPTH)
- Grouped ports (control signals + data signals)
- Proper VHDL structure for testing

## Prerequisites

```bash
# Install PyHDLio in development mode
pip install -e ./PyHDLio

# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate    # Linux/Mac
```

## Development Notes

This example serves multiple purposes:
- **Learning Tool**: Understand PyHDLio's capabilities
- **Integration Preview**: See planned pyVHDLModel integration
- **Decision Guide**: Choose the right approach for your needs
- **Testing**: Verify PyHDLio functionality

The unified approach demonstrates that both PyHDLio AST and pyVHDLModel can coexist and complement each other, with users choosing the appropriate tool for their specific requirements.

## Available Examples

### VHDL Examples (`vhdl/`)

- **`simple/`** - Basic entity reporting example
  - `simple.vhd` - VHDL entity with ports (no generics)
  - `simple.py` - Python script demonstrating entity parsing and reporting

## Features Demonstrated

### Entity Parsing
- Parse VHDL files into structured AST representations
- Extract entity names, generics, and ports
- Handle both simple and complex entity declarations

### Entity Reporting
- **Flat Mode**: Display all ports in a simple list
- **Grouped Mode**: Display ports grouped by source proximity (blank lines or whitespace gaps separate groups)
- Clean, readable output format
- Support for entities with or without generics/ports

### Error Handling
- Graceful handling of file not found errors
- VHDL syntax error reporting
- Robust parsing with meaningful error messages

## Code Structure

### Basic Usage Pattern

```python
from hdlio.vhdl.parse_vhdl import parse_vhdl, VHDLSyntaxError
from hdlio.vhdl.reporter import report_entities

def main():
    vhdl_file = "path/to/your/file.vhd"
    
    try:
        # Parse VHDL file into AST
        module = parse_vhdl(vhdl_file, mode='ast')
        
        # Report all entities (shows generics, flat ports, and grouped ports)
        print(report_entities(module))
        
    except FileNotFoundError:
        print(f"Error: {vhdl_file} not found")
    except VHDLSyntaxError as e:
        print(f"Syntax error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

### Advanced Usage - Modular Reporting

```python
from hdlio.vhdl.parse_vhdl import parse_vhdl
from hdlio.vhdl.reporter import report_generics, report_ports_flat, report_ports_grouped

# Parse VHDL file
module = parse_vhdl(vhdl_file, mode='ast')
entity = module.entities[0]

# Use individual reporting functions with custom indentation
print(f"Entity: {entity.name}")
print(report_generics(entity, indent=2))
print(report_ports_flat(entity, indent=2))
print(report_ports_grouped(entity, indent=2))
```

### AST Access

```python
# Parse into AST for programmatic access
module = parse_vhdl(vhdl_file, mode='ast')

# Access entities
for entity in module.entities:
    print(f"Entity: {entity.name}")
    
    # Access generics
    for generic in entity.generics:
        print(f"  Generic: {generic.name}: {generic.type} = {generic.default_value}")
    
    # Access ports (flat list)
    for port in entity.ports:
        print(f"  Port: {port.name}: {port.direction} {port.type}")
    
    # Access port groups
    for i, group in enumerate(entity.port_groups, 1):
        print(f"  Group {i}:")
        for port in group.ports:
            print(f"    - {port.name}: {port.direction} {port.type}")
```

## Adding New Examples

When adding new examples:

1. **Create appropriate directory structure** under the relevant category
2. **Include both sample VHDL files and Python scripts**
3. **Add clear documentation** explaining the example's purpose
4. **Update this README** with the new example information
5. **Test the example** to ensure it works as documented

## Related Documentation

- **[Main README](../../README.md)** - Project overview and setup
- **[Testing Guide](../../tests/README.md)** - Comprehensive testing instructions
- **[Implementation Plan](../../doc/plan_1.md)** - Detailed development plan 