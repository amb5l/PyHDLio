import os
from hdlio.vhdl.parse_vhdl import parse_vhdl, VHDLSyntaxError
from hdlio.vhdl.reporter import report_entities

def main():
    """Demonstrate VHDL parsing and entity reporting."""
    vhdl_file = os.path.join(os.path.dirname(__file__), "simple.vhd")
    try:
        module = parse_vhdl(vhdl_file, mode='ast')
        print(report_entities(module))
    except FileNotFoundError:
        print(f"Error: {vhdl_file} not found")
    except VHDLSyntaxError as e:
        print(f"Syntax error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
