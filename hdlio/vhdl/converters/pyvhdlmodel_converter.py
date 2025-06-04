"""
PyVHDLModel Converter

Converts PyHDLio AST objects to pyVHDLModel objects with port grouping support.
"""

from typing import List, Optional
import re

# PyHDLio imports
from ..ast import Entity as PyHDLioEntity, Port as PyHDLioPort, Generic as PyHDLioGeneric, PortGroup as PyHDLioPortGroup

# pyVHDLModel imports
from pyVHDLModel.DesignUnit import Entity as PyVHDLModelEntity
from pyVHDLModel import Document
from pyVHDLModel.Interface import (
    PortGroup,
    PortSignalInterfaceItem,
    GenericConstantInterfaceItem,
    PortInterfaceItemMixin
)
from pyVHDLModel.Base import Mode
from pyVHDLModel.Symbol import SimpleSubtypeSymbol
from pyVHDLModel.Name import SimpleName
from pyVHDLModel.Expression import IntegerLiteral, StringLiteral, EnumerationLiteral
from pathlib import Path


class PyVHDLModelConverter:
    """
    Converts PyHDLio AST objects to pyVHDLModel objects.

    This converter maintains the port grouping information from PyHDLio's
    source-proximity-based grouping and translates it to pyVHDLModel's
    PortGroup objects.
    """

    def __init__(self):
        """Initialize the converter with mode mappings."""
        self._mode_mapping = {
            'in': Mode.In,
            'out': Mode.Out,
            'inout': Mode.InOut,
        }

    def convert_entity(self, pyhdlio_entity: PyHDLioEntity) -> PyVHDLModelEntity:
        """
        Convert a PyHDLio Entity to a pyVHDLModel Entity.

        :param pyhdlio_entity: PyHDLio Entity object
        :returns: pyVHDLModel Entity object with PortGroups populated
        """
        # Convert generics
        generic_items = []
        for generic in pyhdlio_entity.generics:
            generic_item = self._convert_generic(generic)
            if generic_item:
                generic_items.append(generic_item)

        # Convert ports
        port_items = []
        for port in pyhdlio_entity.ports:
            port_item = self._convert_port(port)
            if port_item:
                port_items.append(port_item)

        # Create pyVHDLModel Entity
        entity = PyVHDLModelEntity(
            identifier=pyhdlio_entity.name,
            genericItems=generic_items,
            portItems=port_items
        )

        # Convert and populate port groups
        port_groups = self._convert_port_groups(pyhdlio_entity.port_groups, port_items)
        entity._portGroups.extend(port_groups)

        return entity

    def _convert_generic(self, pyhdlio_generic: PyHDLioGeneric) -> Optional[GenericConstantInterfaceItem]:
        """Convert a PyHDLio Generic to a pyVHDLModel GenericConstantInterfaceItem."""
        try:
            # Create a more informative subtype symbol
            # Since we don't have full symbol table resolution, preserve the type name
            type_name = SimpleName(pyhdlio_generic.type)
            type_symbol = SimpleSubtypeSymbol(type_name)

            # Handle default value - convert to appropriate Expression
            default_expr = None
            if pyhdlio_generic.default_value:
                default_expr = self._convert_default_value(pyhdlio_generic.default_value)

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

    def _convert_default_value(self, value_str: str):
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

    def _convert_port(self, pyhdlio_port: PyHDLioPort) -> Optional[PortSignalInterfaceItem]:
        """Convert a PyHDLio Port to a pyVHDLModel PortSignalInterfaceItem."""
        try:
            # Map direction to Mode
            mode = self._mode_mapping.get(pyhdlio_port.direction.lower(), Mode.In)

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

    def _convert_port_groups(
        self,
        pyhdlio_port_groups: List[PyHDLioPortGroup],
        pyvhdlmodel_ports: List[PortInterfaceItemMixin]
    ) -> List[PortGroup]:
        """
        Convert PyHDLio PortGroups to pyVHDLModel PortGroups.

        :param pyhdlio_port_groups: List of PyHDLio PortGroup objects
        :param pyvhdlmodel_ports: List of converted pyVHDLModel port items
        :returns: List of pyVHDLModel PortGroup objects
        """
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

    def convert_module(self, pyhdlio_module) -> List[PyVHDLModelEntity]:
        """
        Convert a PyHDLio VHDLModule (containing multiple entities) to a list of pyVHDLModel entities.

        :param pyhdlio_module: PyHDLio VHDLModule object
        :returns: List of pyVHDLModel Entity objects
        """
        entities = []

        for pyhdlio_entity in pyhdlio_module.entities:
            try:
                entity = self.convert_entity(pyhdlio_entity)
                entities.append(entity)
            except Exception as e:
                print(f"Error converting entity '{pyhdlio_entity.name}': {e}")
                import traceback
                traceback.print_exc()

        return entities


def convert_to_pyvhdlmodel(ast: 'VHDLAST') -> Document:
    """
    Convert PyHDLio VHDLAST to pyVHDLModel Document.
    
    Args:
        ast: The PyHDLio AST to convert
        
    Returns:
        pyVHDLModel Document containing the converted design units
    """
    # Create a document - use the AST's filename if available, otherwise a default
    doc_path = Path(ast.filename) if hasattr(ast, 'filename') and ast.filename else Path("converted.vhd")
    document = Document(doc_path)
    
    # Create converter instance
    converter = PyVHDLModelConverter()
    
    # Convert each entity
    for entity in ast.entities:
        pyvhdl_entity = converter.convert_entity(entity)
        document._AddEntity(pyvhdl_entity)
    
    return document


def convert_ast_to_pyvhdlmodel(pyhdlio_ast):
    """
    Convert PyHDLio AST objects to pyVHDLModel equivalents.
    
    :param pyhdlio_ast: PyHDLio AST object (Entity or VHDLAST)
    :return: Corresponding pyVHDLModel object(s)
    """
    converter = PyVHDLModelConverter()

    if isinstance(pyhdlio_ast, PyHDLioEntity):
        # Single entity
        return [converter.convert_entity(pyhdlio_ast)]
    else:
        # VHDLAST with multiple entities
        return converter.convert_module(pyhdlio_ast)