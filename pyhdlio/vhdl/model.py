"""
Enhanced VHDL Model Classes with Integrated Parsing

This module provides the main entry point for VHDL parsing and modeling in PyHDLio.
It directly returns pyVHDLModel Document objects using a streamlined parser.

Examples:
    # Parse directly to pyVHDLModel Document
    from pyhdlio.vhdl.model import Document
    doc = Document.from_file("counter.vhd")
"""

__all__ = [
    "Document",
    "Context",
    "Entity",
    "Architecture",
    "Configuration",
    "Package",
    "PackageBody",
    "Component",
    "PortSignalInterfaceItem",
    "GenericConstantInterfaceItem"
]

from typing import Union, Optional
from pathlib import Path

# Import pyVHDLModel Document as the base
from pyVHDLModel import Document as BaseDocument
from pyVHDLModel import (
    Context,
    Entity,
    Architecture,
    Configuration,
    Package,
    PackageBody,
    Component,
    PortSignalInterfaceItem,
    GenericConstantInterfaceItem
)


class VHDLSyntaxError(Exception):
    """Exception raised for VHDL syntax errors."""
    pass


class Document(BaseDocument):
    """
    Enhanced pyVHDLModel Document with integrated parsing functionality.

    This class extends the base pyVHDLModel Document with convenient class methods
    for parsing VHDL directly from strings or files into pyVHDLModel objects.
    """

    @classmethod
    def FromStr(cls, vhdl_code: str, filename: Optional[str] = None) -> 'Document':
        """
        Parse VHDL code from a string and return a pyVHDLModel Document instance.

        Args:
            vhdl_code: VHDL source code as a string
            filename: Optional filename to associate with the document

        Returns:
            Document instance containing the parsed design units

        Raises:
            VHDLSyntaxError: If parsing fails
        """
        # Import ANTLR classes
        from antlr4 import InputStream, CommonTokenStream
        from antlr4.error.ErrorListener import ErrorListener
        from .grammar.VHDLLexer import VHDLLexer
        from .grammar.VHDLParser import VHDLParser
        from .visitor import VHDLVisitor

        # Custom error listener for VHDL parsing
        class VHDLErrorListener(ErrorListener):
            def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
                raise VHDLSyntaxError(f"Syntax error at line {line}, column {column}: {msg}")

        # Create input stream from string
        input_stream = InputStream(vhdl_code)

        # Set up lexer and parser
        lexer = VHDLLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = VHDLParser(stream)

        # Add custom error handling
        parser.removeErrorListeners()
        parser.addErrorListener(VHDLErrorListener())

        try:
            # Parse the VHDL code using the grammar
            tree = parser.rule_DesignFile()
        except Exception as e:
            raise VHDLSyntaxError(f"Failed to parse VHDL code: {str(e)}")

        # Convert parse tree to pyVHDLModel Document using visitor
        visitor = VHDLVisitor(filename=filename or "parsed.vhd")
        return visitor.visit(tree)

    @classmethod
    def FromFile(cls, file_path: Union[str, Path]) -> 'Document':
        """
        Parse a VHDL file and return a pyVHDLModel Document instance.

        Args:
            file_path: Path to the VHDL file to parse

        Returns:
            Document instance containing the parsed design units

        Raises:
            FileNotFoundError: If the file doesn't exist
            VHDLSyntaxError: If parsing fails
        """
        # Read the file and parse as string
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"VHDL file not found: {file_path}")

        vhdl_code = file_path.read_text(encoding='utf-8')
        return cls.FromStr(vhdl_code, str(file_path))