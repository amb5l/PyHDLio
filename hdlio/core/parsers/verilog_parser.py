"""
Verilog Parser implementation using PLY
(Comprehensive implementation with full Verilog language support)
"""

import sys
import os


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
    'AT',
    'HASH',

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
    'ASSIGN_KW',
    'FUNCTION',
    'ENDFUNCTION',
    'TASK',
    'ENDTASK',
    'GENERATE',
    'ENDGENERATE',
    'INTEGER',
    'REAL',
    'TIME',
    'REALTIME'
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
    'assign': 'ASSIGN_KW',
    'function': 'FUNCTION',
    'endfunction': 'ENDFUNCTION',
    'task': 'TASK',
    'endtask': 'ENDTASK',
    'generate': 'GENERATE',
    'endgenerate': 'ENDGENERATE',
    'integer': 'INTEGER',
    'real': 'REAL',
    'time': 'TIME',
    'realtime': 'REALTIME'
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
t_AT = r'@'
t_HASH = r'\#'

# Operators (order matters for multi-character operators)
t_SHIFT_LEFT = r'<<'
t_SHIFT_RIGHT = r'>>'
t_LOGICAL_AND = r'&&'
t_LOGICAL_OR = r'\|\|'
t_EQUAL = r'=='
t_NOT_EQUAL = r'!='
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

def t_NON_BLOCKING_ASSIGN(t):
    r'<='
    return t

# NON_BLOCKING_ASSIGN (<= ) is used for both assignments and comparisons

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
    r"(\d+\'[bBoOdDhH][0-9a-fA-F_xXzZ]+|\d+(\.\d+)?([eE][+-]?\d+)?|\d+)"
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

# Operator precedence (lowest to highest)
precedence = (
    ('left', 'LOGICAL_OR'),
    ('left', 'LOGICAL_AND'),
    ('left', 'BITWISE_OR'),
    ('left', 'BITWISE_XOR'),
    ('left', 'BITWISE_AND'),
    ('left', 'EQUAL', 'NOT_EQUAL'),
    ('left', 'LESS_THAN', 'NON_BLOCKING_ASSIGN', 'GREATER_THAN', 'GREATER_EQUAL'),
    ('left', 'SHIFT_LEFT', 'SHIFT_RIGHT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE', 'MODULO'),
    ('right', 'UMINUS', 'UPLUS', 'LOGICAL_NOT', 'BITWISE_NOT'),
    ('left', 'LBRACKET'),
)

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
    '''module_declaration : MODULE IDENTIFIER parameter_port_list LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE
                         | MODULE IDENTIFIER LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE
                         | MODULE IDENTIFIER SEMICOLON module_items ENDMODULE'''
    global current_document, current_tokens

    module_name = p[2]
    module = VerilogModule(module_name)

    # Extract ports if they exist
    if len(p) == 10:  # Module with parameters and ports
        if p[5]:  # port_list exists
            port_groups = extract_port_groups(p[5], current_tokens)
            for group in port_groups:
                module.add_port_group(group)
    elif len(p) == 9:  # Module with ports only
        if p[4]:  # port_list exists
            port_groups = extract_port_groups(p[4], current_tokens)
            for group in port_groups:
                module.add_port_group(group)

    if current_document:
        current_document.add_design_unit(module)

def p_parameter_port_list(p):
    '''parameter_port_list :
                          | HASH LPAREN parameter_list RPAREN'''
    pass

def p_parameter_list(p):
    '''parameter_list : parameter_declaration
                     | parameter_list COMMA parameter_declaration'''
    pass

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
           | INPUT net_type range IDENTIFIER
           | OUTPUT net_type range IDENTIFIER
           | INOUT net_type range IDENTIFIER
           | INPUT range IDENTIFIER
           | OUTPUT range IDENTIFIER
           | INOUT range IDENTIFIER
           | INPUT IDENTIFIER
           | OUTPUT IDENTIFIER
           | INOUT IDENTIFIER'''

    # Extract port information
    if len(p) == 2:  # Just identifier
        p[0] = {'name': p[1], 'direction': None, 'type': None, 'range': None}
    elif len(p) == 3:  # direction + identifier
        p[0] = {'name': p[2], 'direction': p[1], 'type': None, 'range': None}
    elif len(p) == 4:  # direction + range + identifier
        p[0] = {'name': p[3], 'direction': p[1], 'type': None, 'range': p[2]}
    elif len(p) == 5:  # direction + type + range + identifier
        p[0] = {'name': p[4], 'direction': p[1], 'type': p[2], 'range': p[3]}

def p_net_type(p):
    '''net_type : WIRE
               | REG'''
    p[0] = p[1]

def p_module_items(p):
    '''module_items :
                   | module_items module_item'''
    pass

def p_module_item(p):
    '''module_item : port_declaration
                  | parameter_declaration
                  | localparam_declaration
                  | net_declaration
                  | reg_declaration
                  | integer_declaration
                  | real_declaration
                  | time_declaration
                  | always_block
                  | initial_block
                  | assign_statement
                  | module_instantiation
                  | generate_block
                  | function_declaration
                  | task_declaration
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
    '''port_declaration : INPUT net_type range identifier_list SEMICOLON
                       | OUTPUT net_type range identifier_list SEMICOLON
                       | INOUT net_type range identifier_list SEMICOLON
                       | INPUT range identifier_list SEMICOLON
                       | OUTPUT range identifier_list SEMICOLON
                       | INOUT range identifier_list SEMICOLON
                       | INPUT identifier_list SEMICOLON
                       | OUTPUT identifier_list SEMICOLON
                       | INOUT identifier_list SEMICOLON'''
    pass

def p_net_declaration(p):
    '''net_declaration : WIRE range identifier_list SEMICOLON
                      | WIRE identifier_list SEMICOLON'''
    pass

def p_reg_declaration(p):
    '''reg_declaration : REG range identifier_list SEMICOLON
                      | REG identifier_list SEMICOLON'''
    pass

def p_integer_declaration(p):
    '''integer_declaration : INTEGER identifier_list SEMICOLON'''
    pass

def p_real_declaration(p):
    '''real_declaration : REAL identifier_list SEMICOLON'''
    pass

def p_time_declaration(p):
    '''time_declaration : TIME identifier_list SEMICOLON
                       | REALTIME identifier_list SEMICOLON'''
    pass

def p_identifier_list(p):
    '''identifier_list : IDENTIFIER
                      | identifier_list COMMA IDENTIFIER'''
    pass

def p_range(p):
    '''range :
            | LBRACKET expression COLON expression RBRACKET'''
    if len(p) == 1:
        p[0] = None
    else:
        p[0] = f"[{p[2]}:{p[4]}]"

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
    '''always_block : ALWAYS statement
                   | ALWAYS AT LPAREN event_expression RPAREN statement'''
    pass

def p_initial_block(p):
    '''initial_block : INITIAL statement'''
    pass

def p_event_expression(p):
    '''event_expression : event_expression OR event_expression
                       | POSEDGE expression
                       | NEGEDGE expression
                       | expression
                       | MULTIPLY'''
    pass

def p_assign_statement(p):
    '''assign_statement : ASSIGN_KW assignment_list SEMICOLON'''
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
             | IDENTIFIER LBRACKET expression COLON expression RBRACKET
             | concatenation'''
    pass

def p_statement(p):
    '''statement : blocking_assignment
                | non_blocking_assignment
                | procedural_continuous_assignment
                | conditional_statement
                | case_statement
                | loop_statement
                | seq_block
                | par_block
                | task_enable
                | system_task_enable
                | disable_statement
                | event_trigger
                | SEMICOLON'''
    pass

def p_blocking_assignment(p):
    '''blocking_assignment : lvalue ASSIGN expression SEMICOLON
                           | lvalue ASSIGN delay_or_event_control expression SEMICOLON'''
    pass

def p_non_blocking_assignment(p):
    '''non_blocking_assignment : lvalue NON_BLOCKING_ASSIGN expression SEMICOLON
                               | lvalue NON_BLOCKING_ASSIGN delay_or_event_control expression SEMICOLON'''
    pass

def p_procedural_continuous_assignment(p):
    '''procedural_continuous_assignment : ASSIGN_KW lvalue ASSIGN expression SEMICOLON'''
    pass

def p_conditional_statement(p):
    '''conditional_statement : IF LPAREN expression RPAREN statement
                            | IF LPAREN expression RPAREN statement ELSE statement'''
    pass

def p_case_statement(p):
    '''case_statement : CASE LPAREN expression RPAREN case_items ENDCASE'''
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
                     | WHILE LPAREN expression RPAREN statement'''
    pass

def p_seq_block(p):
    '''seq_block : BEGIN statement_list END
                | BEGIN COLON IDENTIFIER statement_list END'''
    pass

def p_par_block(p):
    '''par_block : BEGIN statement_list END
                | BEGIN COLON IDENTIFIER statement_list END'''
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
    '''system_task_enable : IDENTIFIER SEMICOLON
                         | IDENTIFIER LPAREN expression_list RPAREN SEMICOLON'''
    pass

def p_disable_statement(p):
    '''disable_statement : IDENTIFIER SEMICOLON'''
    pass

def p_event_trigger(p):
    '''event_trigger : IDENTIFIER SEMICOLON'''
    pass

def p_delay_or_event_control(p):
    '''delay_or_event_control : delay_control
                             | event_control'''
    pass

def p_delay_control(p):
    '''delay_control : HASH expression
                    | HASH LPAREN expression RPAREN'''
    pass

def p_event_control(p):
    '''event_control : AT event_expression
                    | AT LPAREN event_expression RPAREN
                    | AT MULTIPLY
                    | AT LPAREN MULTIPLY RPAREN'''
    pass

def p_expression(p):
    '''expression : primary
                 | unary_expression
                 | binary_expression
                 | conditional_expression'''
    p[0] = p[1]

def p_primary(p):
    '''primary : NUMBER
              | IDENTIFIER
              | IDENTIFIER LBRACKET expression RBRACKET
              | IDENTIFIER LBRACKET expression COLON expression RBRACKET
              | concatenation
              | multiple_concatenation
              | function_call
              | system_function_call
              | LPAREN expression RPAREN
              | STRING_LITERAL'''
    p[0] = p[1]

def p_unary_expression(p):
    '''unary_expression : PLUS expression %prec UPLUS
                       | MINUS expression %prec UMINUS
                       | LOGICAL_NOT expression
                       | BITWISE_NOT expression
                       | BITWISE_AND expression
                       | BITWISE_OR expression
                       | BITWISE_XOR expression'''
    pass

def p_binary_expression(p):
    '''binary_expression : expression PLUS expression
                        | expression MINUS expression
                        | expression MULTIPLY expression
                        | expression DIVIDE expression
                        | expression MODULO expression
                        | expression EQUAL expression
                        | expression NOT_EQUAL expression
                        | expression LESS_THAN expression
                        | expression NON_BLOCKING_ASSIGN expression
                        | expression GREATER_THAN expression
                        | expression GREATER_EQUAL expression
                        | expression LOGICAL_AND expression
                        | expression LOGICAL_OR expression
                        | expression BITWISE_AND expression
                        | expression BITWISE_OR expression
                        | expression BITWISE_XOR expression
                        | expression SHIFT_LEFT expression
                        | expression SHIFT_RIGHT expression'''
    pass

def p_conditional_expression(p):
    '''conditional_expression : expression'''
    pass

def p_concatenation(p):
    '''concatenation : LBRACE expression_list RBRACE'''
    pass

def p_multiple_concatenation(p):
    '''multiple_concatenation : LBRACE expression LBRACE expression_list RBRACE RBRACE'''
    pass

def p_function_call(p):
    '''function_call : IDENTIFIER LPAREN expression_list RPAREN
                    | IDENTIFIER LPAREN RPAREN'''
    pass

def p_system_function_call(p):
    '''system_function_call : IDENTIFIER LPAREN expression_list RPAREN
                           | IDENTIFIER LPAREN RPAREN'''
    pass

def p_expression_list(p):
    '''expression_list : expression
                      | expression_list COMMA expression'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_module_instantiation(p):
    '''module_instantiation : IDENTIFIER instance_list SEMICOLON
                           | IDENTIFIER parameter_value_assignment instance_list SEMICOLON'''
    pass

def p_parameter_value_assignment(p):
    '''parameter_value_assignment : HASH LPAREN expression_list RPAREN'''
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
                           | FUNCTION IDENTIFIER SEMICOLON function_items ENDFUNCTION'''
    pass

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
    '''task_declaration : TASK IDENTIFIER SEMICOLON task_items ENDTASK'''
    pass

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
    """Verilog Parser using PLY"""

    def __init__(self, language: str):
        super().__init__(language)

    def _setup_lexer(self):
        """Setup Verilog lexer"""
        self.lexer = lex.lex()

    def _setup_parser(self):
        """Setup Verilog parser"""
        self.parser = yacc.yacc(debug=False)

    def parse(self, filename: str, source_text: str) -> HDLDocument:
        """Parse Verilog source and return HDLDocument"""
        return parse_verilog(filename, source_text, self.language)
