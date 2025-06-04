# PyHDLio

This is the main repository for the `pyhdlio` Python package.

The intial goals of the `pyhdlio` package are:
1) to enable reading details of entities and their generics and ports from VHDL source files;
2) to enable the creation of VHDL source from an object hierarchy.

Support for Verilog is planned.

## Acknowledgements

Language processing uses [ANTLR](https://www.antlr.org/).

The VHDL grammar was written by Denis Gavrish.

The VHDL object model uses [pyVHDLModel](https://github.com/VHDL/pyVHDLModel).

## Installation

End users may obtain and install `pyhdlio` by using `pip`:

```bash
pip install pyhdlio
```

Alternatively, clone this repository and install the package from it:

```bash
git clone
```

## Examples

See the examples readme [here](examples/README.md).

## Development

See https://github.com/amb5l/PyHDLio-dev.
