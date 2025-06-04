from typing import overload, Union
from .ast import VHDLAST, Entity, Generic, Port, PortGroup

# pyVHDLModel imports (required)
from pyVHDLModel.DesignUnit import Entity as PyVHDLModelEntity
from pyVHDLModel.Interface import GenericConstantInterfaceItem, PortSignalInterfaceItem, PortGroup as PyVHDLModelPortGroup

# Type aliases for cleaner code
EntityType = Union[Entity, 'PyVHDLModelEntity']


@overload
def report_generics(entity: Entity, indent: int = 2) -> str: ...

@overload
def report_generics(entity: 'PyVHDLModelEntity', indent: int = 2) -> str: ...

def report_generics(entity: EntityType, indent: int = 2) -> str:
    """Generate formatted report of entity generics.

    Args:
        entity: Entity to report (PyHDLio AST or pyVHDLModel)
        indent: Number of spaces for indentation

    Returns:
        Formatted string report of generics
    """
    if isinstance(entity, PyVHDLModelEntity):
        return _report_pyvhdlmodel_generics(entity, indent)
    else:
        return _report_ast_generics(entity, indent)


def _report_ast_generics(entity: Entity, indent: int = 2) -> str:
    """Generate formatted report of PyHDLio AST entity generics."""
    istr = " " * indent
    output = [f"{istr}Generics:"]
    if entity.generics:
        for generic in entity.generics:
            default = f" = {generic.default_value}" if generic.default_value else ""
            output.append(f"{istr}    - {generic.name}: {generic.type}{default}")
    else:
        output.append(f"{istr}    None")
    return "\n".join(output)


def _report_pyvhdlmodel_generics(entity: 'PyVHDLModelEntity', indent: int = 2) -> str:
    """Generate formatted report of pyVHDLModel entity generics."""
    istr = " " * indent
    output = [f"{istr}Generics:"]
    if entity.GenericItems:
        for generic in entity.GenericItems:
            name = generic.Identifiers[0] if generic.Identifiers else "unknown"
            # Try to get our stored type string, fallback to str(Subtype)
            # Check for None instead of truthiness since unresolved symbols return False
            if generic.Subtype is not None and hasattr(generic.Subtype, '_typeString'):
                type_str = generic.Subtype._typeString
            else:
                type_str = str(generic.Subtype) if generic.Subtype else "unknown"
            default = f" = {generic.DefaultExpression}" if generic.DefaultExpression else ""
            output.append(f"{istr}    - {name}: {type_str}{default}")
    else:
        output.append(f"{istr}    None")
    return "\n".join(output)


@overload
def report_ports_flat(entity: Entity, indent: int = 2) -> str: ...

@overload
def report_ports_flat(entity: 'PyVHDLModelEntity', indent: int = 2) -> str: ...

def report_ports_flat(entity: EntityType, indent: int = 2) -> str:
    """Generate formatted report of entity ports in flat format.

    Args:
        entity: Entity to report (PyHDLio AST or pyVHDLModel)
        indent: Number of spaces for indentation

    Returns:
        Formatted string report of ports
    """
    if isinstance(entity, PyVHDLModelEntity):
        return _report_pyvhdlmodel_ports_flat(entity, indent)
    else:
        return _report_ast_ports_flat(entity, indent)


def _report_ast_ports_flat(entity: Entity, indent: int = 2) -> str:
    """Generate formatted report of PyHDLio AST entity ports in flat format."""
    istr = " " * indent
    output = [f"{istr}Ports (flat):"]
    if entity.ports:
        for port in entity.ports:
            constraint = f" {port.constraint}" if port.constraint else ""
            output.append(f"{istr}    - {port.name}: {port.direction} {port.type}{constraint}")
    else:
        output.append(f"{istr}    None")
    return "\n".join(output)


def _report_pyvhdlmodel_ports_flat(entity: 'PyVHDLModelEntity', indent: int = 2) -> str:
    """Generate formatted report of pyVHDLModel entity ports in flat format."""
    istr = " " * indent
    output = [f"{istr}Ports (flat):"]
    if entity.PortItems:
        for port in entity.PortItems:
            name = port.Identifiers[0] if port.Identifiers else "unknown"
            direction = port.Mode.name.lower() if port.Mode else "unknown"
            # Try to get our stored type string, fallback to str(Subtype)
            # Check for None instead of truthiness since unresolved symbols return False
            if port.Subtype is not None and hasattr(port.Subtype, '_typeString'):
                type_str = port.Subtype._typeString
            else:
                type_str = str(port.Subtype) if port.Subtype else "unknown"
            output.append(f"{istr}    - {name}: {direction} {type_str}")
    else:
        output.append(f"{istr}    None")
    return "\n".join(output)


@overload
def report_ports_grouped(entity: Entity, indent: int = 2) -> str: ...

@overload
def report_ports_grouped(entity: 'PyVHDLModelEntity', indent: int = 2) -> str: ...

def report_ports_grouped(entity: EntityType, indent: int = 2) -> str:
    """Generate formatted report of entity ports in grouped format.

    Args:
        entity: Entity to report (PyHDLio AST or pyVHDLModel)
        indent: Number of spaces for indentation

    Returns:
        Formatted string report of grouped ports
    """
    if isinstance(entity, PyVHDLModelEntity):
        return _report_pyvhdlmodel_ports_grouped(entity, indent)
    else:
        return _report_ast_ports_grouped(entity, indent)


def _report_ast_ports_grouped(entity: Entity, indent: int = 2) -> str:
    """Generate formatted report of PyHDLio AST entity ports in grouped format."""
    istr = " " * indent
    output = [f"{istr}Ports (grouped):"]
    if entity.port_groups:
        for i, group in enumerate(entity.port_groups, 1):
            output.append(f"{istr}  Group {i}:")
            for port in group.ports:
                constraint = f" {port.constraint}" if port.constraint else ""
                output.append(f"{istr}    - {port.name}: {port.direction} {port.type}{constraint}")
    else:
        output.append(f"{istr}    None")
    return "\n".join(output)


def _report_pyvhdlmodel_ports_grouped(entity: 'PyVHDLModelEntity', indent: int = 2) -> str:
    """Generate formatted report of pyVHDLModel entity ports in grouped format."""
    istr = " " * indent
    output = [f"{istr}Ports (grouped):"]
    if entity.PortGroups:
        for i, group in enumerate(entity.PortGroups, 1):
            output.append(f"{istr}  Group {i}:")
            for port in group.PortItems:
                name = port.Identifiers[0] if port.Identifiers else "unknown"
                direction = port.Mode.name.lower() if port.Mode else "unknown"
                # Try to get our stored type string, fallback to str(Subtype)
                # Check for None instead of truthiness since unresolved symbols return False
                if port.Subtype is not None and hasattr(port.Subtype, '_typeString'):
                    type_str = port.Subtype._typeString
                else:
                    type_str = str(port.Subtype) if port.Subtype else "unknown"
                output.append(f"{istr}    - {name}: {direction} {type_str}")
    else:
        output.append(f"{istr}    None")
    return "\n".join(output)


@overload
def report_entity(entity: Entity, indent: int = 0) -> str: ...

@overload
def report_entity(entity: 'PyVHDLModelEntity', indent: int = 0) -> str: ...

def report_entity(entity: EntityType, indent: int = 0) -> str:
    """Generate complete formatted report of an entity.

    Args:
        entity: Entity to report (PyHDLio AST or pyVHDLModel)
        indent: Number of spaces for indentation

    Returns:
        Formatted string report of the entity
    """
    istr = " " * indent

    # Get entity name
    if isinstance(entity, PyVHDLModelEntity):
        entity_name = entity.Identifier
    else:
        entity_name = entity.name

    output = [f"{istr}Entity: {entity_name}"]
    output.append(report_generics(entity, indent + 2))
    output.append(report_ports_flat(entity, indent + 2))
    output.append(report_ports_grouped(entity, indent + 2))
    return "\n".join(output)


def report_entities(module: VHDLAST) -> str:
    """Generate formatted report of entities.

    Args:
        module: Parsed VHDL module

    Returns:
        Formatted string report
    """
    if not module.entities:
        return "No entities found."
    output = []
    for entity in module.entities:
        output.append(report_entity(entity))
    return "\n".join(output)


# Additional utility functions for pyVHDLModel
def report_pyvhdlmodel_entities(entities: list) -> str:
    """Generate formatted report of pyVHDLModel entities.

    Args:
        entities: List of pyVHDLModel Entity objects

    Returns:
        Formatted string report
    """
    if not entities:
        return "No entities found."
    output = []
    for entity in entities:
        output.append(report_entity(entity))
    return "\n".join(output)
