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

### Port Grouping
- **Automatic Grouping**: Ports are automatically grouped based on source code proximity
- **Flexible Access**: Access ports both as a flat list and as organized groups
- **Clean Structure**: Maintains source code organization for better understanding
- **Complete Information**: Includes generics, ports, and type constraints

### Error Handling
- Graceful handling of file not found errors
- VHDL syntax error reporting
- Robust parsing with meaningful error messages

## Code Structure

### Basic Usage Pattern

```python
from pyhdlio.vhdl.model import VHDLAST, VHDLSyntaxError

def main():
    vhdl_file = "path/to/your/file.vhd"

    try:
        # Parse VHDL file into AST
        ast = VHDLAST.from_file(vhdl_file)

        # Access and print entity information
        for entity in ast.entities:
            print(f"Entity: {entity.name}")

            # Display generics
            if entity.generics:
                print("Generics:")
                for generic in entity.generics:
                    default = f" = {generic.default_value}" if generic.default_value else ""
                    print(f"  {generic.name}: {generic.type}{default}")

            # Display ports
            if entity.ports:
                print("Ports:")
                for port in entity.ports:
                    constraint = f" {port.constraint}" if port.constraint else ""
                    print(f"  {port.name}: {port.direction} {port.type}{constraint}")

    except FileNotFoundError:
        print(f"Error: {vhdl_file} not found")
    except VHDLSyntaxError as e:
        print(f"Syntax error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

### pyVHDLModel Integration

```python
from pyhdlio.vhdl.model import Document, VHDLSyntaxError

def main():
    vhdl_file = "path/to/your/file.vhd"

    try:
        # Parse directly to pyVHDLModel Document
        document = Document.from_file(vhdl_file)

        # Access entities through pyVHDLModel API
        for entity in document.Entities.values():
            print(f"Entity: {entity.Identifier}")

            # Access generics
            if entity.GenericItems:
                print("Generics:")
                for generic in entity.GenericItems:
                    name = generic.Identifiers[0] if generic.Identifiers else "unnamed"
                    print(f"  {name}: {generic.Subtype}")

            # Access ports
            if entity.PortItems:
                print("Ports:")
                for port in entity.PortItems:
                    name = port.Identifiers[0] if port.Identifiers else "unnamed"
                    print(f"  {name}: {port.Mode.name.lower()} {port.Subtype}")

    except VHDLSyntaxError as e:
        print(f"Syntax error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
```

### AST Access with Port Grouping

```python
from pyhdlio.vhdl.model import VHDLAST

# Parse into AST for programmatic access
ast = VHDLAST.from_file(vhdl_file)

# Access entities
for entity in ast.entities:
    print(f"Entity: {entity.name}")

    # Access generics
    for generic in entity.generics:
        default = f" = {generic.default_value}" if generic.default_value else ""
        print(f"  Generic: {generic.name}: {generic.type}{default}")

    # Access ports (flat list)
    for port in entity.ports:
        constraint = f" {port.constraint}" if port.constraint else ""
        print(f"  Port: {port.name}: {port.direction} {port.type}{constraint}")

    # Access port groups (grouped by proximity in source)
    for i, group in enumerate(entity.port_groups, 1):
        print(f"  Group {i}:")
        for port in group.ports:
            constraint = f" {port.constraint}" if port.constraint else ""
            print(f"    - {port.name}: {port.direction} {port.type}{constraint}")
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