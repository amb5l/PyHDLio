"""
Enhanced VHDL Model Classes with Integrated Parsing

This module provides the main entry point for VHDL parsing and modeling in PyHDLio.
It re-exports VHDLAST from ast.py and includes enhanced Document class with convenient parsing methods.

Users should import from this module for the complete API, or from ast module for AST-only use.

Examples:
    # Recommended: Complete API from model module (re-exports VHDLAST from ast.py)
    from pyhdlio.vhdl.model import Document, VHDLAST

    # Parse directly to pyVHDLModel Document
    doc = Document.from_file("counter.vhd")

    # Parse directly to PyHDLio AST
    ast = VHDLAST.from_file("counter.vhd")

    # Convert existing AST to Document
    doc = Document.from_ast(ast)

    # Alternative: Direct AST import (VHDLAST actually lives here)
    from pyhdlio.vhdl.ast import VHDLAST
    ast = VHDLAST.from_file("counter.vhd")
"""

from typing import Union, Optional, List
from pathlib import Path

# Import AST classes and exceptions
from .ast import VHDLAST, VHDLSyntaxError

# Import pyVHDLModel classes (required)
from pyVHDLModel import Document as BaseDocument
from pyVHDLModel.DesignUnit import Entity
from pyVHDLModel.Interface import (
    GenericConstantInterfaceItem,
    PortSignalInterfaceItem,
    PortGroup
)
from pyVHDLModel.Base import Mode
from pyVHDLModel.Expression import IntegerLiteral, EnumerationLiteral, StringLiteral
from pyVHDLModel.Symbol import SimpleSubtypeSymbol
from pyVHDLModel.Name import SimpleName

class Document(BaseDocument):
    """
    Enhanced pyVHDLModel Document with integrated parsing functionality.

    This class extends the base pyVHDLModel Document with convenient class methods
    for parsing VHDL directly from strings or files into pyVHDLModel objects.
    """

    @classmethod
    def from_string(cls, vhdl_code: str, filename: Optional[str] = None) -> 'Document':
        """
        Parse VHDL code from a string and return a pyVHDLModel Document instance.

        Args:
            vhdl_code: VHDL source code as a string
            filename: Optional filename to associate with the document

        Returns:
            Document instance containing the parsed design units

        Raises:
            VHDLSyntaxError: If parsing fails
        """
        # First parse to PyHDLio AST
        ast = VHDLAST.from_string(vhdl_code)

        # Set filename if provided
        if filename:
            ast.filename = filename

        # Convert to pyVHDLModel Document
        return cls.from_ast(ast)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'Document':
        """
        Parse a VHDL file and return a pyVHDLModel Document instance.

        Args:
            file_path: Path to the VHDL file to parse

        Returns:
            Document instance containing the parsed design units

        Raises:
            FileNotFoundError: If the file doesn't exist
            VHDLSyntaxError: If parsing fails
        """
        # Read file and parse as string
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"VHDL file not found: {file_path}")

        vhdl_code = file_path.read_text(encoding='utf-8')
        return cls.from_string(vhdl_code, filename=str(file_path))

    @classmethod
    def from_ast(cls, ast: VHDLAST) -> 'Document':
        """
        Convert a PyHDLio VHDLAST to a pyVHDLModel Document instance.

        Args:
            ast: PyHDLio VHDLAST instance to convert

        Returns:
            Document instance containing the converted design units
        """
        # Create a document - use the AST's filename if available, otherwise a default
        doc_path = Path(ast.filename) if hasattr(ast, 'filename') and ast.filename else Path("converted.vhd")
        document = cls(doc_path)

        # Convert each entity
        for entity in ast.entities:
            pyvhdl_entity = cls._convert_entity(entity)
            document._AddEntity(pyvhdl_entity)

        return document

    @staticmethod
    def _convert_entity(pyhdlio_entity) -> Entity:
        """Convert a PyHDLio Entity to a pyVHDLModel Entity."""
        # Convert generics
        generic_items = []
        for generic in pyhdlio_entity.generics:
            generic_item = Document._convert_generic(generic)
            if generic_item:
                generic_items.append(generic_item)

        # Convert ports
        port_items = []
        for port in pyhdlio_entity.ports:
            port_item = Document._convert_port(port)
            if port_item:
                port_items.append(port_item)

        # Create pyVHDLModel Entity
        entity = Entity(
            identifier=pyhdlio_entity.name,
            genericItems=generic_items,
            portItems=port_items
        )

        # Convert and populate port groups
        port_groups = Document._convert_port_groups(pyhdlio_entity.port_groups, port_items)
        entity._portGroups.extend(port_groups)

        return entity

    @staticmethod
    def _convert_generic(pyhdlio_generic) -> Optional[GenericConstantInterfaceItem]:
        """Convert a PyHDLio Generic to a pyVHDLModel GenericConstantInterfaceItem."""
        try:
            # Create a more informative subtype symbol
            type_name = SimpleName(pyhdlio_generic.type)
            type_symbol = SimpleSubtypeSymbol(type_name)

            # Handle default value - convert to appropriate Expression
            default_expr = None
            if pyhdlio_generic.default_value:
                default_expr = Document._convert_default_value(pyhdlio_generic.default_value)

            generic_item = GenericConstantInterfaceItem(
                identifiers=[pyhdlio_generic.name],
                mode=Mode.In,  # Generics are always input mode
                subtype=type_symbol,
                defaultExpression=default_expr
            )

            return generic_item
        except Exception as e:
            print(f"Warning: Failed to convert generic '{pyhdlio_generic.name}': {e}")
            return None

    @staticmethod
    def _convert_default_value(value_str: str):
        """Convert a default value string to an appropriate Expression."""
        if not value_str:
            return None

        value_str = value_str.strip()

        # Try to parse as integer
        try:
            int_val = int(value_str)
            return IntegerLiteral(int_val)
        except ValueError:
            pass

        # If it's quoted, treat as string literal
        if value_str.startswith('"') and value_str.endswith('"'):
            return StringLiteral(value_str[1:-1])  # Remove quotes

        # Otherwise treat as enumeration literal (identifier)
        return EnumerationLiteral(value_str)

    @staticmethod
    def _convert_port(pyhdlio_port) -> Optional[PortSignalInterfaceItem]:
        """Convert a PyHDLio Port to a pyVHDLModel PortSignalInterfaceItem."""
        try:
            # Map direction to Mode
            mode_mapping = {
                'in': Mode.In,
                'out': Mode.Out,
                'inout': Mode.InOut,
                'buffer': Mode.Buffer,
                'linkage': Mode.Linkage
            }
            mode = mode_mapping.get(pyhdlio_port.direction.lower(), Mode.In)

            # Create type symbol - combine type and constraint if present
            type_str = pyhdlio_port.type
            if pyhdlio_port.constraint:
                type_str = f"{type_str}{pyhdlio_port.constraint}"

            type_name = SimpleName(type_str)
            type_symbol = SimpleSubtypeSymbol(type_name)

            port_item = PortSignalInterfaceItem(
                identifiers=[pyhdlio_port.name],
                mode=mode,
                subtype=type_symbol
            )

            return port_item
        except Exception as e:
            print(f"Warning: Failed to convert port '{pyhdlio_port.name}': {e}")
            return None

    @staticmethod
    def _convert_port_groups(pyhdlio_port_groups: List, pyvhdlmodel_ports: List) -> List[PortGroup]:
        """Convert PyHDLio PortGroups to pyVHDLModel PortGroups."""
        port_groups = []

        # Create a mapping from port names to pyVHDLModel port objects
        port_name_to_obj = {}
        for port_obj in pyvhdlmodel_ports:
            # PortSignalInterfaceItem has identifiers list
            if hasattr(port_obj, '_identifiers') and port_obj._identifiers:
                port_name_to_obj[port_obj._identifiers[0]] = port_obj

        # Convert each PyHDLio port group
        for pyhdlio_group in pyhdlio_port_groups:
            group_ports = []

            for pyhdlio_port in pyhdlio_group.ports:
                pyvhdlmodel_port = port_name_to_obj.get(pyhdlio_port.name)
                if pyvhdlmodel_port:
                    group_ports.append(pyvhdlmodel_port)
                else:
                    print(f"Warning: Port '{pyhdlio_port.name}' not found in converted ports")

            if group_ports:
                try:
                    port_group = PortGroup(ports=group_ports, name=pyhdlio_group.name)
                    port_groups.append(port_group)
                except Exception as e:
                    print(f"Warning: Failed to create PortGroup: {e}")

        return port_groups

# Re-export commonly used classes for convenience
__all__ = [
    'VHDLAST',
    'Document',
    'VHDLSyntaxError',
    'Entity',
    'GenericConstantInterfaceItem',
    'PortSignalInterfaceItem',
    'PortGroup',
    'Mode',
]