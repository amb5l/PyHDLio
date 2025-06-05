# PyHDLio

This is the main repository for the `pyhdlio` Python package, which is intended to support the input and output of HDL source.

Features:
- VHDL parsing (source → AST)
  - port groups inferred from source proximity (empty lines, comments)
- VHDL object model (AST → model)
- VHDL output (model → source) (coming soon)
- Verilog parsing (source → AST) (planned)
- Verilog object model (AST → model) (planned)
- Verilog output (model → source) (planned)

## Acknowledgements

- Language processing uses [ANTLR](https://www.antlr.org/).
- The VHDL grammar was copied from [pyVHDLParser](https://github.com/VHDL/pyVHDLParser).
- The VHDL object model uses [pyVHDLModel](https://github.com/VHDL/pyVHDLModel).

## Installation

`pyhdlio` may be installed using `pip`:

```bash
pip install pyhdlio
```

Alternatively, clone this repository and install the package from it:

```bash
git clone https://github.com/amb5l/PyHDLio
cd PyHDLio
pip install -e .
```

## Examples

See the examples readme [here](examples/README.md).

## Development

See https://github.com/amb5l/PyHDLio-dev.


## License

PyHDLio is distributed under the GNU General Public License v3.0 (GPLv3). See [LICENSE.md](./LICENSE.md) for details.

For license information on ANTLR, see: [ANTLR 4 License](https://www.antlr.org/license.html).

For license information for pyVHDLModel and pyVHDLParser, see:
- [pyVHDLModel on GitHub](https://github.com/Paebbels/pyVHDLModel)
- [pyVHDLParser on GitHub](https://github.com/Paebbels/pyVHDLParser)
