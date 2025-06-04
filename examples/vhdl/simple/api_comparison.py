"""
API Comparison: Old Manual Approach vs New Enhanced API

This example demonstrates the difference between the old way of manually
chaining parsing functions and the new enhanced API with integrated parsing.
"""

import os

def old_approach():
    """Demonstrate the old manual approach with separate parsing and conversion."""
    print("=== OLD APPROACH (Manual Chaining) ===")
    
    # Old way: Import separate functions and chain them manually
    from hdlio.vhdl.parse_vhdl import parse_vhdl
    from hdlio.vhdl.converters.pyvhdlmodel_converter import convert_to_pyvhdlmodel
    
    vhdl_file = os.path.join(os.path.dirname(__file__), "simple.vhd")
    
    # Step 1: Parse to PyHDLio AST
    ast = parse_vhdl(vhdl_file, mode='ast')
    
    # Step 2: Convert to pyVHDLModel Document  
    document = convert_to_pyvhdlmodel(ast)
    
    # Step 3: Use the result
    entity = list(document.Entities.values())[0]
    print(f"Entity: {entity.Identifier}")
    print(f"Ports: {len(entity.PortItems)}")
    print(f"Port Groups: {len(entity.PortGroups)}")

def new_approach():
    """Demonstrate the new enhanced API with integrated parsing."""
    print("\n=== NEW APPROACH (Enhanced API) ===")
    
    # New way: Import enhanced classes with integrated parsing
    from hdlio.vhdl.model import VHDLAST, Document
    
    vhdl_file = os.path.join(os.path.dirname(__file__), "simple.vhd")
    
    # Option 1: Parse directly to PyHDLio AST
    print("Option 1: Parse directly to VHDLAST")
    ast = VHDLAST.from_file(vhdl_file)
    entity = ast.entities[0]
    print(f"Entity: {entity.name}")
    print(f"Ports: {len(entity.ports)}")
    print(f"Port Groups: {len(entity.port_groups)}")
    
    print("\nOption 2: Parse directly to pyVHDLModel Document")
    # Option 2: Parse directly to pyVHDLModel Document
    document = Document.from_file(vhdl_file)
    entity = list(document.Entities.values())[0]
    print(f"Entity: {entity.Identifier}")
    print(f"Ports: {len(entity.PortItems)}")
    print(f"Port Groups: {len(entity.PortGroups)}")
    
    print("\nOption 3: Parse to AST, then convert with from_ast")
    # Option 3: Two-step conversion using from_ast
    ast = VHDLAST.from_file(vhdl_file)
    document = Document.from_ast(ast)
    entity = list(document.Entities.values())[0]
    print(f"Entity: {entity.Identifier}")
    print(f"Ports: {len(entity.PortItems)}")
    print(f"Port Groups: {len(entity.PortGroups)}")

def string_parsing_example():
    """Demonstrate string-based parsing (only available with new API)."""
    print("\n=== NEW FEATURE: String-Based Parsing ===")
    
    from hdlio.vhdl.model import VHDLAST, Document
    
    vhdl_code = """
    entity simple_counter is
      port (
        clk : in std_logic;
        count : out natural
      );
    end entity simple_counter;
    """
    
    # Parse VHDL code directly from string
    ast = VHDLAST.from_string(vhdl_code)
    
    # Option 1: Direct string to Document
    document_direct = Document.from_string(vhdl_code, filename="inline_code.vhd")
    
    # Option 2: String to AST, then convert with from_ast
    document_from_ast = Document.from_ast(ast)
    
    print("Parsed from string:")
    print(f"AST entities: {len(ast.entities)}")
    print(f"Direct Document entities: {len(document_direct.Entities)}")
    print(f"from_ast Document entities: {len(document_from_ast.Entities)}")

if __name__ == "__main__":
    old_approach()
    new_approach() 
    string_parsing_example()
    
    print("\n" + "="*60)
    print("RECOMMENDATION: Use the new enhanced API from hdlio.vhdl.model")
    print("✓ Cleaner and more Pythonic")
    print("✓ Multiple parsing approaches (file, string, AST conversion)")
    print("✓ Better error handling and type safety")
    print("✓ Consistent architecture (from_file builds on from_string)")
    print("="*60) 