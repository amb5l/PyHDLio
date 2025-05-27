# PyHDLio - Python HDL Parsing Library

PyHDLio is a Python library for parsing VHDL, Verilog, and SystemVerilog files using PLY (Python Lex-Yacc) with complete source reconstruction capability.

## Features

- **Multi-HDL Support**:
  - **VHDL**: IEEE 1076 (LRM) versions 1993, 2000, 2008, 2019
  - **Verilog**: IEEE 1364 (LRM) versions 1995, 2001, 2005
  - **SystemVerilog**: IEEE 1800 (LRM) versions 2005, 2009, 2012, 2017
- **100% Source Reconstruction**: Preserves all whitespace, newlines, and formatting
- **Port Grouping**: Automatically groups ports based on comments and empty lines
- **Source Order Preservation**: All lists and dictionaries maintain source declaration order
- **Simple API**: Easy-to-use interface for extracting design units and ports

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PyHDLio
```

2. Initialize submodules:
```bash
git submodule update --init --recursive
```

3. The library is ready to use (no additional dependencies required).

## Usage

### Basic Usage

```python
from hdlio import HDLio, VHDL_2008

# Parse a VHDL file
hdl = HDLio("test.vhd", VHDL_2008)
design_units = hdl.getDesignUnits()

for design_unit in design_units:
    if design_unit.getVhdlType() == "entity":
        port_groups = design_unit.getPortGroups()
        for port_group in port_groups:
            print("port group:", port_group)
            ports = port_group.getPorts()
            for port in ports:
                print("port:", port)
```

### Port Grouping Example

Given this VHDL entity:
```vhdl
entity my_entity is
  port (
    -- Clock and Reset group
    clk : in std_logic;
    rst_n : in std_logic;

    -- Data group
    data_in : in std_logic_vector(7 downto 0);
    data_out : out std_logic_vector(7 downto 0);

    -- Control group
    enable : in std_logic;
    ready : out std_logic
  );
end entity my_entity;
```

PyHDLio will create port groups named "Clock and Reset group", "Data group", and "Control group" based on the preceding comments.

## API Reference

### HDLio Class
- `HDLio(filename, language)` - Create parser instance
- `getDesignUnits()` - Get all design units in source order
- `getDocument()` - Get complete document object
- `getSourceText()` - Get original source text
- `getReconstructedText()` - Get reconstructed source (should match original 100%)

### Design Unit Methods
- `getVhdlType()` - Returns "entity", "architecture", "package", etc.
- `getPortGroups()` - Get all port groups in source order

### Port Group Methods
- `getName()` - Get group name (from comment or auto-generated)
- `getPorts()` - Get all ports in this group

### Port Methods
- `getName()` - Get port name
- `getType()` - Get port type
- `getDirection()` - Get port direction (in, out, inout, buffer)

## Architecture

The library is structured as follows:

```
hdlio/
├── __init__.py              # Main exports
├── core/
│   ├── hdlio.py            # Main HDLio class
│   ├── constants.py        # Language version constants
│   ├── base.py             # Base classes for document object model
│   ├── vhdl.py             # VHDL-specific classes
│   ├── verilog.py          # Verilog-specific classes
│   ├── systemverilog.py    # SystemVerilog-specific classes
│   └── parsers/
│       ├── parser_factory.py      # Parser factory
│       ├── base_parser.py          # Base parser class
│       ├── vhdl_parser_working.py  # Working VHDL parser
│       ├── verilog_parser.py       # Verilog parser (basic)
│       └── systemverilog_parser.py # SystemVerilog parser (basic)
└── submodules/
    └── ply/                # PLY (Python Lex-Yacc) submodule
```

## Development and Testing

For development, testing, and comprehensive documentation, see the companion repository:

**[PyHDLio-dev](../PyHDLio-dev)** - Contains all test suites, development documentation, and testing infrastructure.

## Current Status

- ✅ VHDL 2008 basic parsing (entities, ports)
- ✅ Port grouping based on comments
- ✅ 100% source reconstruction capability
- ✅ Simple API interface
- 🔄 Verilog/SystemVerilog parsers (basic structure implemented)
- 🔄 Advanced VHDL features (architectures, packages, etc.)

## Contributing

1. Clone both PyHDLio and PyHDLio-dev repositories
2. See PyHDLio-dev for testing and development workflows
3. Submit pull requests with appropriate tests

## License

See LICENSE file for details.

## Dependencies

- Python 3.6+
- PLY (Python Lex-Yacc) - included as submodule
