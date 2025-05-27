"""
Base parser class for all HDL parsers
"""

import sys
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

# Add PLY to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate from hdlio/core/parsers to hdlio/submodules/ply/src
ply_path = os.path.join(current_dir, '..', '..', '..', 'hdlio', 'submodules', 'ply', 'src')
ply_path = os.path.normpath(ply_path)
if ply_path not in sys.path:
    sys.path.insert(0, ply_path)

import ply.lex as lex
import ply.yacc as yacc

from ..base import HDLDocument, HDLDesignUnit, HDLPort, HDLPortGroup, HDLToken


class BaseHDLParser(ABC):
    """Base class for all HDL parsers"""

    def __init__(self, language: str):
        self.language = language
        self.tokens = []
        self.lexer = None
        self.parser = None
        self.current_document = None
        self.current_line = 1
        self.current_column = 1
        self._setup_lexer()
        self._setup_parser()

    @abstractmethod
    def _setup_lexer(self):
        """Setup the lexer for this HDL language"""
        pass

    @abstractmethod
    def _setup_parser(self):
        """Setup the parser for this HDL language"""
        pass

    def parse(self, filename: str, source_text: str) -> HDLDocument:
        """
        Parse HDL source text into a document object

        Args:
            filename: Name of the file being parsed
            source_text: The source code to parse

        Returns:
            HDLDocument object representing the parsed structure
        """
        # Create the document
        self.current_document = HDLDocument(filename, self.language)
        self.current_document.set_source_text(source_text)

        # Reset line/column tracking
        self.current_line = 1
        self.current_column = 1

        # Parse the source
        try:
            self.parser.parse(source_text, lexer=self.lexer)
        except Exception as e:
            raise RuntimeError(f"Parse error in {filename}: {str(e)}")

        return self.current_document

    def create_token(self, token_type: str, value: str, line: int = None, column: int = None) -> HDLToken:
        """Create an HDL token with position information"""
        if line is None:
            line = self.current_line
        if column is None:
            column = self.current_column

        return HDLToken(token_type, value, line, column)

    def extract_port_groups(self, ports: List[HDLPort], port_tokens: List[HDLToken]) -> List[HDLPortGroup]:
        """
        Extract port groups based on comments and empty lines

        Args:
            ports: List of port objects
            port_tokens: List of tokens from the port declaration

        Returns:
            List of HDLPortGroup objects
        """
        if not ports:
            return []

        groups = []
        current_group = None
        group_counter = 1

        # Look for comment tokens to group ports
        i = 0
        port_index = 0

        while i < len(port_tokens) and port_index < len(ports):
            token = port_tokens[i]

            # Check for comment that might indicate a new group
            if 'COMMENT' in token.token_type:
                # Start a new group with the comment as the name
                comment_text = token.value.strip('--').strip('//').strip('/*').strip('*/').strip()
                if comment_text:
                    group_name = comment_text
                else:
                    group_name = f"group{group_counter}"
                    group_counter += 1

                current_group = HDLPortGroup(group_name)
                current_group.comment = token.value
                groups.append(current_group)

            # Check for port-related tokens
            elif any(port.name in token.value for port in ports[port_index:]):
                # Find the matching port
                for j, port in enumerate(ports[port_index:], port_index):
                    if port.name in token.value:
                        if current_group is None:
                            current_group = HDLPortGroup(f"group{group_counter}")
                            group_counter += 1
                            groups.append(current_group)

                        current_group.add_port(port)
                        port_index = j + 1
                        break

            i += 1

        # Add any remaining ports to the last group or create a new one
        while port_index < len(ports):
            if current_group is None:
                current_group = HDLPortGroup(f"group{group_counter}")
                groups.append(current_group)

            current_group.add_port(ports[port_index])
            port_index += 1

        # If no groups were created, put all ports in a default group
        if not groups and ports:
            default_group = HDLPortGroup("group1")
            for port in ports:
                default_group.add_port(port)
            groups.append(default_group)

        return groups
