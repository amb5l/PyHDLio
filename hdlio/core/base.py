"""
Base classes for HDL document object model
"""

from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod


class HDLToken:
    """Represents a single token with position and whitespace information"""

    def __init__(self, token_type: str, value: str, line: int, column: int,
                 preceding_whitespace: str = "", following_whitespace: str = ""):
        self.token_type = token_type
        self.value = value
        self.line = line
        self.column = column
        self.preceding_whitespace = preceding_whitespace
        self.following_whitespace = following_whitespace

    def __str__(self):
        return f"{self.preceding_whitespace}{self.value}{self.following_whitespace}"

    def __repr__(self):
        return f"HDLToken({self.token_type}, '{self.value}', {self.line}:{self.column})"


class HDLNode(ABC):
    """Base class for all HDL AST nodes"""

    def __init__(self):
        self.tokens: List[HDLToken] = []
        self.children: List['HDLNode'] = []
        self.parent: Optional['HDLNode'] = None
        self._source_order: int = 0

    def add_token(self, token: HDLToken):
        """Add a token to this node"""
        self.tokens.append(token)

    def add_child(self, child: 'HDLNode'):
        """Add a child node"""
        child.parent = self
        child._source_order = len(self.children)
        self.children.append(child)

    def get_source_text(self) -> str:
        """Reconstruct the exact source text for this node"""
        if self.tokens and not self.children:
            return "".join(str(token) for token in self.tokens)

        # For nodes with children, combine child source text
        result = ""
        for child in self.children:
            result += child.get_source_text()

        # Add any direct tokens not covered by children
        for token in self.tokens:
            if not any(token in child.tokens for child in self.children):
                result += str(token)

        return result

    @abstractmethod
    def get_node_type(self) -> str:
        """Return the type of this node"""
        pass


class HDLDesignUnit(HDLNode):
    """Base class for design units (entity, module, etc.)"""

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.port_groups: List['HDLPortGroup'] = []

    def add_port_group(self, port_group: 'HDLPortGroup'):
        """Add a port group to this design unit"""
        self.port_groups.append(port_group)

    def get_port_groups(self) -> List['HDLPortGroup']:
        """Get all port groups in source order"""
        return self.port_groups.copy()

    @abstractmethod
    def get_vhdl_type(self) -> str:
        """Return the VHDL/Verilog type (entity, module, etc.)"""
        pass


class HDLPort(HDLNode):
    """Represents a single port declaration"""

    def __init__(self, name: str, port_type: str, direction: str = ""):
        super().__init__()
        self.name = name
        self.port_type = port_type
        self.direction = direction  # in, out, inout, etc.
        self.width: Optional[str] = None
        self.default_value: Optional[str] = None

    def get_node_type(self) -> str:
        return "port"

    def get_name(self) -> str:
        return self.name

    def get_type(self) -> str:
        return self.port_type

    def get_direction(self) -> str:
        return self.direction

    def __str__(self):
        return f"{self.name}: {self.direction} {self.port_type}"


class HDLPortGroup(HDLNode):
    """Represents a group of ports, typically separated by comments or whitespace"""

    def __init__(self, name: str = ""):
        super().__init__()
        self.name = name
        self.ports: List[HDLPort] = []
        self.comment: str = ""

    def add_port(self, port: HDLPort):
        """Add a port to this group"""
        self.ports.append(port)
        self.add_child(port)

    def get_ports(self) -> List[HDLPort]:
        """Get all ports in this group in source order"""
        return self.ports.copy()

    def get_name(self) -> str:
        return self.name

    def get_node_type(self) -> str:
        return "port_group"

    def __str__(self):
        if self.name:
            return f"PortGroup '{self.name}' ({len(self.ports)} ports)"
        else:
            return f"PortGroup ({len(self.ports)} ports)"


class HDLDocument(HDLNode):
    """Root document containing all design units"""

    def __init__(self, filename: str, language: str):
        super().__init__()
        self.filename = filename
        self.language = language
        self.design_units: List[HDLDesignUnit] = []
        self.source_text: str = ""

    def add_design_unit(self, unit: HDLDesignUnit):
        """Add a design unit to the document"""
        self.design_units.append(unit)
        self.add_child(unit)

    def get_design_units(self) -> List[HDLDesignUnit]:
        """Get all design units in source order"""
        return self.design_units.copy()

    def get_node_type(self) -> str:
        return "document"

    def set_source_text(self, text: str):
        """Store the original source text for reference"""
        self.source_text = text
