# PyHDLio

A Python HDL parsing library using ANTLR4.

## Installation

To install from this repository, as an editable package:

```bash
pip install -e .
```

## Usage

```python
from hdlio.vhdl.parse_vhdl import parse_vhdl

# Parse a VHDL file
parse_tree = parse_vhdl("your_file.vhd")
print(f"Parse tree: {parse_tree}")
```

## Examples

Run the simple VHDL parsing example:
```bash
python examples/vhdl/simple/simple.py
```

## Development

See https://github.com/amb5l/PyHDLio-dev.
