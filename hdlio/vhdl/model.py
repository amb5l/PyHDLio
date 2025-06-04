"""
Enhanced VHDL Model Classes with Integrated Parsing

This module provides the main entry point for VHDL parsing and modeling in PyHDLio.
It re-exports VHDLAST from ast.py and includes enhanced Document class with convenient parsing methods.

Users should import from this module for the complete API, or from ast module for AST-only use.

Examples:
    # Recommended: Complete API from model module (re-exports VHDLAST from ast.py)
    from hdlio.vhdl.model import Document, VHDLAST

    # Parse directly to pyVHDLModel Document
    doc = Document.from_file("counter.vhd")

    # Parse directly to PyHDLio AST
    ast = VHDLAST.from_file("counter.vhd")

    # Convert existing AST to Document
    doc = Document.from_ast(ast)

    # Alternative: Direct AST import (VHDLAST actually lives here)
    from hdlio.vhdl.ast import VHDLAST
    ast = VHDLAST.from_file("counter.vhd")
"""

from typing import Union, Optional
from pathlib import Path

# Import parsing functionality
from .parse_vhdl import VHDLSyntaxError
from .converters.pyvhdlmodel_converter import convert_to_pyvhdlmodel

# Import AST classes
from .ast import VHDLAST

# Import pyVHDLModel classes if available
try:
    from pyVHDLModel import Document as BaseDocument
    from pyVHDLModel.DesignUnit import Entity
    from pyVHDLModel.Interface import (
        GenericConstantInterfaceItem,
        PortSignalInterfaceItem,
        PortGroup
    )
    from pyVHDLModel.Base import Mode
    PYVHDLMODEL_AVAILABLE = True
except ImportError:
    BaseDocument = None
    Entity = None
    GenericConstantInterfaceItem = None
    PortSignalInterfaceItem = None
    PortGroup = None
    Mode = None
    PYVHDLMODEL_AVAILABLE = False


if PYVHDLMODEL_AVAILABLE:
    class Document(BaseDocument):
        """
        Enhanced pyVHDLModel Document with integrated parsing functionality.

        This class extends the base pyVHDLModel Document with convenient class methods
        for parsing VHDL directly from strings or files into pyVHDLModel objects.
        """

        @classmethod
        def from_string(cls, vhdl_code: str, filename: Optional[str] = None) -> 'Document':
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
            # First parse to PyHDLio AST
            ast = VHDLAST.from_string(vhdl_code)

            # Set filename if provided
            if filename:
                ast.filename = filename

            # Convert to pyVHDLModel Document
            return convert_to_pyvhdlmodel(ast)

        @classmethod
        def from_file(cls, file_path: Union[str, Path]) -> 'Document':
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
            # Read file and parse as string
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"VHDL file not found: {file_path}")

            vhdl_code = file_path.read_text(encoding='utf-8')
            return cls.from_string(vhdl_code, filename=str(file_path))

        @classmethod
        def from_ast(cls, ast: VHDLAST) -> 'Document':
            """
            Convert a PyHDLio VHDLAST to a pyVHDLModel Document instance.

            Args:
                ast: PyHDLio VHDLAST instance to convert

            Returns:
                Document instance containing the converted design units
            """
            return convert_to_pyvhdlmodel(ast)
else:
    # Create a placeholder class when pyVHDLModel is not available
    class Document:
        """Placeholder Document class - pyVHDLModel not available."""

        @classmethod
        def from_string(cls, vhdl_code: str, filename: Optional[str] = None):
            raise ImportError("pyVHDLModel is not available. Install it to use Document class.")

        @classmethod
        def from_file(cls, file_path: Union[str, Path]):
            raise ImportError("pyVHDLModel is not available. Install it to use Document class.")

        @classmethod
        def from_ast(cls, ast: VHDLAST):
            raise ImportError("pyVHDLModel is not available. Install it to use Document class.")


# Re-export commonly used classes for convenience
__all__ = [
    'VHDLAST',
    'Document',
    'VHDLSyntaxError',
]

# Conditionally add pyVHDLModel exports
if PYVHDLMODEL_AVAILABLE:
    __all__.extend([
        'Entity',
        'GenericConstantInterfaceItem',
        'PortSignalInterfaceItem',
        'PortGroup',
        'Mode',
    ])


# Export the parsing error for user convenience
from .parse_vhdl import VHDLSyntaxError