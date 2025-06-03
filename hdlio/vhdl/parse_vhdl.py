from antlr4 import *
from hdlio.grammar.vhdlLexer import vhdlLexer
from hdlio.grammar.vhdlParser import vhdlParser

def parse_vhdl(file_path):
    """Parse a VHDL file and return its parse tree as a string."""
    input_stream = FileStream(file_path)
    lexer = vhdlLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = vhdlParser(stream)
    tree = parser.design_file()  # Adjust to your grammar’s entry rule
    return tree.toStringTree(recog=parser)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python parse_vhdl.py <vhdl_file>")
        sys.exit(1)
    print(parse_vhdl(sys.argv[1]))
