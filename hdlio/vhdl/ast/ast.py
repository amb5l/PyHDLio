from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Generic:
    """Represents a VHDL generic parameter."""
    name: str
    type: str
    default_value: Optional[str] = None

@dataclass
class Port:
    """Represents a VHDL port."""
    name: str
    direction: str  # "in", "out", "inout"
    type: str
    constraint: Optional[str] = None  # e.g., "(3 downto 0)"

@dataclass
class PortGroup:
    """Represents a group of ports separated by empty/comment lines."""
    ports: List[Port]

@dataclass
class Entity:
    """Represents a VHDL entity with dual port access."""
    name: str
    generics: List[Generic]
    ports: List[Port]  # Flat list of all ports
    port_groups: List[PortGroup]  # Grouped ports

@dataclass
class VHDLModule:
    """Represents a complete VHDL file with multiple entities."""
    entities: List[Entity] 