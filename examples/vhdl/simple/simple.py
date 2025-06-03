import os
from hdlio.vhdl.parse_vhdl import parse_vhdl

def main():
    # VHDL file path relative to this script
    vhdl_file = os.path.join(os.path.dirname(__file__), "simple.vhd")
    try:
        parse_tree = parse_vhdl(vhdl_file)
        print(f"Parse tree for {vhdl_file}:\n{parse_tree}")
    except FileNotFoundError:
        print(f"Error: {vhdl_file} not found")
    except Exception as e:
        print(f"Error parsing {vhdl_file}: {e}")

if __name__ == "__main__":
    main()
