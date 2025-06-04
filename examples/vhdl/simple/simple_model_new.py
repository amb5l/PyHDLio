import os, sys, traceback

from hdlio.vhdl.model import Document, VHDLSyntaxError

def main():
    vhdl_file = os.path.join(os.path.dirname(__file__), "simple.vhd")
    if not os.path.exists(vhdl_file):
        print(f"Error: VHDL file not found: {vhdl_file}")
        sys.exit(1)
    try:
        # New clean API - parse directly to pyVHDLModel Document
        document = Document.from_file(vhdl_file)
        
        for entity in document.Entities.values():
            print("Entity: ", entity.Identifier)

            # Display generics
            if entity.GenericItems:
                print("Generics:")
                for generic in entity.GenericItems:
                    # Get the first identifier
                    name = generic.Identifiers[0] if generic.Identifiers else "unnamed"

                    # Fix: Don't use truthiness check on Subtype since it returns False when unresolved
                    if hasattr(generic, 'Subtype') and generic.Subtype is not None and hasattr(generic.Subtype, 'Name'):
                        type_name = generic.Subtype.Name.Identifier
                    else:
                        type_name = "unknown"
                    default = f" = {generic.DefaultExpression}" if hasattr(generic, 'DefaultExpression') and generic.DefaultExpression else ""
                    print(f"  {name}: {type_name}{default}")
            else:
                print("Generics: None")

            # Display ports
            if entity.PortItems:
                print("Ports:")
                for port in entity.PortItems:
                    # Get the first identifier
                    name = port.Identifiers[0] if port.Identifiers else "unnamed"

                    # Fix: Don't use truthiness check on Subtype since it returns False when unresolved
                    if hasattr(port, 'Subtype') and port.Subtype is not None and hasattr(port.Subtype, 'Name'):
                        type_name = port.Subtype.Name.Identifier
                    else:
                        type_name = "unknown"
                    constraint = f"({port.Subtype.Constraint})" if hasattr(port, 'Subtype') and port.Subtype is not None and hasattr(port.Subtype, 'Constraint') and port.Subtype.Constraint else ""
                    print(f"  {name}: {port.Mode.name.lower()} {type_name}{constraint}")
            else:
                print("Ports: None")

            # Display port groups
            if entity.PortGroups:
                print("Port Groups:")
                for i, group in enumerate(entity.PortGroups):
                    group_name = group.Name if hasattr(group, 'Name') and group.Name else f"Group {i+1}"
                    print(f"  {group_name}:")

                    # Access the port items in the PortGroup using the correct property
                    group_ports = group.PortItems if hasattr(group, 'PortItems') else []
                    for port in group_ports:
                        # Get the first identifier
                        name = port.Identifiers[0] if port.Identifiers else "unnamed"

                        # Fix: Don't use truthiness check on Subtype since it returns False when unresolved
                        if hasattr(port, 'Subtype') and port.Subtype is not None and hasattr(port.Subtype, 'Name'):
                            type_name = port.Subtype.Name.Identifier
                        else:
                            type_name = "unknown"
                        constraint = f"({port.Subtype.Constraint})" if hasattr(port, 'Subtype') and port.Subtype is not None and hasattr(port.Subtype, 'Constraint') and port.Subtype.Constraint else ""
                        print(f"    {name}: {port.Mode.name.lower()} {type_name}{constraint}")
            else:
                print("Port Groups: None")

    except VHDLSyntaxError as e:
        print(f"VHDL syntax error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main() 