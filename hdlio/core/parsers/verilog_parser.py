"""
Verilog Parser implementation using PLY
(Comprehensive implementation with proper PLY structure)
"""

import sys
import os
from typing import List, Dict, Any, Optional

# Add PLY to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
ply_path = os.path.join(current_dir, '..', '..', '..', 'hdlio', 'submodules', 'ply', 'src')
ply_path = os.path.normpath(ply_path)
if ply_path not in sys.path:
    sys.path.insert(0, ply_path)

import ply.lex as lex
import ply.yacc as yacc

from .base_parser import BaseHDLParser
from ..verilog import VerilogModule, VerilogPort
from ..base import HDLDocument, HDLToken, HDLPortGroup

# Global variables for the parser
current_document = None
current_tokens = []
current_modules = []

# Verilog Token definitions
tokens = (
    'IDENTIFIER',
    'NUMBER',
    'STRING_LITERAL',
    'COMMENT_LINE',
    'COMMENT_BLOCK',
    'SEMICOLON',
    'COLON',
    'COMMA',
    'DOT',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'LBRACE',
    'RBRACE',
    'ASSIGN',
    'MULTIPLY',
    'PLUS',
    'MINUS',
    'DIVIDE',
    'MODULO',
    'EQUAL',
    'NOT_EQUAL',
    'LESS_THAN',
    'LESS_EQUAL',
    'GREATER_THAN',
    'GREATER_EQUAL',
    'LOGICAL_AND',
    'LOGICAL_OR',
    'LOGICAL_NOT',
    'BITWISE_AND',
    'BITWISE_OR',
    'BITWISE_XOR',
    'BITWISE_NOT',
    'SHIFT_LEFT',
    'SHIFT_RIGHT',
    'NON_BLOCKING_ASSIGN',
    'BLOCKING_ASSIGN',
    'AT',
    'QUESTION',
    'CONCAT',

    # Verilog Keywords
    'MODULE',
    'ENDMODULE',
    'INPUT',
    'OUTPUT',
    'INOUT',
    'WIRE',
    'REG',
    'PARAMETER',
    'LOCALPARAM',
    'BEGIN',
    'END',
    'IF',
    'ELSE',
    'CASE',
    'ENDCASE',
    'DEFAULT',
    'FOR',
    'WHILE',
    'ALWAYS',
    'INITIAL',
    'POSEDGE',
    'NEGEDGE',
    'OR',
    'AND',
    'CLOCK',
    'RESET',
    'LOGIC',
    'BIT',
    'ASSIGN_KW'
)

# Verilog reserved words
reserved = {
    'module': 'MODULE',
    'endmodule': 'ENDMODULE',
    'input': 'INPUT',
    'output': 'OUTPUT',
    'inout': 'INOUT',
    'wire': 'WIRE',
    'reg': 'REG',
    'parameter': 'PARAMETER',
    'localparam': 'LOCALPARAM',
    'begin': 'BEGIN',
    'end': 'END',
    'if': 'IF',
    'else': 'ELSE',
    'case': 'CASE',
    'endcase': 'ENDCASE',
    'default': 'DEFAULT',
    'for': 'FOR',
    'while': 'WHILE',
    'always': 'ALWAYS',
    'initial': 'INITIAL',
    'posedge': 'POSEDGE',
    'negedge': 'NEGEDGE',
    'or': 'OR',
    'and': 'AND',
    # Note: clk, clock, rst, reset are treated as identifiers, not keywords
    'logic': 'LOGIC',
    'bit': 'BIT',
    'assign': 'ASSIGN_KW'
}

# Token rules
t_SEMICOLON = r';'
t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_QUESTION = r'\?'
t_AT = r'@'

# Operators (order matters for multi-character operators)
t_SHIFT_LEFT = r'<<'
t_SHIFT_RIGHT = r'>>'
t_LOGICAL_AND = r'&&'
t_LOGICAL_OR = r'\|\|'
t_EQUAL = r'=='
t_NOT_EQUAL = r'!='
t_NON_BLOCKING_ASSIGN = r'<='
t_GREATER_EQUAL = r'>='
t_ASSIGN = r'='
t_LESS_THAN = r'<'
t_GREATER_THAN = r'>'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_BITWISE_AND = r'&'
t_BITWISE_OR = r'\|'
t_BITWISE_XOR = r'\^'
t_BITWISE_NOT = r'~'
t_LOGICAL_NOT = r'!'
t_CONCAT = r'\{'

# Ignored characters
t_ignore = ' \t'

def t_COMMENT_BLOCK(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')
    global current_tokens
    current_tokens.append(
        HDLToken('COMMENT_BLOCK', t.value, t.lineno, find_column(t))
    )
    return t

def t_COMMENT_LINE(t):
    r'//.*'
    global current_tokens
    current_tokens.append(
        HDLToken('COMMENT_LINE', t.value, t.lineno, find_column(t))
    )
    return t

def t_STRING_LITERAL(t):
    r'"([^"\\]|\\.)*"'
    return t

def t_NUMBER(t):
    r'\d+\'[bBoOdDhH][0-9a-fA-F_xXzZ]+|\d+(\.\d+)?([eE][+-]?\d+)?'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFIER')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

def find_column(token):
    line_start = token.lexer.lexdata.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

# Grammar rules
def p_source_text(p):
    '''source_text : description_list'''
    pass

def p_description_list(p):
    '''description_list : description
                       | description_list description'''
    pass

def p_description(p):
    '''description : module_declaration
                  | comment_or_empty'''
    pass

def p_module_declaration(p):
    '''module_declaration : MODULE IDENTIFIER LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE
                         | MODULE IDENTIFIER SEMICOLON module_items ENDMODULE'''
    global current_document, current_tokens
    
    module_name = p[2]
    module = VerilogModule(module_name)
    
    # Extract ports if they exist
    if len(p) == 9:  # Module with ports
        if p[4]:  # port_list exists
            port_groups = extract_port_groups(p[4], current_tokens)
            for group in port_groups:
                module.add_port_group(group)
    
    if current_document:
        current_document.add_design_unit(module)

def p_port_list(p):
    '''port_list : 
                | port_list_items'''
    if len(p) == 2:
        p[0] = p[1] if p[1] else []
    else:
        p[0] = []

def p_port_list_items(p):
    '''port_list_items : port
                      | port_list_items COMMA port'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        if p[1] is None:
            p[1] = []
        p[0] = p[1] + [p[3]]

def p_port(p):
    '''port : IDENTIFIER
           | INPUT IDENTIFIER
           | OUTPUT IDENTIFIER
           | INOUT IDENTIFIER
           | INPUT WIRE IDENTIFIER
           | OUTPUT WIRE IDENTIFIER
           | INOUT WIRE IDENTIFIER
           | INPUT REG IDENTIFIER
           | OUTPUT REG IDENTIFIER
           | INPUT LBRACKET NUMBER COLON NUMBER RBRACKET IDENTIFIER
           | OUTPUT LBRACKET NUMBER COLON NUMBER RBRACKET IDENTIFIER
           | INOUT LBRACKET NUMBER COLON NUMBER RBRACKET IDENTIFIER
           | INPUT WIRE LBRACKET NUMBER COLON NUMBER RBRACKET IDENTIFIER
           | OUTPUT WIRE LBRACKET NUMBER COLON NUMBER RBRACKET IDENTIFIER
           | INOUT WIRE LBRACKET NUMBER COLON NUMBER RBRACKET IDENTIFIER
           | INPUT REG LBRACKET NUMBER COLON NUMBER RBRACKET IDENTIFIER
           | OUTPUT REG LBRACKET NUMBER COLON NUMBER RBRACKET IDENTIFIER'''
    
    # Extract port information
    if len(p) == 2:  # Just identifier
        p[0] = {'name': p[1], 'direction': None, 'type': None, 'range': None}
    elif len(p) == 3:  # direction + identifier
        p[0] = {'name': p[2], 'direction': p[1], 'type': None, 'range': None}
    elif len(p) == 4:  # direction + type + identifier
        p[0] = {'name': p[3], 'direction': p[1], 'type': p[2], 'range': None}
    elif len(p) == 7:  # direction + [range] + identifier
        p[0] = {'name': p[6], 'direction': p[1], 'type': None, 'range': f"[{p[3]}:{p[5]}]"}
    elif len(p) == 8:  # direction + type + [range] + identifier
        p[0] = {'name': p[7], 'direction': p[1], 'type': p[2], 'range': f"[{p[4]}:{p[6]}]"}

def p_module_items(p):
    '''module_items : 
                   | module_items module_item'''
    pass

def p_module_item(p):
    '''module_item : port_declaration
                  | parameter_declaration
                  | localparam_declaration
                  | wire_declaration
                  | reg_declaration
                  | always_block
                  | initial_block
                  | assign_statement
                  | comment_or_empty'''
    pass

def p_comment_or_empty(p):
    '''comment_or_empty : COMMENT_LINE
                       | COMMENT_BLOCK
                       | empty'''
    pass

def p_empty(p):
    '''empty :'''
    pass

def p_port_declaration(p):
    '''port_declaration : INPUT IDENTIFIER SEMICOLON
                       | OUTPUT IDENTIFIER SEMICOLON
                       | INOUT IDENTIFIER SEMICOLON
                       | INPUT WIRE IDENTIFIER SEMICOLON
                       | OUTPUT WIRE IDENTIFIER SEMICOLON
                       | INOUT WIRE IDENTIFIER SEMICOLON
                       | INPUT REG IDENTIFIER SEMICOLON
                       | OUTPUT REG IDENTIFIER SEMICOLON
                       | INPUT range IDENTIFIER SEMICOLON
                       | OUTPUT range IDENTIFIER SEMICOLON
                       | INOUT range IDENTIFIER SEMICOLON
                       | INPUT WIRE range IDENTIFIER SEMICOLON
                       | OUTPUT WIRE range IDENTIFIER SEMICOLON
                       | INOUT WIRE range IDENTIFIER SEMICOLON
                       | INPUT REG range IDENTIFIER SEMICOLON
                       | OUTPUT REG range IDENTIFIER SEMICOLON'''
    pass

def p_range(p):
    '''range : LBRACKET NUMBER COLON NUMBER RBRACKET
            | LBRACKET IDENTIFIER COLON IDENTIFIER RBRACKET
            | LBRACKET expression COLON expression RBRACKET'''
    pass

def p_parameter_declaration(p):
    '''parameter_declaration : PARAMETER IDENTIFIER ASSIGN expression SEMICOLON'''
    pass

def p_localparam_declaration(p):
    '''localparam_declaration : LOCALPARAM IDENTIFIER ASSIGN expression SEMICOLON'''
    pass

def p_wire_declaration(p):
    '''wire_declaration : WIRE IDENTIFIER SEMICOLON
                       | WIRE range IDENTIFIER SEMICOLON'''
    pass

def p_reg_declaration(p):
    '''reg_declaration : REG IDENTIFIER SEMICOLON
                      | REG range IDENTIFIER SEMICOLON'''
    pass

def p_always_block(p):
    '''always_block : ALWAYS AT LPAREN sensitivity_list RPAREN statement'''
    pass

def p_initial_block(p):
    '''initial_block : INITIAL statement'''
    pass

def p_assign_statement(p):
    '''assign_statement : ASSIGN_KW IDENTIFIER ASSIGN expression SEMICOLON'''
    pass

def p_sensitivity_list(p):
    '''sensitivity_list : sensitivity_items'''
    pass

def p_sensitivity_items(p):
    '''sensitivity_items : sensitivity_item
                        | sensitivity_items OR sensitivity_item'''
    pass

def p_sensitivity_item(p):
    '''sensitivity_item : IDENTIFIER
                       | POSEDGE IDENTIFIER
                       | NEGEDGE IDENTIFIER
                       | POSEDGE IDENTIFIER OR NEGEDGE IDENTIFIER
                       | NEGEDGE IDENTIFIER OR POSEDGE IDENTIFIER'''
    pass

def p_statement(p):
    '''statement : assignment_statement
                | BEGIN statement_list END
                | IF LPAREN expression RPAREN statement
                | IF LPAREN expression RPAREN statement ELSE statement
                | CASE LPAREN expression RPAREN case_items ENDCASE
                | SEMICOLON'''
    pass

def p_assignment_statement(p):
    '''assignment_statement : IDENTIFIER ASSIGN expression SEMICOLON
                           | IDENTIFIER NON_BLOCKING_ASSIGN expression SEMICOLON
                           | IDENTIFIER LBRACKET expression RBRACKET ASSIGN expression SEMICOLON'''
    pass

def p_case_items(p):
    '''case_items : case_item
                 | case_items case_item'''
    pass

def p_case_item(p):
    '''case_item : expression COLON statement
                | DEFAULT COLON statement'''
    pass

def p_statement_list(p):
    '''statement_list : statement
                     | statement_list statement'''
    pass

def p_expression(p):
    '''expression : IDENTIFIER
                 | NUMBER
                 | STRING_LITERAL
                 | IDENTIFIER LBRACKET expression RBRACKET
                 | expression PLUS expression
                 | expression MINUS expression
                 | expression MULTIPLY expression
                 | expression DIVIDE expression
                 | expression MODULO expression
                 | expression EQUAL expression
                 | expression NOT_EQUAL expression
                 | expression LESS_THAN expression
                 | expression LESS_EQUAL expression
                 | expression GREATER_THAN expression
                 | expression GREATER_EQUAL expression
                 | expression LOGICAL_AND expression
                 | expression LOGICAL_OR expression
                 | expression BITWISE_AND expression
                 | expression BITWISE_OR expression
                 | expression BITWISE_XOR expression
                 | LOGICAL_NOT expression
                 | BITWISE_NOT expression
                 | LPAREN expression RPAREN
                 | concatenation
                 | expression_list'''
    pass

def p_expression_list(p):
    '''expression_list : expression
                      | expression_list COMMA expression'''
    pass

def p_concatenation(p):
    '''concatenation : LBRACE expression_list RBRACE'''
    pass

def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} ('{p.value}') at line {p.lineno}")
    else:
        print("Syntax error at EOF")

def parse_verilog(filename: str, source_text: str, language: str) -> HDLDocument:
    """Parse Verilog source text and return HDLDocument"""
    global current_document, current_tokens, current_modules
    
    # Initialize global state
    current_document = HDLDocument(filename, language)
    current_tokens = []
    current_modules = []
    
    try:
        # Build lexer and parser
        lexer = lex.lex()
        parser = yacc.yacc()
        
        # Parse the source text
        result = parser.parse(source_text, lexer=lexer)
        
        # Set tokens in document
        current_document.tokens = current_tokens
        
        return current_document
        
    except Exception as e:
        print(f"Error parsing Verilog: {e}")
        return current_document

def extract_port_groups(port_list, tokens):
    """Extract port groups from parsed port list"""
    if not port_list:
        return []
    
    groups = {}
    
    for port_info in port_list:
        if isinstance(port_info, dict):
            direction = port_info.get('direction', 'input')
            port_name = port_info.get('name', 'unknown')
            port_type = port_info.get('type', 'wire')
            port_range = port_info.get('range', '')
            
            # Create port
            port = VerilogPort(port_name, direction, port_type)
            if port_range:
                port.range = port_range
            
            # Group by direction
            if direction not in groups:
                groups[direction] = HDLPortGroup(direction)
            groups[direction].add_port(port)
    
    return list(groups.values())


class VerilogParser(BaseHDLParser):
    """Verilog Parser using PLY"""

    def __init__(self, language: str):
        super().__init__(language)

    def _setup_lexer(self):
        """Setup Verilog lexer"""
        self.lexer = lex.lex()

    def _setup_parser(self):
        """Setup Verilog parser"""
        self.parser = yacc.yacc()

    def parse(self, filename: str, source_text: str) -> HDLDocument:
        """Parse Verilog source and return HDLDocument"""
        return parse_verilog(filename, source_text, self.language)