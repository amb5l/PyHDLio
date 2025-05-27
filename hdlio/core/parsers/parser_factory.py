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
    def get_parser(cls, language: str, comprehensive: bool = False) -> BaseHDLParser:
        """
        Get the appropriate parser for the given language

        Args:
            language: Language version constant
            comprehensive: If True, use comprehensive parser that handles all language constructs.
                         If False, use optimized parser focused on entity/port parsing.

        Returns:
            Parser instance for the language
        """
        parser_key = f"{language}_{'comprehensive' if comprehensive else 'working'}"
        
        if parser_key not in cls._parsers:
            cls._parsers[parser_key] = cls._create_parser(language, comprehensive)

        return cls._parsers[parser_key]

    @classmethod
    def _create_parser(cls, language: str, comprehensive: bool = False) -> BaseHDLParser:
        """Create a new parser instance for the given language"""

        if language in VHDL_LANGUAGES:
            # Use the single VHDL parser for all VHDL parsing needs
            # It supports both entity-focused and comprehensive parsing
            from .vhdl_parser import VHDLParser
            return VHDLParser(language)

        elif language in VERILOG_LANGUAGES:
            from .verilog_parser import VerilogParser
            return VerilogParser(language)

        elif language in SYSTEMVERILOG_LANGUAGES:
            from .systemverilog_parser import SystemVerilogParser
            return SystemVerilogParser(language)

        else:
            raise ValueError(f"Unsupported language: {language}")

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