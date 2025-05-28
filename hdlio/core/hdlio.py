"""
Main HDLio class providing the user interface for HDL parsing
"""

import os
from typing import List, Optional, Dict
from .constants import HDL_LRM
from .base import HDLLibrary, HDLDesignUnit
from .parsers.parser_factory import ParserFactory


class HDLio:
    """
    Main HDLio class for parsing HDL files and managing libraries

    Usage:
        hdlio = HDLio()
        path = "./example.vhd"
        library = "work"
        lrm = HDL_LRM.VHDL_2008
        source = hdlio.load(path, library, lrm)
        # source is the fully expanded path to the loaded source, or None if loading fails
    """

    def __init__(self):
        """Initialize HDLio with empty library collection"""
        self.libraries: Dict[str, HDLLibrary] = {}

    def load(
        self,
        path: str,
        library: str = "work",
        hdl_lrm: HDL_LRM = HDL_LRM.VHDL_2008
    ) -> Optional[str]:
        """
        Load an HDL source file into the specified library

        Args:
            path: Path to the HDL file to load
            library: Library name to load into (default: "work")
            hdl_lrm: HDL Language Reference Manual version to use for parsing

        Returns:
            Fully expanded path to the loaded source file, or None if loading fails
        """
        try:
            print(f"DEBUG HDLio.load: Starting load of {path} with {hdl_lrm}")
            
            # Expand the path to absolute
            abs_path = os.path.abspath(path)
            print(f"DEBUG HDLio.load: Absolute path: {abs_path}")

            if not os.path.exists(abs_path):
                print(f"DEBUG HDLio.load: File does not exist: {abs_path}")
                return None

            # Read the source file
            with open(abs_path, 'r', encoding='utf-8') as f:
                source_text = f.read()
            print(f"DEBUG HDLio.load: Read {len(source_text)} characters from file")

            # Get the appropriate parser - ParserFactory will handle validation
            print(f"DEBUG HDLio.load: Getting parser for {hdl_lrm}")
            parser = ParserFactory.get_parser(hdl_lrm, comprehensive=True)
            print(f"DEBUG HDLio.load: Got parser: {type(parser).__name__}")

            # Parse the file into a library
            print(f"DEBUG HDLio.load: Starting parse...")
            parsed_library = parser.parse(abs_path, source_text, library)
            print(f"DEBUG HDLio.load: Parse completed. Library: {parsed_library}")

            if parsed_library:
                print(f"DEBUG HDLio.load: Design units in parsed library: {len(parsed_library.get_design_units())}")
            else:
                print(f"DEBUG HDLio.load: No library returned from parser")

            # Check if parsing actually produced any design units
            if not parsed_library or len(parsed_library.get_design_units()) == 0:
                # No design units found - likely a parse error or empty file
                print(f"DEBUG HDLio.load: No design units found, returning None")
                return None

            # Add or merge with existing library
            if library in self.libraries:
                # Merge design units into existing library
                existing_library = self.libraries[library]
                for unit in parsed_library.get_design_units():
                    existing_library.add_design_unit(unit)
                print(f"DEBUG HDLio.load: Merged into existing library '{library}'")
            else:
                # Create new library
                self.libraries[library] = parsed_library
                print(f"DEBUG HDLio.load: Created new library '{library}'")

            print(f"DEBUG HDLio.load: Success, returning {abs_path}")
            return abs_path

        except Exception as e:
            # Log error if needed, but return None to indicate failure
            print(f"DEBUG HDLio.load: Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_libraries(self) -> Dict[str, HDLLibrary]:
        """Get all loaded libraries"""
        return self.libraries.copy()

    def get_library(self, name: str) -> Optional[HDLLibrary]:
        """Get a specific library by name"""
        return self.libraries.get(name)

    def get_design_units(self, library: str = "work") -> List[HDLDesignUnit]:
        """
        Get all design units from the specified library

        Args:
            library: Library name (default: "work")

        Returns:
            List of HDLDesignUnit objects in source order
        """
        if library not in self.libraries:
            return []

        return self.libraries[library].get_design_units()

    def clear_library(self, library: str):
        """Clear all design units from the specified library"""
        if library in self.libraries:
            del self.libraries[library]

    def clear_all_libraries(self):
        """Clear all libraries"""
        self.libraries.clear()
