"""
AST module for VHDL constructs.

This module defines the Abstract Syntax Tree (AST) classes for representing
parsed VHDL constructs in PyHDLio.
"""

from dataclasses import dataclass
from typing import List, Optional, Union
from pathlib import Path


class VHDLSyntaxError(Exception):
    """Exception raised for VHDL syntax errors."""
    pass


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
    name: Optional[str] = None

@dataclass
class Entity:
    """Represents a VHDL entity with dual port access."""
    name: str
    generics: List[Generic]
    ports: List[Port]  # Flat list of all ports
    port_groups: List[PortGroup]  # Grouped ports

@dataclass
class VHDLAST:
    """
    Enhanced VHDLAST with integrated parsing functionality.

    This class represents a parsed VHDL file with multiple design units
    and provides convenient class methods for parsing VHDL directly
    from strings or files.
    """
    entities: List[Entity]

    @classmethod
    def from_string(cls, vhdl_code: str) -> 'VHDLAST':
        """
        Parse VHDL code from a string and return a VHDLAST instance.

        Args:
            vhdl_code: VHDL source code as a string

        Returns:
            VHDLAST instance containing the parsed entities

        Raises:
            VHDLSyntaxError: If parsing fails
        """
        # Import ANTLR classes
        from antlr4 import InputStream, CommonTokenStream
        from antlr4.error.ErrorListener import ErrorListener
        from hdlio.grammar.vhdlLexer import vhdlLexer
        from hdlio.grammar.vhdlParser import vhdlParser
        from .visitor import VHDLVisitor

        # Custom error listener for VHDL parsing
        class VHDLErrorListener(ErrorListener):
            def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
                raise VHDLSyntaxError(f"Syntax error at line {line}, column {column}: {msg}")

        # Create input stream from string
        input_stream = InputStream(vhdl_code)

        # Set up lexer and parser
        lexer = vhdlLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = vhdlParser(stream)

        # Add custom error handling
        parser.removeErrorListeners()
        parser.addErrorListener(VHDLErrorListener())

        try:
            # Parse the VHDL code
            tree = parser.design_file()
        except Exception as e:
            raise VHDLSyntaxError(f"Failed to parse VHDL code: {str(e)}")

        # Convert parse tree to AST using visitor
        visitor = VHDLVisitor()
        return visitor.visit(tree)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'VHDLAST':
        """
        Parse a VHDL file and return a VHDLAST instance.

        Args:
            file_path: Path to the VHDL file to parse

        Returns:
            VHDLAST instance containing the parsed entities

        Raises:
            FileNotFoundError: If the file doesn't exist
            VHDLSyntaxError: If parsing fails
        """
        # Read the file and parse as string
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"VHDL file not found: {file_path}")

        vhdl_code = file_path.read_text(encoding='utf-8')
        ast = cls.from_string(vhdl_code)

        # Set the filename attribute for reference
        ast.filename = str(file_path)
        return ast