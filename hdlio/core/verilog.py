"""
Verilog-specific classes
"""

from .base import HDLDesignUnit, HDLPort


class VerilogModule(HDLDesignUnit):
    """Verilog Module design unit"""

    def __init__(self, name: str):
        super().__init__(name)
        self.parameters = []

    def get_vhdl_type(self) -> str:
        return "module"

    def get_node_type(self) -> str:
        return "verilog_module"

    def add_parameter(self, parameter):
        """Add a parameter"""
        self.parameters.append(parameter)

    def get_parameters(self):
        """Get all parameters"""
        return self.parameters.copy()


class VerilogPort(HDLPort):
    """Verilog-specific port"""

    def __init__(self, name: str, port_type: str, direction: str = ""):
        super().__init__(name, port_type, direction)
        self.wire_type = "wire"  # wire, reg, etc.
        self.is_signed = False
        self.range_spec = None  # [7:0], etc.

    def get_node_type(self) -> str:
        return "verilog_port"