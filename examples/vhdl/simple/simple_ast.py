import os, sys, traceback

from pyhdlio.vhdl.model import VHDLAST, VHDLSyntaxError

def main():
    vhdl_file = os.path.join(os.path.dirname(__file__), "simple.vhd")
    if not os.path.exists(vhdl_file):
        print(f"Error: VHDL file not found: {vhdl_file}")
        sys.exit(1)
    try:
        # Create AST from source file
        ast = VHDLAST.from_file(vhdl_file)

        for entity in ast.entities:
            print("Entity: ", entity.name)

            # Display generics
            if entity.generics:
                print("Generics:")
                for generic in entity.generics:
                    default = f" = {generic.default_value}" if generic.default_value else ""
                    print(f"  {generic.name}: {generic.type}{default}")
            else:
                print("Generics: None")

            # Display ports
            if entity.ports:
                print("Ports:")
                for port in entity.ports:
                    constraint = f" {port.constraint}" if port.constraint else ""
                    print(f"  {port.name}: {port.direction} {port.type}{constraint}")
            else:
                print("Ports: None")

            # Display port groups
            if entity.port_groups:
                print("Port Groups:")
                for i, group in enumerate(entity.port_groups):
                    group_name = group.name if group.name else f"Group {i+1}"
                    print(f"  {group_name}:")
                    for port in group.ports:
                        constraint = f" {port.constraint}" if port.constraint else ""
                        print(f"    {port.name}: {port.direction} {port.type}{constraint}")
            else:
                print("Port Groups: None")

    except VHDLSyntaxError as e:
        print(f"VHDL syntax error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
