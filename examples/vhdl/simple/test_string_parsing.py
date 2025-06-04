"""Test script demonstrating string-based parsing with the new enhanced API."""

from hdlio.vhdl.model import VHDLAST, Document, VHDLSyntaxError

# Sample VHDL code as a string
vhdl_code = """
entity test_entity is
  generic (
    SIZE : natural := 8
  );
  port (
    clk   : in  std_logic;
    reset : in  std_logic;
    
    data_in  : in  std_logic_vector(SIZE-1 downto 0);
    data_out : out std_logic_vector(SIZE-1 downto 0)
  );
end entity test_entity;
"""

def test_ast_from_string():
    """Test VHDLAST.from_string() method."""
    print("=== Testing VHDLAST.from_string() ===")
    try:
        ast = VHDLAST.from_string(vhdl_code)
        entity = ast.entities[0]
        print(f"Entity: {entity.name}")
        print(f"Generics: {len(entity.generics)}")
        print(f"Ports: {len(entity.ports)}")
        print(f"Port Groups: {len(entity.port_groups)}")
        print("✓ VHDLAST.from_string() works!")
    except Exception as e:
        print(f"✗ Error: {e}")

def test_document_from_string():
    """Test Document.from_string() method."""
    print("\n=== Testing Document.from_string() ===")
    try:
        document = Document.from_string(vhdl_code, filename="test.vhd")
        entities = list(document.Entities.values())
        entity = entities[0]
        print(f"Entity: {entity.Identifier}")
        print(f"Generics: {len(entity.GenericItems)}")
        print(f"Ports: {len(entity.PortItems)}")
        print(f"Port Groups: {len(entity.PortGroups)}")
        print("✓ Document.from_string() works!")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_ast_from_string()
    test_document_from_string() 