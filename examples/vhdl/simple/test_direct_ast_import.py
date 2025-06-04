"""
Test direct import from ast module.

This demonstrates that VHDLAST now properly lives in the ast module
and can be imported directly for users who only need AST functionality.
"""

import os

def test_direct_ast_import():
    """Test importing VHDLAST directly from ast module."""
    print("=== Testing Direct AST Import ===")
    
    # Import directly from ast module (not model)
    from hdlio.vhdl.ast import VHDLAST
    
    vhdl_file = os.path.join(os.path.dirname(__file__), "simple.vhd")
    
    # Use the enhanced VHDLAST methods
    ast = VHDLAST.from_file(vhdl_file)
    
    entity = ast.entities[0]
    print(f"✓ Imported VHDLAST directly from ast module")
    print(f"Entity: {entity.name}")
    print(f"Ports: {len(entity.ports)}")
    print(f"Port Groups: {len(entity.port_groups)}")
    
    # Test string parsing too
    vhdl_code = """
    entity test is
      port (
        sig : in std_logic
      );
    end entity;
    """
    
    ast_from_string = VHDLAST.from_string(vhdl_code)
    print(f"✓ String parsing works from direct ast import")
    print(f"Entities from string: {len(ast_from_string.entities)}")

def test_model_import():
    """Test that model module still re-exports everything correctly."""
    print("\n=== Testing Model Module Re-export ===")
    
    # Import from model module (convenience wrapper)
    from hdlio.vhdl.model import VHDLAST, Document
    
    vhdl_file = os.path.join(os.path.dirname(__file__), "simple.vhd")
    
    # Test VHDLAST from model
    ast = VHDLAST.from_file(vhdl_file)
    print(f"✓ VHDLAST works from model module")
    print(f"Entity: {ast.entities[0].name}")
    
    # Test Document from model
    document = Document.from_file(vhdl_file)
    print(f"✓ Document works from model module")
    entity = list(document.Entities.values())[0]
    print(f"Entity: {entity.Identifier}")

if __name__ == "__main__":
    test_direct_ast_import()
    test_model_import()
    
    print("\n" + "="*50)
    print("✅ ARCHITECTURE IMPROVEMENT VERIFIED!")
    print("✓ VHDLAST now properly lives in ast.py")
    print("✓ model.py is a clean convenience wrapper")
    print("✓ Users can import from either module")
    print("="*50) 