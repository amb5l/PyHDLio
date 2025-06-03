from .ast.ast import VHDLModule, Entity, Generic, Port, PortGroup

def report_generics(entity: Entity, indent: int = 2) -> str:
    """Generate formatted report of entity generics.

    Args:
        entity: Entity to report
        indent: Number of spaces for indentation

    Returns:
        Formatted string report of generics
    """
    istr = " " * indent
    output = [f"{istr}Generics:"]
    if entity.generics:
        for generic in entity.generics:
            default = f" = {generic.default_value}" if generic.default_value else ""
            output.append(f"{istr}    - {generic.name}: {generic.type}{default}")
    else:
        output.append(f"{istr}    None")
    return "\n".join(output)

def report_ports_flat(entity: Entity, indent: int = 2) -> str:
    """Generate formatted report of entity ports in flat format.

    Args:
        entity: Entity to report
        indent: Number of spaces for indentation

    Returns:
        Formatted string report of ports
    """
    istr = " " * indent
    output = [f"{istr}Ports (flat):"]
    if entity.ports:
        for port in entity.ports:
            constraint = f" {port.constraint}" if port.constraint else ""
            output.append(f"{istr}    - {port.name}: {port.direction} {port.type}{constraint}")
    else:
        output.append(f"{istr}    None")
    return "\n".join(output)

def report_ports_grouped(entity: Entity, indent: int = 2) -> str:
    """Generate formatted report of entity ports in grouped format.

    Args:
        entity: Entity to report
        indent: Number of spaces for indentation

    Returns:
        Formatted string report of grouped ports
    """
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

def report_entity(entity: Entity, indent: int = 0) -> str:
    """Generate complete formatted report of an entity.

    Args:
        entity: Entity to report
        indent: Number of spaces for indentation

    Returns:
        Formatted string report of the entity
    """
    istr = " " * indent
    output = [f"{istr}Entity: {entity.name}"]
    output.append(report_generics(entity, indent + 2))
    output.append(report_ports_flat(entity, indent + 2))
    output.append(report_ports_grouped(entity, indent + 2))
    return "\n".join(output)

def report_entities(module: VHDLModule) -> str:
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
