"""
SystemVerilog-specific classes
"""

from .verilog import VerilogModule, VerilogPort


class SystemVerilogModule(VerilogModule):
    """SystemVerilog Module design unit (extends Verilog)"""

    def __init__(self, name: str):
        super().__init__(name)
        self.interfaces = []
        self.modports = []

    def get_vhdl_type(self) -> str:
        return "module"

    def get_node_type(self) -> str:
        return "systemverilog_module"

    def add_interface(self, interface):
        """Add an interface"""
        self.interfaces.append(interface)

    def get_interfaces(self):
        """Get all interfaces"""
        return self.interfaces.copy()


class SystemVerilogInterface(VerilogModule):
    """SystemVerilog Interface design unit"""

    def __init__(self, name: str):
        super().__init__(name)
        self.modports = []

    def get_vhdl_type(self) -> str:
        return "interface"

    def get_node_type(self) -> str:
        return "systemverilog_interface"


class SystemVerilogPackage(VerilogModule):
    """SystemVerilog Package design unit"""

    def __init__(self, name: str):
        super().__init__(name)

    def get_vhdl_type(self) -> str:
        return "package"

    def get_node_type(self) -> str:
        return "systemverilog_package"


class SystemVerilogPort(VerilogPort):
    """SystemVerilog-specific port with additional SystemVerilog features"""

    def __init__(self, name: str, port_type: str, direction: str = ""):
        super().__init__(name, port_type, direction)
        self.is_interface = False
        self.interface_type = None
        self.modport = None

    def get_node_type(self) -> str:
        return "systemverilog_port"
