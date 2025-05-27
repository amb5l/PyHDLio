"""
Main HDLio class providing the user interface for HDL parsing
"""

import os
from typing import List, Optional, Union
from .constants import *
from .base import HDLDocument, HDLDesignUnit
from .parsers.parser_factory import ParserFactory


class HDLio:
    """
    Main HDLio class for parsing HDL files

    Usage:
        # Entity-focused parsing (optimized, default)
        hdl = HDLio("test.vhd", VHDL_2008)
        
        # Comprehensive parsing (handles all VHDL constructs)
        hdl = HDLio("test.vhd", VHDL_2008, comprehensive=True)
        
        design_units = hdl.getDesignUnits()
        for unit in design_units:
            if unit.getVhdlType() == "entity":
                port_groups = unit.getPortGroups()
                for group in port_groups:
                    ports = group.getPorts()
    """

    def __init__(self, filename: str, language: str, comprehensive: bool = False):
        """
        Initialize HDLio with a file and language specification

        Args:
            filename: Path to the HDL file to parse
            language: Language version constant (e.g., VHDL_2008, VERILOG_2001)
            comprehensive: If True, use comprehensive parser that handles all language constructs.
                          If False (default), use optimized parser focused on entity/port parsing.
        """
        if language not in ALL_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}. "
                           f"Supported languages: {', '.join(ALL_LANGUAGES)}")

        self.filename = filename
        self.language = language
        self.comprehensive = comprehensive
        self.document: Optional[HDLDocument] = None
        self._parsed = False

        # Parse the file immediately
        self._parse_file()

    def _parse_file(self):
        """Parse the HDL file using the appropriate parser"""
        if not os.path.exists(self.filename):
            raise FileNotFoundError(f"File not found: {self.filename}")

        # Read the source file
        with open(self.filename, 'r', encoding='utf-8') as f:
            source_text = f.read()

        # Get the appropriate parser
        parser = ParserFactory.get_parser(self.language, self.comprehensive)

        # Parse the file
        self.document = parser.parse(self.filename, source_text)
        self._parsed = True

    def getDesignUnits(self) -> List[HDLDesignUnit]:
        """
        Get all design units from the parsed file

        Returns:
            List of HDLDesignUnit objects in source order
        """
        if not self._parsed or not self.document:
            raise RuntimeError("File has not been parsed successfully")

        return self.document.getDesignUnits()

    def getDocument(self) -> HDLDocument:
        """
        Get the complete document object

        Returns:
            HDLDocument object containing the entire parsed structure
        """
        if not self._parsed or not self.document:
            raise RuntimeError("File has not been parsed successfully")

        return self.document

    def getSourceText(self) -> str:
        """
        Get the original source text

        Returns:
            Original source text as string
        """
        if not self._parsed or not self.document:
            raise RuntimeError("File has not been parsed successfully")

        return self.document.source_text

    def getReconstructedText(self) -> str:
        """
        Reconstruct the source text from the parsed document
        This should match the original source exactly (100% accuracy)

        Returns:
            Reconstructed source text
        """
        if not self._parsed or not self.document:
            raise RuntimeError("File has not been parsed successfully")

        return self.document.get_source_text()

    def getLanguage(self) -> str:
        """Get the language version being used"""
        return self.language

    def getFilename(self) -> str:
        """Get the filename being parsed"""
        return self.filename

    def isComprehensive(self) -> bool:
        """Check if comprehensive parsing mode is enabled"""
        return self.comprehensive

    def getParserInfo(self) -> dict:
        """
        Get information about the parser being used
        
        Returns:
            Dictionary with parser information
        """
        return {
            'filename': self.filename,
            'language': self.language,
            'comprehensive': self.comprehensive,
            'parsed': self._parsed,
            'parser_type': 'comprehensive' if self.comprehensive else 'entity-focused'
        }