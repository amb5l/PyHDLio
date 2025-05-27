"""
VHDL-specific classes
"""

from .base import HDLDesignUnit, HDLPort


class VHDLEntity(HDLDesignUnit):
    """VHDL Entity design unit"""

    def __init__(self, name: str):
        super().__init__(name)
        self.generics = []
        self.architecture_names = []

    def getVhdlType(self) -> str:
        return "entity"

    def get_node_type(self) -> str:
        return "vhdl_entity"

    def add_generic(self, generic):
        """Add a generic parameter"""
        self.generics.append(generic)

    def getGenerics(self):
        """Get all generic parameters"""
        return self.generics.copy()


class VHDLArchitecture(HDLDesignUnit):
    """VHDL Architecture design unit"""

    def __init__(self, name: str, entity_name: str = ""):
        super().__init__(name)
        self.entity_name = entity_name

    def getVhdlType(self) -> str:
        return "architecture"

    def get_node_type(self) -> str:
        return "vhdl_architecture"

    def getEntityName(self) -> str:
        return self.entity_name


class VHDLPackage(HDLDesignUnit):
    """VHDL Package design unit"""

    def __init__(self, name: str):
        super().__init__(name)

    def getVhdlType(self) -> str:
        return "package"

    def get_node_type(self) -> str:
        return "vhdl_package"


class VHDLPackageBody(HDLDesignUnit):
    """VHDL Package Body design unit"""

    def __init__(self, name: str):
        super().__init__(name)

    def getVhdlType(self) -> str:
        return "package_body"

    def get_node_type(self) -> str:
        return "vhdl_package_body"


class VHDLConfiguration(HDLDesignUnit):
    """VHDL Configuration design unit"""

    def __init__(self, name: str):
        super().__init__(name)

    def getVhdlType(self) -> str:
        return "configuration"

    def get_node_type(self) -> str:
        return "vhdl_configuration"


class VHDLPort(HDLPort):
    """VHDL-specific port with additional VHDL features"""

    def __init__(self, name: str, port_type: str, direction: str = ""):
        super().__init__(name, port_type, direction)
        self.is_buffer = False
        self.mode = direction  # in, out, inout, buffer

    def get_node_type(self) -> str:
        return "vhdl_port"