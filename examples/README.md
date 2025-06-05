# PyHDLio Examples

This directory contains the following examples:

1. `vhdl_in`

    This example reads in a VHDL source and builds an object hierarchy corresponding to its design units. Basic information about the design units is then dumped. At present, entity and component declarations in packages are captured, with details of generics and ports.

2. `vhdl_out`

    This **WORK IN PROGRESS** example demonstrates the process of creating an entity and architecture using the object model, and of converting the objects to VHDL source.

## Adding New Examples

When adding new examples:

1. **Create an appropriately named directory** under `examples/`
2. **Include both sample HDL files and Python scripts**
3. **Add clear documentation** explaining the example's purpose
4. **Update this README** with the new example information
5. **Test the example** to ensure it works as documented

# Related Documentation

- **[Main README](../../README.md)** - Project overview and setup
- **[Testing Guide](../../tests/README.md)** - Comprehensive testing instructions
- **[Implementation Plan](../../doc/plan_1.md)** - Detailed development plan