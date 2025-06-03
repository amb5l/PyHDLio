from antlr4 import *
from antlr4.error.ErrorListener import ErrorListener
from hdlio.grammar.vhdlLexer import vhdlLexer
from hdlio.grammar.vhdlParser import vhdlParser

class VHDLSyntaxError(Exception):
    """Exception raised for VHDL syntax errors."""
    pass

class VHDLErrorListener(ErrorListener):
    """Custom error listener for VHDL parsing."""
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise VHDLSyntaxError(f"Syntax error at line {line}, column {column}: {msg}")

def parse_vhdl(file_path, mode='tree'):
    """Parse a VHDL file and return parse tree or AST.

    Args:
        file_path (str): Path to the VHDL file
        mode (str): 'tree' for string representation, 'ast' for structured AST

    Returns:
        str | VHDLModule: Parse tree string or VHDLModule AST

    Raises:
        FileNotFoundError: If file doesn't exist
        VHDLSyntaxError: If parsing fails
    """
    try:
        input_stream = FileStream(file_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"VHDL file not found: {file_path}")

    lexer = vhdlLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = vhdlParser(stream)
    
    # Add custom error handling
    parser.removeErrorListeners()
    parser.addErrorListener(VHDLErrorListener())

    try:
        tree = parser.design_file()
    except Exception as e:
        raise VHDLSyntaxError(f"Failed to parse {file_path}: {str(e)}")

    if mode == 'ast':
        # Import here to handle both module and direct script execution
        try:
            from .visitor import VHDLVisitor
            from .ast.ast import VHDLModule
        except ImportError:
            # Handle direct script execution
            from visitor import VHDLVisitor
            from ast.ast import VHDLModule
        
        visitor = VHDLVisitor()
        return visitor.visit(tree)
    
    return tree.toStringTree(recog=parser)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python parse_vhdl.py <vhdl_file>")
        sys.exit(1)
    
    try:
        result = parse_vhdl(sys.argv[1], mode='ast')
        print(f"Parsed module: {result}")
    except (FileNotFoundError, VHDLSyntaxError) as e:
        print(f"Error: {e}")
        sys.exit(1)
