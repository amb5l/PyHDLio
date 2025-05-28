"""
Parser factory for creating appropriate HDL parsers
"""

from ..constants import *
from .base_parser import BaseHDLParser


class ParserFactory:
    """Factory for creating HDL parsers"""

    _parsers = {}
    _comprehensive_mode = False

    @classmethod
    def get_parser(cls, hdl_lrm: HDL_LRM, comprehensive: bool = False) -> BaseHDLParser:
        """
        Get the appropriate parser for the given HDL language version

        Args:
            hdl_lrm: HDL Language Reference Manual version enum
            comprehensive: If True, use comprehensive parser that handles all language constructs.
                         If False, use optimized parser focused on entity/port parsing.

        Returns:
            Parser instance for the language
        """
        parser_key = f"{hdl_lrm.value}_{'comprehensive' if comprehensive else 'working'}"

        if parser_key not in cls._parsers:
            cls._parsers[parser_key] = cls._create_parser(hdl_lrm, comprehensive)

        return cls._parsers[parser_key]

    @classmethod
    def _create_parser(cls, hdl_lrm: HDL_LRM, comprehensive: bool = False) -> BaseHDLParser:
        """Create a new parser instance for the given HDL language version"""

        if hdl_lrm in VHDL_VERSIONS:
            # Use the single VHDL parser for all VHDL parsing needs
            # It supports both entity-focused and comprehensive parsing
            from .vhdl_parser import VHDLParser
            return VHDLParser(hdl_lrm)

        elif hdl_lrm in VERILOG_VERSIONS:
            from .verilog_parser import VerilogParser
            return VerilogParser(hdl_lrm)

        elif hdl_lrm in SYSTEMVERILOG_VERSIONS:
            from .systemverilog_parser import SystemVerilogParser
            return SystemVerilogParser(hdl_lrm)

        else:
            raise ValueError(f"Unsupported HDL LRM: {hdl_lrm}")

    @classmethod
    def set_comprehensive_mode(cls, enabled: bool):
        """
        Set the default comprehensive parsing mode

        Args:
            enabled: If True, use comprehensive parsing by default
        """
        cls._comprehensive_mode = enabled

    @classmethod
    def get_comprehensive_mode(cls) -> bool:
        """Get the current comprehensive parsing mode"""
        return cls._comprehensive_mode

    @classmethod
    def clear_cache(cls):
        """Clear the parser cache"""
        cls._parsers.clear()
