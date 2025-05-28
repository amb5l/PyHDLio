"""
Verilog Parser using PLY (Python Lex-Yacc)
Enhanced to handle Verilog-2005 constructs including packages, imports, and macros
"""

import sys
import os
import re
from typing import Dict, List, Optional, Any

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

# Global variables for parser state
current_document = None
current_tokens = []
current_modules = []
parser_instance = None

# Verilog keywords
keywords = {
    'module': 'MODULE',
    'endmodule': 'ENDMODULE',
    'input': 'INPUT',
    'output': 'OUTPUT',
    'inout': 'INOUT',
    'wire': 'WIRE',
    'reg': 'REG',
    'integer': 'INTEGER',
    'real': 'REAL',
    'time': 'TIME',
    'parameter': 'PARAMETER',
    'localparam': 'LOCALPARAM',
    'always': 'ALWAYS',
    'initial': 'INITIAL',
    'begin': 'BEGIN',
    'end': 'END',
    'if': 'IF',
    'else': 'ELSE',
    'case': 'CASE',
    'casex': 'CASEX',
    'casez': 'CASEZ',
    'endcase': 'ENDCASE',
    'default': 'DEFAULT',
    'for': 'FOR',
    'while': 'WHILE',
    'repeat': 'REPEAT',
    'forever': 'FOREVER',
    'fork': 'FORK',
    'join': 'JOIN',
    'task': 'TASK',
    'endtask': 'ENDTASK',
    'function': 'FUNCTION',
    'endfunction': 'ENDFUNCTION',
    'assign': 'ASSIGN',
    'deassign': 'DEASSIGN',
    'force': 'FORCE',
    'release': 'RELEASE',
    'disable': 'DISABLE',
    'wait': 'WAIT',
    'posedge': 'POSEDGE',
    'negedge': 'NEGEDGE',
    'or': 'OR',
    'and': 'AND',
    'nand': 'NAND',
    'nor': 'NOR',
    'xor': 'XOR',
    'xnor': 'XNOR',
    'not': 'NOT',
    'buf': 'BUF',
    'bufif0': 'BUFIF0',
    'bufif1': 'BUFIF1',
    'notif0': 'NOTIF0',
    'notif1': 'NOTIF1',
    'nmos': 'NMOS',
    'pmos': 'PMOS',
    'cmos': 'CMOS',
    'rnmos': 'RNMOS',
    'rpmos': 'RPMOS',
    'rcmos': 'RCMOS',
    'rtran': 'RTRAN',
    'rtranif0': 'RTRANIF0',
    'rtranif1': 'RTRANIF1',
    'tran': 'TRAN',
    'tranif0': 'TRANIF0',
    'tranif1': 'TRANIF1',
    'pullup': 'PULLUP',
    'pulldown': 'PULLDOWN',
    'supply0': 'SUPPLY0',
    'supply1': 'SUPPLY1',
    'tri': 'TRI',
    'tri0': 'TRI0',
    'tri1': 'TRI1',
    'triand': 'TRIAND',
    'trior': 'TRIOR',
    'trireg': 'TRIREG',
    'wand': 'WAND',
    'wor': 'WOR',
    'generate': 'GENERATE',
    'endgenerate': 'ENDGENERATE',
    'genvar': 'GENVAR',
    'package': 'PACKAGE',
    'endpackage': 'ENDPACKAGE',
    'import': 'IMPORT',
    'automatic': 'AUTOMATIC',
}

# Token list
tokens = [
    'IDENTIFIER', 'NUMBER', 'STRING_LITERAL',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
    'SEMICOLON', 'COMMA', 'DOT', 'COLON', 'COLON_COLON',
    'ASSIGN', 'NON_BLOCKING_ASSIGN',
    'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MODULO',
    'LOGICAL_AND', 'LOGICAL_OR', 'LOGICAL_NOT',
    'BITWISE_AND', 'BITWISE_OR', 'BITWISE_XOR', 'BITWISE_NOT', 'BITWISE_NAND', 'BITWISE_NOR', 'BITWISE_XNOR',
    'SHIFT_LEFT', 'SHIFT_RIGHT',
    'LT', 'LE', 'GT', 'GE', 'EQ', 'NE', 'CASE_EQ', 'CASE_NE',
    'QUESTION', 'HASH',
    'AT', 'DOLLAR',
    'COMMENT_BLOCK', 'COMMENT_LINE',
    'SYSTEM_TASK', 'SYSTEM_FUNCTION',
    'BACKTICK', 'INCLUDE', 'DEFINE',
] + list(keywords.values())

# Token rules
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_COMMA = r','
t_DOT = r'\.'
t_COLON = r':'
t_COLON_COLON = r'::'
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_MODULO = r'%'
t_LOGICAL_AND = r'&&'
t_LOGICAL_OR = r'\|\|'
t_LOGICAL_NOT = r'!'
t_BITWISE_AND = r'&'
t_BITWISE_OR = r'\|'
t_BITWISE_XOR = r'\^'
t_BITWISE_NOT = r'~'
t_BITWISE_NAND = r'~&'
t_BITWISE_NOR = r'~\|'
t_BITWISE_XNOR = r'~\^'
t_SHIFT_LEFT = r'<<'
t_SHIFT_RIGHT = r'>>'
t_LT = r'<'
t_LE = r'<='
t_GT = r'>'
t_GE = r'>='
t_EQ = r'=='
t_NE = r'!='
t_CASE_EQ = r'==='
t_CASE_NE = r'!=='
t_QUESTION = r'\?'
t_HASH = r'\#'
t_AT = r'@'
t_DOLLAR = r'\$'
t_BACKTICK = r'`'

# Ignored characters (spaces and tabs)
t_ignore = ' \t'

def t_ASSIGN(t):
    r'='
    return t

def t_NON_BLOCKING_ASSIGN(t):
    r'<='
    return t

def t_BACKTICK_DEFINE(t):
    r'`define\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*(.*)'
    global current_tokens, parser_instance
    match = re.match(r'`define\s+([a-zA-Z_][a-zA-Z_0-9]*)\s*(.*)', t.value)
    if match and parser_instance:
        macro_name = match.group(1)
        macro_value = match.group(2).strip()
        parser_instance.macros[macro_name] = macro_value
    current_tokens.append(HDLToken('DEFINE', t.value, t.lineno, find_column(t)))
    return None

def t_BACKTICK_INCLUDE(t):
    r'`include\s+"[^"]*"'
    global current_tokens
    print(f"Warning: Ignoring `include directive: {t.value} at line {t.lineno}")
    current_tokens.append(HDLToken('INCLUDE', t.value, t.lineno, find_column(t)))
    return None

def t_BACKTICK_IDENTIFIER(t):
    r'`[a-zA-Z_][a-zA-Z_0-9]*'
    global parser_instance
    macro_name = t.value[1:]  # Remove backtick
    if parser_instance and macro_name in parser_instance.macros:
        t.value = parser_instance.macros[macro_name]
        t.type = 'NUMBER' if t.value.isdigit() else 'IDENTIFIER'
    else:
        t.type = 'IDENTIFIER'
    return t

def t_SYSTEM_TASK(t):
    r'\$[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_SYSTEM_FUNCTION(t):
    r'\$[a-zA-Z_][a-zA-Z_0-9]*'
    return t

def t_COMMENT_BLOCK(t):
    r'/\*(.|\n)*?\*/'
    global current_tokens
    current_tokens.append(HDLToken('COMMENT_BLOCK', t.value, t.lineno, find_column(t)))
    t.lexer.lineno += t.value.count('\n')
    return None

def t_COMMENT_LINE(t):
    r'//.*'
    global current_tokens
    current_tokens.append(HDLToken('COMMENT_LINE', t.value, t.lineno, find_column(t)))
    return None

def t_STRING_LITERAL(t):
    r'"([^"\\]|\\.)*"'
    return t

def t_NUMBER(t):
    r"(\d+)?'[bBoOdDhH][0-9a-fA-F_xXzZ]+|\d+\.\d+|\d+"
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = keywords.get(t.value, 'IDENTIFIER')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

def find_column(token):
    """Find column position of token"""
    line_start = token.lexer.lexdata.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

# Grammar rules
def p_source_text(p):
    '''source_text : description_list'''
    p[0] = p[1]

def p_description_list(p):
    '''description_list : description
                       | description_list description'''
    pass

def p_description(p):
    '''description : module_declaration
                  | package_declaration
                  | comment_or_empty'''
    pass

def p_module_declaration(p):
    '''module_declaration : MODULE IDENTIFIER parameter_port_list LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE
                         | MODULE IDENTIFIER LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE
                         | MODULE IDENTIFIER SEMICOLON module_items ENDMODULE
                         | MODULE IDENTIFIER import_list parameter_port_list LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE
                         | MODULE IDENTIFIER import_list LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE
                         | MODULE IDENTIFIER import_list SEMICOLON module_items ENDMODULE'''
    global current_document, current_tokens, parser_instance
    module_name = p[2]
    module = VerilogModule(module_name)

    # Handle import list if present
    import_offset = 0
    if len(p) >= 6 and isinstance(p[3], list):  # Has import list
        import_offset = 1
        if parser_instance:
            parser_instance.process_imports_for_module(p[3], module)

    # Handle port list
    port_list_index = 4 + import_offset if len(p) > 6 + import_offset else None
    if port_list_index and port_list_index < len(p) and p[port_list_index]:
        port_list = p[port_list_index]
        if port_list:
            port_groups = extract_port_groups(port_list, current_tokens)
            for group in port_groups:
                module.add_port_group(group)

    if current_document:
        current_document.add_design_unit(module)

def p_parameter_port_list(p):
    '''parameter_port_list : HASH LPAREN parameter_list RPAREN
                          | empty'''
    if len(p) == 5:
        p[0] = p[3]
    else:
        p[0] = None

def p_parameter_list(p):
    '''parameter_list : parameter_assignment
                     | parameter_list COMMA parameter_assignment'''
    pass

def p_port_list(p):
    '''port_list : port_list_items
                | empty'''
    if p[1]:
        p[0] = p[1]
    else:
        p[0] = []

def p_port_list_items(p):
    '''port_list_items : port
                      | port_list_items COMMA port'''
    if len(p) == 2:
        p[0] = [p[1]] if p[1] else []
    else:
        p[0] = p[1] + ([p[3]] if p[3] else [])

def p_port(p):
    '''port : IDENTIFIER
           | DOT IDENTIFIER LPAREN IDENTIFIER RPAREN
           | DOT IDENTIFIER LPAREN RPAREN
           | INPUT range IDENTIFIER
           | OUTPUT range IDENTIFIER
           | INOUT range IDENTIFIER
           | INPUT IDENTIFIER
           | OUTPUT IDENTIFIER
           | INOUT IDENTIFIER
           | INPUT WIRE range IDENTIFIER
           | OUTPUT WIRE range IDENTIFIER
           | INOUT WIRE range IDENTIFIER
           | INPUT WIRE IDENTIFIER
           | OUTPUT WIRE IDENTIFIER
           | INOUT WIRE IDENTIFIER
           | INPUT REG range IDENTIFIER
           | OUTPUT REG range IDENTIFIER
           | INOUT REG range IDENTIFIER
           | INPUT REG IDENTIFIER
           | OUTPUT REG IDENTIFIER
           | INOUT REG IDENTIFIER'''
    if len(p) == 2:
        p[0] = {'name': p[1], 'direction': 'input', 'type': 'wire'}
    elif len(p) == 4:
        if p[1] in ['input', 'output', 'inout']:
            p[0] = {'name': p[3], 'direction': p[1], 'type': 'wire'}
        else:
            p[0] = {'name': p[3], 'direction': p[1], 'type': p[2]}
    elif len(p) == 5:
        if p[2] in ['wire', 'reg']:
            p[0] = {'name': p[4], 'direction': p[1], 'type': p[2]}
        else:
            p[0] = {'name': p[4], 'direction': p[1], 'type': 'wire', 'range': p[2]}
    elif len(p) == 6:
        if p[1] == '.':
            p[0] = {'name': p[4], 'connection': p[2]}
        else:
            p[0] = {'name': p[5], 'direction': p[1], 'type': p[2], 'range': p[3]}
    else:
        p[0] = {'name': p[2], 'connection': None}

def p_net_type(p):
    '''net_type : WIRE
               | TRI
               | SUPPLY0
               | SUPPLY1
               | WAND
               | WOR'''
    p[0] = p[1]

def p_module_items(p):
    '''module_items : module_item
                   | module_items module_item'''
    pass

def p_module_item(p):
    '''module_item : port_declaration
                  | net_declaration
                  | reg_declaration
                  | integer_declaration
                  | real_declaration
                  | time_declaration
                  | parameter_declaration
                  | localparam_declaration
                  | always_block
                  | initial_block
                  | assign_statement
                  | module_instantiation
                  | generate_block
                  | function_declaration
                  | task_declaration
                  | genvar_declaration
                  | comment_or_empty'''
    pass

def p_comment_or_empty(p):
    '''comment_or_empty : COMMENT_BLOCK
                       | COMMENT_LINE
                       | empty'''
    pass

def p_empty(p):
    '''empty :'''
    pass

def p_port_declaration(p):
    '''port_declaration : INPUT range identifier_list SEMICOLON
                       | OUTPUT range identifier_list SEMICOLON
                       | INOUT range identifier_list SEMICOLON
                       | INPUT identifier_list SEMICOLON
                       | OUTPUT identifier_list SEMICOLON
                       | INOUT identifier_list SEMICOLON'''
    pass

def p_net_declaration(p):
    '''net_declaration : net_type range identifier_list SEMICOLON
                      | net_type identifier_list SEMICOLON'''
    pass

def p_reg_declaration(p):
    '''reg_declaration : REG range identifier_list SEMICOLON
                      | REG identifier_list SEMICOLON
                      | REG range IDENTIFIER range SEMICOLON
                      | REG IDENTIFIER range SEMICOLON'''
    pass

def p_integer_declaration(p):
    '''integer_declaration : INTEGER identifier_list SEMICOLON'''
    pass

def p_real_declaration(p):
    '''real_declaration : REAL identifier_list SEMICOLON'''
    pass

def p_time_declaration(p):
    '''time_declaration : TIME identifier_list SEMICOLON'''
    pass

def p_identifier_list(p):
    '''identifier_list : IDENTIFIER
                      | identifier_list COMMA IDENTIFIER
                      | IDENTIFIER range
                      | identifier_list COMMA IDENTIFIER range'''
    pass

def p_range(p):
    '''range : LBRACKET expression COLON expression RBRACKET
            | LBRACKET expression RBRACKET
            | empty'''
    if len(p) == 6:
        p[0] = f"[{p[2]}:{p[4]}]"
    elif len(p) == 4:
        p[0] = f"[{p[2]}]"
    else:
        p[0] = ""

def p_parameter_declaration(p):
    '''parameter_declaration : PARAMETER parameter_assignments SEMICOLON
                            | PARAMETER range parameter_assignments SEMICOLON'''
    pass

def p_localparam_declaration(p):
    '''localparam_declaration : LOCALPARAM parameter_assignments SEMICOLON
                             | LOCALPARAM range parameter_assignments SEMICOLON'''
    pass

def p_parameter_assignments(p):
    '''parameter_assignments : parameter_assignment
                            | parameter_assignments COMMA parameter_assignment'''
    pass

def p_parameter_assignment(p):
    '''parameter_assignment : IDENTIFIER ASSIGN expression'''
    pass

def p_always_block(p):
    '''always_block : ALWAYS delay_or_event_control statement
                   | ALWAYS statement'''
    pass

def p_initial_block(p):
    '''initial_block : INITIAL statement'''
    pass

def p_event_expression(p):
    '''event_expression : POSEDGE IDENTIFIER
                       | NEGEDGE IDENTIFIER
                       | IDENTIFIER
                       | event_expression OR event_expression'''
    pass

def p_assign_statement(p):
    '''assign_statement : ASSIGN assignment_list SEMICOLON'''
    pass

def p_assignment_list(p):
    '''assignment_list : assignment
                      | assignment_list COMMA assignment'''
    pass

def p_assignment(p):
    '''assignment : lvalue ASSIGN expression'''
    pass

def p_lvalue(p):
    '''lvalue : IDENTIFIER
             | IDENTIFIER LBRACKET expression RBRACKET
             | IDENTIFIER LBRACKET expression COLON expression RBRACKET'''
    pass

def p_statement(p):
    '''statement : BEGIN statement_list END
                | assignment
                | blocking_assignment
                | non_blocking_assignment
                | conditional_statement
                | case_statement
                | loop_statement
                | seq_block
                | par_block
                | task_enable
                | system_task_enable
                | disable_statement
                | event_trigger
                | IDENTIFIER SEMICOLON
                | SEMICOLON'''
    p[0] = p[1]

def p_blocking_assignment(p):
    '''blocking_assignment : lvalue ASSIGN delay_or_event_control expression
                           | lvalue ASSIGN expression'''
    pass

def p_non_blocking_assignment(p):
    '''non_blocking_assignment : lvalue NON_BLOCKING_ASSIGN delay_or_event_control expression
                               | lvalue NON_BLOCKING_ASSIGN expression'''
    pass

def p_procedural_continuous_assignment(p):
    '''procedural_continuous_assignment : ASSIGN assignment
                                       | DEASSIGN lvalue'''
    pass

def p_conditional_statement(p):
    '''conditional_statement : IF LPAREN expression RPAREN statement
                            | IF LPAREN expression RPAREN statement ELSE statement'''
    pass

def p_case_statement(p):
    '''case_statement : CASE LPAREN expression RPAREN case_items ENDCASE
                     | CASEX LPAREN expression RPAREN case_items ENDCASE
                     | CASEZ LPAREN expression RPAREN case_items ENDCASE'''
    pass

def p_case_items(p):
    '''case_items : case_item
                 | case_items case_item'''
    pass

def p_case_item(p):
    '''case_item : expression_list COLON statement
                | DEFAULT COLON statement
                | DEFAULT statement'''
    pass

def p_loop_statement(p):
    '''loop_statement : FOR LPAREN assignment SEMICOLON expression SEMICOLON assignment RPAREN statement
                     | WHILE LPAREN expression RPAREN statement
                     | REPEAT LPAREN expression RPAREN statement
                     | FOREVER statement'''
    pass

def p_seq_block(p):
    '''seq_block : BEGIN statement_list END
                | BEGIN COLON IDENTIFIER statement_list END'''
    pass

def p_par_block(p):
    '''par_block : FORK statement_list JOIN
                | FORK COLON IDENTIFIER statement_list JOIN'''
    pass

def p_statement_list(p):
    '''statement_list : statement
                     | statement_list statement'''
    pass

def p_task_enable(p):
    '''task_enable : IDENTIFIER SEMICOLON
                  | IDENTIFIER LPAREN expression_list RPAREN SEMICOLON'''
    pass

def p_system_task_enable(p):
    '''system_task_enable : SYSTEM_TASK SEMICOLON
                         | SYSTEM_TASK LPAREN expression_list RPAREN SEMICOLON
                         | SYSTEM_TASK LPAREN RPAREN SEMICOLON'''
    pass

def p_disable_statement(p):
    '''disable_statement : DISABLE IDENTIFIER SEMICOLON'''
    pass

def p_event_trigger(p):
    '''event_trigger : MINUS GT IDENTIFIER SEMICOLON'''
    pass

def p_delay_or_event_control(p):
    '''delay_or_event_control : delay_control
                             | event_control
                             | empty'''
    pass

def p_delay_control(p):
    '''delay_control : HASH NUMBER
                    | HASH IDENTIFIER
                    | HASH LPAREN expression RPAREN'''
    pass

def p_event_control(p):
    '''event_control : AT LPAREN event_expression RPAREN
                    | AT MULTIPLY
                    | AT LPAREN MULTIPLY RPAREN
                    | AT IDENTIFIER'''
    pass

def p_expression(p):
    '''expression : primary
                 | unary_expression
                 | binary_expression
                 | conditional_expression
                 | concatenation
                 | multiple_concatenation
                 | function_call
                 | system_function_call'''
    p[0] = p[1]

def p_primary(p):
    '''primary : NUMBER
              | IDENTIFIER
              | IDENTIFIER LBRACKET expression RBRACKET
              | IDENTIFIER LBRACKET expression COLON expression RBRACKET
              | STRING_LITERAL
              | LPAREN expression RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = f"({p[2]})"
    elif len(p) == 5:
        p[0] = f"{p[1]}[{p[3]}]"
    else:
        p[0] = f"{p[1]}[{p[3]}:{p[5]}]"

def p_unary_expression(p):
    '''unary_expression : PLUS primary
                       | MINUS primary
                       | LOGICAL_NOT primary
                       | BITWISE_NOT primary
                       | BITWISE_AND primary
                       | BITWISE_NAND primary
                       | BITWISE_OR primary
                       | BITWISE_NOR primary
                       | BITWISE_XOR primary
                       | BITWISE_XNOR primary'''
    p[0] = {'type': 'unary', 'operator': p[1], 'operand': p[2]}

def p_binary_expression(p):
    '''binary_expression : expression PLUS expression
                        | expression MINUS expression
                        | expression MULTIPLY expression
                        | expression DIVIDE expression
                        | expression MODULO expression
                        | expression LOGICAL_AND expression
                        | expression LOGICAL_OR expression
                        | expression BITWISE_AND expression
                        | expression BITWISE_OR expression
                        | expression BITWISE_XOR expression
                        | expression BITWISE_NAND expression
                        | expression BITWISE_NOR expression
                        | expression BITWISE_XNOR expression
                        | expression SHIFT_LEFT expression
                        | expression SHIFT_RIGHT expression
                        | expression LT expression
                        | expression LE expression
                        | expression GT expression
                        | expression GE expression
                        | expression EQ expression
                        | expression NE expression
                        | expression CASE_EQ expression
                        | expression CASE_NE expression'''
    p[0] = {'type': 'binary', 'left': p[1], 'operator': p[2], 'right': p[3]}

def p_conditional_expression(p):
    '''conditional_expression : expression QUESTION expression COLON expression'''
    p[0] = {'type': 'ternary', 'condition': p[1], 'true_expr': p[3], 'false_expr': p[5]}

def p_concatenation(p):
    '''concatenation : LBRACE expression_list RBRACE'''
    p[0] = {'type': 'concatenation', 'expressions': p[2]}

def p_multiple_concatenation(p):
    '''multiple_concatenation : LBRACE expression LBRACE expression_list RBRACE RBRACE'''
    p[0] = {'type': 'multiple_concatenation', 'repeat': p[2], 'expressions': p[4]}

def p_function_call(p):
    '''function_call : IDENTIFIER LPAREN expression_list RPAREN
                    | IDENTIFIER LPAREN RPAREN'''
    pass

def p_system_function_call(p):
    '''system_function_call : SYSTEM_FUNCTION LPAREN expression_list RPAREN
                           | SYSTEM_FUNCTION LPAREN RPAREN'''
    pass

def p_expression_list(p):
    '''expression_list : expression
                      | expression_list COMMA expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_module_instantiation(p):
    '''module_instantiation : IDENTIFIER parameter_value_assignment instance_list SEMICOLON
                           | IDENTIFIER instance_list SEMICOLON'''
    pass

def p_parameter_value_assignment(p):
    '''parameter_value_assignment : HASH LPAREN expression_list RPAREN
                                 | empty'''
    pass

def p_instance_list(p):
    '''instance_list : module_instance
                    | instance_list COMMA module_instance'''
    pass

def p_module_instance(p):
    '''module_instance : IDENTIFIER LPAREN port_connections RPAREN
                      | IDENTIFIER LPAREN RPAREN'''
    pass

def p_port_connections(p):
    '''port_connections : port_connection
                       | port_connections COMMA port_connection'''
    pass

def p_port_connection(p):
    '''port_connection : expression
                      | DOT IDENTIFIER LPAREN expression RPAREN
                      | DOT IDENTIFIER LPAREN RPAREN'''
    pass

def p_generate_block(p):
    '''generate_block : GENERATE generate_items ENDGENERATE'''
    pass

def p_generate_items(p):
    '''generate_items : generate_item
                     | generate_items generate_item'''
    pass

def p_generate_item(p):
    '''generate_item : module_item
                    | generate_conditional
                    | generate_loop
                    | generate_block'''
    pass

def p_generate_conditional(p):
    '''generate_conditional : IF LPAREN expression RPAREN generate_item
                           | IF LPAREN expression RPAREN generate_item ELSE generate_item'''
    pass

def p_generate_loop(p):
    '''generate_loop : FOR LPAREN assignment SEMICOLON expression SEMICOLON assignment RPAREN generate_item'''
    pass

def p_function_declaration(p):
    '''function_declaration : FUNCTION range IDENTIFIER SEMICOLON function_items ENDFUNCTION
                           | FUNCTION IDENTIFIER SEMICOLON function_items ENDFUNCTION
                           | FUNCTION AUTOMATIC range IDENTIFIER SEMICOLON function_items ENDFUNCTION
                           | FUNCTION AUTOMATIC IDENTIFIER SEMICOLON function_items ENDFUNCTION'''
    global parser_instance
    if parser_instance and parser_instance.current_package:
        func_name = p[4] if len(p) == 7 and p[2] == 'automatic' else p[3]
        parser_instance.add_package_symbol(parser_instance.current_package, func_name, 'function')

def p_function_items(p):
    '''function_items : function_item
                     | function_items function_item'''
    pass

def p_function_item(p):
    '''function_item : port_declaration
                    | parameter_declaration
                    | net_declaration
                    | reg_declaration
                    | integer_declaration
                    | real_declaration
                    | time_declaration
                    | statement'''
    pass

def p_task_declaration(p):
    '''task_declaration : TASK IDENTIFIER SEMICOLON task_items ENDTASK
                       | TASK AUTOMATIC IDENTIFIER SEMICOLON task_items ENDTASK'''
    global parser_instance
    if parser_instance and parser_instance.current_package:
        task_name = p[3] if len(p) == 6 and p[2] == 'automatic' else p[2]
        parser_instance.add_package_symbol(parser_instance.current_package, task_name, 'task')

def p_task_items(p):
    '''task_items : task_item
                 | task_items task_item'''
    pass

def p_task_item(p):
    '''task_item : port_declaration
                | parameter_declaration
                | net_declaration
                | reg_declaration
                | integer_declaration
                | real_declaration
                | time_declaration
                | statement'''
    pass

def p_package_declaration(p):
    '''package_declaration : PACKAGE IDENTIFIER SEMICOLON package_items ENDPACKAGE
                          | PACKAGE IDENTIFIER SEMICOLON ENDPACKAGE'''
    global current_document, parser_instance
    package_name = p[2]
    package = VerilogModule(package_name)  # Use VerilogModule for compatibility

    if parser_instance:
        parser_instance.current_package = package_name
        if len(p) == 6 and p[4]:  # Package with items
            # Package items are processed by their individual rules
            pass
        parser_instance.current_package = None

    if current_document:
        current_document.add_design_unit(package)

def p_package_items(p):
    '''package_items : package_item
                    | package_items package_item'''
    pass

def p_package_item(p):
    '''package_item : parameter_declaration
                   | localparam_declaration
                   | function_declaration
                   | task_declaration
                   | comment_or_empty'''
    pass

def p_import_statement(p):
    '''import_statement : IMPORT IDENTIFIER COLON_COLON IDENTIFIER SEMICOLON
                       | IMPORT IDENTIFIER COLON_COLON MULTIPLY SEMICOLON'''
    if len(p) == 6:  # Specific import
        package_name, symbol = p[2], p[4]
        p[0] = {'type': 'specific_import', 'package': package_name, 'symbol': symbol}
    else:  # Wildcard import
        package_name = p[2]
        p[0] = {'type': 'wildcard_import', 'package': package_name}

def p_import_list(p):
    '''import_list : import_statement
                  | import_list import_statement'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_genvar_declaration(p):
    '''genvar_declaration : GENVAR identifier_list SEMICOLON'''
    pass

def p_error(p):
    global parser_instance
    if parser_instance:
        parser_instance.error_count += 1
        if parser_instance.error_count > parser_instance.max_errors:
            raise RuntimeError("Too many syntax errors, aborting parse")

    if p:
        print(f"Syntax error at token {p.type} ('{p.value}') at line {p.lineno}")
        # Skip the problematic token
        p.lexer.skip(1)
    else:
        print("Syntax error at EOF")

def parse_verilog(filename: str, source_text: str, language: str) -> HDLDocument:
    """Parse Verilog source text and return HDLDocument"""
    global current_document, current_tokens, current_modules, parser_instance

    # Initialize global state
    current_document = HDLDocument(filename, language)
    current_tokens = []
    current_modules = []

    try:
        # Build lexer and parser
        lexer = lex.lex()
        parser = yacc.yacc(debug=False)

        # Parse the source text
        result = parser.parse(source_text, lexer=lexer, debug=False)

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
    """Enhanced Verilog Parser with symbol table and macro support"""

    def __init__(self, language: str):
        super().__init__(language)
        self.symbol_table: Dict[str, Dict[str, str]] = {}  # package_name -> {symbol_name: type}
        self.current_package: Optional[str] = None  # Track current package being parsed
        self.macros: Dict[str, str] = {}  # Store macro definitions
        self.error_count: int = 0
        self.max_errors: int = 100

    def _setup_lexer(self):
        """Setup Verilog lexer"""
        self.lexer = lex.lex()

    def _setup_parser(self):
        """Setup Verilog parser"""
        self.parser = yacc.yacc(debug=False)

    def add_package_symbol(self, package_name: str, symbol_name: str, symbol_type: str):
        """Add a symbol to a package's symbol table"""
        if package_name not in self.symbol_table:
            self.symbol_table[package_name] = {}
        self.symbol_table[package_name][symbol_name] = symbol_type

    def resolve_identifier(self, identifier: str) -> Optional[str]:
        """Resolve an identifier by checking current package and imported packages"""
        for pkg, symbols in self.symbol_table.items():
            if identifier in symbols:
                return symbols[identifier]
        return None

    def process_imports_for_module(self, import_list: List[Dict], module: VerilogModule):
        """Process import statements for a module"""
        for import_stmt in import_list:
            if import_stmt['type'] == 'wildcard_import':
                package_name = import_stmt['package']
                if package_name in self.symbol_table:
                    # Import all symbols into current scope
                    for symbol_name, symbol_type in self.symbol_table[package_name].items():
                        # Add symbol to module context (implementation depends on requirements)
                        pass
            elif import_stmt['type'] == 'specific_import':
                package_name = import_stmt['package']
                symbol_name = import_stmt['symbol']
                if package_name in self.symbol_table and symbol_name in self.symbol_table[package_name]:
                    # Import specific symbol
                    pass

    def parse(self, filename: str, source_text: str) -> HDLDocument:
        """Parse Verilog source and return HDLDocument"""
        global parser_instance
        parser_instance = self
        self.error_count = 0

        try:
            return parse_verilog(filename, source_text, self.language)
        finally:
            parser_instance = None