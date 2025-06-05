import os, sys, traceback, argparse
import re
from typing import Union, Tuple

from pyhdlio.vhdl import (
    Document,
    VHDLSyntaxError,
    Context,
    Entity,
    Architecture,
    Configuration,
    Package,
    PackageBody,
    Component,
    PortSignalInterfaceItem,
    GenericConstantInterfaceItem
)


def name_type_str(x : Union[PortSignalInterfaceItem, GenericConstantInterfaceItem]) -> Tuple[str, str]:
    name_str = x.Identifiers[0]
    type_str = x.Subtype.Name.Identifier
    constraint_str = ""
    if hasattr(x.Subtype, 'Constraint') and x.Subtype.Constraint:
        constraint_str = str(x.Subtype.Constraint)
        constraint_str = constraint_str.replace('-', ' - ')
        constraint_str = re.sub(r'([0-9\w])downto([0-9\w])', r'\1 downto \2', constraint_str)
        constraint_str = re.sub(r'([0-9\w])\s*downto\s*([0-9\w])', r'\1 downto \2', constraint_str)
        constraint_str = ' '.join(constraint_str.split())
        constraint_str = f"({constraint_str})"
    return name_str, type_str + constraint_str

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Parse and dump VHDL file contents showing all design units',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python dump.py test.vhd           # Parse test.vhd
  python dump.py ../simple.vhd      # Parse relative path
  python dump.py /path/to/file.vhd  # Parse absolute path
        """
    )
    parser.add_argument(
        'vhdl_file',
        help='Path to the VHDL file to parse and dump'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output with debug information'
    )
    args = parser.parse_args()

    if not os.path.exists(args.vhdl_file):
        print(f"Error: VHDL file not found: {args.vhdl_file}")
        sys.exit(1)

    try:
        document = Document.FromFile(args.vhdl_file)

        print(f"Document instance created from: {document.Path}")
        if args.verbose:
            print(f"Absolute path: {os.path.abspath(args.vhdl_file)}")
            print(f"File size: {os.path.getsize(args.vhdl_file)} bytes")
        print()

        print(f"  Contexts : {len(document.Contexts)}")
        print()

        print(f"  Entities : {len(document.Entities)}")
        print()
        entity : Entity
        for entity in document.Entities.values():
            print(f"    Entity: {entity.Identifier}")
            print(f"      Generics: {'None' if entity.GenericItems is None else len(entity.GenericItems)}")
            for generic in entity.GenericItems:
                print("        %s: %s" % name_type_str(generic))
            print(f"      Ports: {'None' if entity.PortItems is None else len(entity.PortItems)}")
            for port in entity.PortItems:
                print("        %s: %s" % name_type_str(port))
            print(f"      Port Groups: {'None' if entity.PortGroups is None else len(entity.PortGroups)}")
            for group in entity.PortGroups:
                print(f"        {group.Name}: {group.Count} ports")
                for port in group.PortItems:
                    print("          %s: %s" % name_type_str(port))
            print()

        print(f"  Architectures : {len(document.Architectures)}")
        print()

        print(f"  Configurations : {len(document.Configurations)}")
        print()

        print(f"  Packages : {len(document.Packages)}")
        print()
        package : Package
        for package in document.Packages.values():
            print(f"    Package: {package.Identifier}")
            print()
            print(f"      Components: {'None' if package.Components is None else len(package.Components)}")
            component : Component
            for component in package.Components.values():
                print(f"        Component: {component.Identifier}")
                print(f"          Generics: {'None' if component.GenericItems is None else len(component.GenericItems)}")
                for generic in component.GenericItems:
                    print("          %s: %s" % name_type_str(generic))
                print(f"          Ports: {'None' if component.PortItems is None else len(component.PortItems)}")
                for port in component.PortItems:
                    print("          %s: %s" % name_type_str(port))
                print(f"          Port Groups: {'None' if component.PortGroups is None else len(component.PortGroups)}")
                for group in component.PortGroups:
                    print(f"          {group.Name}: {group.Count} ports")
                    for port in group.PortItems:
                        print("            %s: %s" % name_type_str(port))
                print()
            print()

        print(f"  Package Bodies : {len(document.PackageBodies)}")
        print()

    except VHDLSyntaxError as e:
        print(f"Syntax error in VHDL file: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        if args.verbose:
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
