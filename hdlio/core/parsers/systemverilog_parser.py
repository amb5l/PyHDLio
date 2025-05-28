"""
SystemVerilog Parser implementation using PLY
(Extends Verilog parser with SystemVerilog-specific features)
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
from ..systemverilog import SystemVerilogModule, SystemVerilogInterface, SystemVerilogPackage, SystemVerilogPort
from ..base import HDLLibrary, HDLToken, HDLPortGroup

# Import Verilog parser tokens and keywords
from .verilog_parser import tokens as verilog_tokens, keywords as verilog_keywords

# Import token functions that exist in verilog_parser
from .verilog_parser import (
    t_ASSIGN, t_NON_BLOCKING_ASSIGN, t_COMMENT_BLOCK,
    t_COMMENT_LINE, t_STRING_LITERAL, t_NUMBER, t_newline, t_error,
    find_column, t_ignore
)

# Import simple token rules from verilog_parser
from .verilog_parser import (
    t_SEMICOLON, t_COLON, t_COMMA, t_DOT, t_LPAREN, t_RPAREN,
    t_LBRACKET, t_RBRACKET, t_LBRACE, t_RBRACE, t_AT, t_HASH,
    t_SHIFT_LEFT, t_SHIFT_RIGHT, t_LOGICAL_AND, t_LOGICAL_OR,
    t_EQ, t_NE, t_GE, t_LT, t_GT, t_LE, t_PLUS, t_MINUS, 
    t_MULTIPLY, t_DIVIDE, t_MODULO, t_BITWISE_AND, t_BITWISE_OR, 
    t_BITWISE_XOR, t_BITWISE_NOT, t_LOGICAL_NOT
)

# Global variables for the parser
current_library = None
current_tokens = []

# SystemVerilog tokens (extends Verilog tokens)
tokens = verilog_tokens + [
    'INTERFACE',
    'ENDINTERFACE',
    'MODPORT',
    'CLASS',
    'ENDCLASS',
    'LOGIC',
    'BIT',
    'BYTE',
    'SHORTINT',
    'INT',
    'LONGINT',
    'SHORTREAL',
    'STRING',
    'CHANDLE',
    'EVENT',
    'VIRTUAL',
    'TYPEDEF',
    'ENUM',
    'STRUCT',
    'UNION',
    'PACKED',
    'UNPACKED',
    'ALWAYS_FF',
    'ALWAYS_COMB',
    'RAND',
    'VOID',
    'NEW',
    'RETURN',
    'APOSTROPHE'
]

# SystemVerilog extends Verilog keywords
reserved = dict(verilog_keywords, **{
    # SystemVerilog-specific keywords
    'interface': 'INTERFACE',
    'endinterface': 'ENDINTERFACE',
    'modport': 'MODPORT',
    'logic': 'LOGIC',
    'bit': 'BIT',
    'byte': 'BYTE',
    'shortint': 'SHORTINT',
    'int': 'INT',
    'longint': 'LONGINT',
    'shortreal': 'SHORTREAL',
    'string': 'STRING',
    'chandle': 'CHANDLE',
    'event': 'EVENT',
    'class': 'CLASS',
    'endclass': 'ENDCLASS',
    'extends': 'EXTENDS',
    'implements': 'IMPLEMENTS',
    'virtual': 'VIRTUAL',
    'pure': 'PURE',
    'extern': 'EXTERN',
    'static': 'STATIC',
    'protected': 'PROTECTED',
    'local': 'LOCAL',
    'const': 'CONST',
    'ref': 'REF',
    'typedef': 'TYPEDEF',
    'enum': 'ENUM',
    'struct': 'STRUCT',
    'union': 'UNION',
    'packed': 'PACKED',
    'unpacked': 'UNPACKED',
    'tagged': 'TAGGED',
    'alias': 'ALIAS',
    'always_ff': 'ALWAYS_FF',
    'always_comb': 'ALWAYS_COMB',
    'always_latch': 'ALWAYS_LATCH',
    'unique': 'UNIQUE',
    'priority': 'PRIORITY',
    'final': 'FINAL',
    'iff': 'IFF',
    'inside': 'INSIDE',
    'dist': 'DIST',
    'covergroup': 'COVERGROUP',
    'endgroup': 'ENDGROUP',
    'coverpoint': 'COVERPOINT',
    'cross': 'CROSS',
    'bins': 'BINS',
    'illegal_bins': 'ILLEGAL_BINS',
    'ignore_bins': 'IGNORE_BINS',
    'wildcard': 'WILDCARD',
    'with': 'WITH',
    'matches': 'MATCHES',
    'throughout': 'THROUGHOUT',
    'within': 'WITHIN',
    'intersect': 'INTERSECT',
    'first_match': 'FIRST_MATCH',
    'expect': 'EXPECT',
    'assume': 'ASSUME',
    'assert': 'ASSERT',
    'cover': 'COVER',
    'restrict': 'RESTRICT',
    'property': 'PROPERTY',
    'endproperty': 'ENDPROPERTY',
    'sequence': 'SEQUENCE',
    'endsequence': 'ENDSEQUENCE',
    'clocking': 'CLOCKING',
    'endclocking': 'ENDCLOCKING',
    'default': 'DEFAULT',
    'global': 'GLOBAL',
    'soft': 'SOFT',
    'solve': 'SOLVE',
    'before': 'BEFORE',
    'super': 'SUPER',
    'this': 'THIS',
    'randomize': 'RANDOMIZE',
    'rand': 'RAND',
    'randc': 'RANDC',
    'constraint': 'CONSTRAINT',
    'endconstraint': 'ENDCONSTRAINT',
    'foreach': 'FOREACH',
    'return': 'RETURN',
    'break': 'BREAK',
    'continue': 'CONTINUE',
    'do': 'DO',
    'while': 'WHILE',
    'new': 'NEW',
    'null': 'NULL',
    'void': 'VOID',
    'type': 'TYPE',
    'context': 'CONTEXT',
    'pure': 'PURE',
    'join_any': 'JOIN_ANY',
    'join_none': 'JOIN_NONE',
    'wait_order': 'WAIT_ORDER',
    'mailbox': 'MAILBOX',
    'semaphore': 'SEMAPHORE',
})

# Additional SystemVerilog-specific token rules
t_QUESTION = r'\?'
t_APOSTROPHE = r"'"
t_DOLLAR = r'\$'
t_COLON_COLON = r'::'


def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFIER')
    return t


# Grammar rules for SystemVerilog


def p_source_text(p):
    '''source_text : description_list'''
    pass


def p_description_list(p):
    '''description_list : description
                       | description_list description'''
    pass


def p_description(p):
    '''description : module_declaration
                  | interface_declaration
                  | package_declaration
                  | class_declaration
                  | comment_or_empty'''
    pass


def p_module_declaration(p):
    '''module_declaration : MODULE IDENTIFIER LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE
                         | MODULE IDENTIFIER module_parameters LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE
                         | MODULE IDENTIFIER SEMICOLON module_items ENDMODULE'''
    global current_library, current_tokens

    module_name = p[2]
    module = SystemVerilogModule(module_name)

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

    if current_library:
        current_library.add_design_unit(module)


def p_interface_declaration(p):
    '''interface_declaration : INTERFACE IDENTIFIER LPAREN port_list RPAREN SEMICOLON interface_items ENDINTERFACE
                            | INTERFACE IDENTIFIER SEMICOLON interface_items ENDINTERFACE'''
    global current_library, current_tokens

    interface_name = p[2]
    interface = SystemVerilogInterface(interface_name)

    # Extract ports if they exist
    if len(p) == 9 and p[4]:  # Interface with ports
        port_groups = extract_port_groups(p[4], current_tokens)
        for group in port_groups:
            interface.add_port_group(group)

    if current_library:
        current_library.add_design_unit(interface)


def p_package_declaration(p):
    '''package_declaration : PACKAGE IDENTIFIER SEMICOLON package_items ENDPACKAGE'''
    global current_library

    package_name = p[2]
    package = SystemVerilogPackage(package_name)

    if current_library:
        current_library.add_design_unit(package)


def p_module_parameters(p):
    '''module_parameters :
                        | HASH LPAREN parameter_list RPAREN
                        | HASH LPAREN parameter_value_list RPAREN'''
    pass


def p_parameter_list(p):
    '''parameter_list : parameter_declaration
                     | parameter_list COMMA parameter_declaration'''
    pass


def p_parameter_value_list(p):
    '''parameter_value_list : parameter_value
                           | parameter_value_list COMMA parameter_value'''
    pass


def p_parameter_value(p):
    '''parameter_value : IDENTIFIER ASSIGN expression
                      | expression'''
    pass


def p_interface_items(p):
    '''interface_items :
                      | interface_items interface_item'''
    pass


def p_interface_item(p):
    '''interface_item : port_declaration
                     | modport_declaration
                     | parameter_declaration
                     | signal_declaration
                     | comment_or_empty'''
    pass


def p_package_items(p):
    '''package_items :
                    | package_items package_item'''
    pass


def p_package_item(p):
    '''package_item : parameter_declaration
                   | typedef_declaration
                   | function_declaration
                   | task_declaration
                   | comment_or_empty'''
    pass


def p_class_declaration(p):
    '''class_declaration : CLASS IDENTIFIER SEMICOLON class_items ENDCLASS'''
    pass


def p_class_items(p):
    '''class_items :
                  | class_items class_item'''
    pass


def p_class_item(p):
    '''class_item : class_property
                 | function_declaration
                 | task_declaration
                 | comment_or_empty'''
    pass


def p_class_property(p):
    '''class_property : data_type identifier_list SEMICOLON
                     | RAND data_type identifier_list SEMICOLON'''
    pass


def p_modport_declaration(p):
    '''modport_declaration : MODPORT IDENTIFIER LPAREN modport_items RPAREN SEMICOLON'''
    pass


def p_modport_items(p):
    '''modport_items : modport_item
                    | modport_items COMMA modport_item'''
    pass


def p_modport_item(p):
    '''modport_item : INPUT modport_port_list
                   | OUTPUT modport_port_list
                   | INOUT modport_port_list'''
    pass


def p_modport_port_list(p):
    '''modport_port_list : IDENTIFIER
                        | modport_port_list COMMA IDENTIFIER'''
    pass


def p_typedef_declaration(p):
    '''typedef_declaration : TYPEDEF data_type IDENTIFIER SEMICOLON
                          | TYPEDEF enum_declaration IDENTIFIER SEMICOLON
                          | TYPEDEF struct_declaration IDENTIFIER SEMICOLON
                          | TYPEDEF union_declaration IDENTIFIER SEMICOLON'''
    pass


def p_enum_declaration(p):
    '''enum_declaration : ENUM data_type LBRACE enum_items RBRACE'''
    pass


def p_enum_items(p):
    '''enum_items : enum_item
                 | enum_items COMMA enum_item'''
    pass


def p_enum_item(p):
    '''enum_item : IDENTIFIER
                | IDENTIFIER ASSIGN expression'''
    pass


def p_struct_declaration(p):
    '''struct_declaration : STRUCT PACKED LBRACE struct_items RBRACE
                         | STRUCT LBRACE struct_items RBRACE'''
    pass


def p_union_declaration(p):
    '''union_declaration : UNION PACKED LBRACE struct_items RBRACE
                        | UNION LBRACE struct_items RBRACE'''
    pass


def p_struct_items(p):
    '''struct_items : struct_item
                   | struct_items struct_item'''
    pass


def p_struct_item(p):
    '''struct_item : data_type identifier_list SEMICOLON
                  | data_type LBRACKET expression RBRACKET identifier_list SEMICOLON'''
    pass


def p_function_declaration(p):
    '''function_declaration : FUNCTION data_type IDENTIFIER LPAREN function_args RPAREN SEMICOLON function_body ENDFUNCTION
                           | FUNCTION AUTOMATIC data_type IDENTIFIER LPAREN function_args RPAREN SEMICOLON function_body ENDFUNCTION
                           | FUNCTION VOID IDENTIFIER LPAREN function_args RPAREN SEMICOLON function_body ENDFUNCTION
                           | FUNCTION AUTOMATIC VOID IDENTIFIER LPAREN function_args RPAREN SEMICOLON function_body ENDFUNCTION
                           | FUNCTION NEW LPAREN function_args RPAREN SEMICOLON function_body ENDFUNCTION'''
    pass


def p_task_declaration(p):
    '''task_declaration : TASK IDENTIFIER LPAREN task_args RPAREN SEMICOLON task_body ENDTASK
                       | TASK AUTOMATIC IDENTIFIER LPAREN task_args RPAREN SEMICOLON task_body ENDTASK'''
    pass


def p_function_args(p):
    '''function_args :
                    | function_arg_list'''
    pass


def p_function_arg_list(p):
    '''function_arg_list : function_arg
                        | function_arg_list COMMA function_arg'''
    pass


def p_function_arg(p):
    '''function_arg : data_type IDENTIFIER
                   | INPUT data_type IDENTIFIER
                   | OUTPUT data_type IDENTIFIER'''
    pass


def p_task_args(p):
    '''task_args :
                | task_arg_list'''
    pass


def p_task_arg_list(p):
    '''task_arg_list : task_arg
                    | task_arg_list COMMA task_arg'''
    pass


def p_task_arg(p):
    '''task_arg : data_type IDENTIFIER
               | INPUT data_type IDENTIFIER
               | OUTPUT data_type IDENTIFIER
               | INOUT data_type IDENTIFIER'''
    pass


def p_function_body(p):
    '''function_body : statement_list
                    | statement_list return_statement'''
    pass


def p_task_body(p):
    '''task_body : statement_list'''
    pass


def p_return_statement(p):
    '''return_statement : RETURN expression SEMICOLON
                       | RETURN SEMICOLON'''
    pass


def p_data_type(p):
    '''data_type : LOGIC
                | BIT
                | BYTE
                | SHORTINT
                | INT
                | LONGINT
                | SHORTREAL
                | STRING
                | CHANDLE
                | EVENT
                | IDENTIFIER
                | data_type LBRACKET expression RBRACKET
                | data_type LBRACKET expression COLON expression RBRACKET'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]}[{p[3]}]" if len(p) == 5 else f"{p[1]}[{p[3]}:{p[5]}]"


def p_signal_declaration(p):
    '''signal_declaration : data_type identifier_list SEMICOLON'''
    pass


def p_port_declaration(p):
    '''port_declaration : INPUT data_type identifier_list SEMICOLON
                       | OUTPUT data_type identifier_list SEMICOLON
                       | INOUT data_type identifier_list SEMICOLON
                       | INPUT data_type LBRACKET expression RBRACKET identifier_list SEMICOLON
                       | OUTPUT data_type LBRACKET expression RBRACKET identifier_list SEMICOLON
                       | INOUT data_type LBRACKET expression RBRACKET identifier_list SEMICOLON'''
    pass


def p_identifier_list(p):
    '''identifier_list : IDENTIFIER
                      | identifier_list COMMA IDENTIFIER'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


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
           | INPUT data_type IDENTIFIER
           | OUTPUT data_type IDENTIFIER
           | INOUT data_type IDENTIFIER
           | INPUT data_type LBRACKET expression RBRACKET IDENTIFIER
           | OUTPUT data_type LBRACKET expression RBRACKET IDENTIFIER
           | INOUT data_type LBRACKET expression RBRACKET IDENTIFIER
           | IDENTIFIER DOT IDENTIFIER IDENTIFIER'''

    # Extract port information
    if len(p) == 2:  # Just identifier
        p[0] = {'name': p[1], 'direction': None, 'type': 'logic', 'range': None}
    elif len(p) == 4:  # direction + data_type + identifier
        p[0] = {'name': p[3], 'direction': p[1], 'type': p[2], 'range': None}
    elif len(p) == 5:  # interface.modport identifier
        p[0] = {'name': p[4], 'direction': None, 'type': f"{p[1]}.{p[3]}", 'range': None}
    elif len(p) == 7:  # direction + data_type + range + identifier
        p[0] = {'name': p[6], 'direction': p[1], 'type': p[2], 'range': f"[{p[4]}]"}


def p_module_items(p):
    '''module_items :
                   | module_items module_item'''
    pass


def p_module_item(p):
    '''module_item : port_declaration
                  | parameter_declaration
                  | signal_declaration
                  | typedef_declaration
                  | always_block
                  | always_ff_block
                  | always_comb_block
                  | assign_statement
                  | module_instantiation
                  | generate_block
                  | function_declaration
                  | task_declaration
                  | comment_or_empty'''
    pass


def p_always_ff_block(p):
    '''always_ff_block : ALWAYS_FF AT LPAREN event_expression RPAREN statement'''
    pass


def p_always_comb_block(p):
    '''always_comb_block : ALWAYS_COMB statement'''
    pass


def p_always_block(p):
    '''always_block : ALWAYS AT LPAREN event_expression RPAREN statement'''
    pass


def p_event_expression(p):
    '''event_expression : POSEDGE IDENTIFIER
                       | NEGEDGE IDENTIFIER
                       | IDENTIFIER
                       | event_expression OR event_expression'''
    pass


def p_statement(p):
    '''statement : BEGIN statement_list END
                | assignment
                | if_statement
                | case_statement
                | for_loop
                | while_loop
                | return_statement
                | IDENTIFIER SEMICOLON
                | SEMICOLON'''
    pass


def p_statement_list(p):
    '''statement_list :
                     | statement_list statement'''
    pass


def p_assignment(p):
    '''assignment : IDENTIFIER ASSIGN expression SEMICOLON
                 | IDENTIFIER NON_BLOCKING_ASSIGN expression SEMICOLON
                 | hierarchical_identifier ASSIGN expression SEMICOLON
                 | hierarchical_identifier NON_BLOCKING_ASSIGN expression SEMICOLON'''
    pass


def p_if_statement(p):
    '''if_statement : IF LPAREN expression RPAREN statement
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
    '''case_item : expression COLON statement
                | DEFAULT COLON statement'''
    pass


def p_for_loop(p):
    '''for_loop : FOR LPAREN assignment expression SEMICOLON assignment RPAREN statement'''
    pass


def p_while_loop(p):
    '''while_loop : WHILE LPAREN expression RPAREN statement'''
    pass


def p_assign_statement(p):
    '''assign_statement : ASSIGN assignment_list SEMICOLON'''
    pass


def p_assignment_list(p):
    '''assignment_list : assignment_item
                      | assignment_list COMMA assignment_item'''
    pass


def p_assignment_item(p):
    '''assignment_item : IDENTIFIER ASSIGN expression'''
    pass


def p_parameter_declaration(p):
    '''parameter_declaration : PARAMETER data_type IDENTIFIER ASSIGN expression SEMICOLON
                            | PARAMETER IDENTIFIER ASSIGN expression SEMICOLON'''
    pass


def p_module_instantiation(p):
    '''module_instantiation : IDENTIFIER instance_list SEMICOLON
                           | IDENTIFIER HASH LPAREN parameter_assignments RPAREN instance_list SEMICOLON'''
    pass


def p_instance_list(p):
    '''instance_list : module_instance
                    | instance_list COMMA module_instance'''
    pass


def p_module_instance(p):
    '''module_instance : IDENTIFIER LPAREN port_connections RPAREN'''
    pass


def p_port_connections(p):
    '''port_connections :
                       | port_connection_list'''
    pass


def p_port_connection_list(p):
    '''port_connection_list : port_connection
                           | port_connection_list COMMA port_connection'''
    pass


def p_port_connection(p):
    '''port_connection : DOT IDENTIFIER LPAREN expression RPAREN
                      | expression'''
    pass


def p_parameter_assignments(p):
    '''parameter_assignments : parameter_assignment
                            | parameter_assignments COMMA parameter_assignment'''
    pass


def p_parameter_assignment(p):
    '''parameter_assignment : DOT IDENTIFIER LPAREN expression RPAREN
                            | expression'''
    pass


def p_generate_block(p):
    '''generate_block : GENERATE generate_items ENDGENERATE'''
    pass


def p_generate_items(p):
    '''generate_items :
                     | generate_items generate_item'''
    pass


def p_generate_item(p):
    '''generate_item : module_item
                    | generate_conditional
                    | generate_loop'''
    pass


def p_generate_conditional(p):
    '''generate_conditional : IF LPAREN expression RPAREN generate_item
                            | IF LPAREN expression RPAREN generate_item ELSE generate_item'''
    pass


def p_generate_loop(p):
    '''generate_loop : FOR LPAREN GENVAR IDENTIFIER ASSIGN expression SEMICOLON expression SEMICOLON IDENTIFIER ASSIGN expression RPAREN generate_item
                    | FOR LPAREN IDENTIFIER ASSIGN expression SEMICOLON expression SEMICOLON IDENTIFIER ASSIGN expression RPAREN generate_item'''
    pass


def p_expression(p):
    '''expression : primary
                 | unary_expression
                 | binary_expression
                 | conditional_expression'''
    p[0] = p[1]


def p_primary(p):
    '''primary : IDENTIFIER
              | NUMBER
              | STRING_LITERAL
              | LPAREN expression RPAREN
              | concatenation
              | function_call
              | system_task_call
              | fill_pattern
              | hierarchical_identifier'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]  # For parenthesized expressions


def p_unary_expression(p):
    '''unary_expression : PLUS primary
                       | MINUS primary
                       | LOGICAL_NOT primary
                       | BITWISE_NOT primary'''
    p[0] = f"{p[1]}{p[2]}"


def p_binary_expression(p):
    '''binary_expression : expression PLUS expression
                        | expression MINUS expression
                        | expression MULTIPLY expression
                        | expression DIVIDE expression
                        | expression MODULO expression
                        | expression EQ expression
                        | expression NE expression
                        | expression LT expression
                        | expression GT expression
                        | expression LOGICAL_AND expression
                        | expression LOGICAL_OR expression
                        | expression BITWISE_AND expression
                        | expression BITWISE_OR expression
                        | expression BITWISE_XOR expression
                        | expression SHIFT_LEFT expression
                        | expression SHIFT_RIGHT expression'''
    p[0] = f"{p[1]} {p[2]} {p[3]}"


def p_conditional_expression(p):
    '''conditional_expression : expression QUESTION expression COLON expression'''
    p[0] = f"{p[1]} ? {p[3]} : {p[5]}"


def p_concatenation(p):
    '''concatenation : LBRACE expression_list RBRACE'''
    p[0] = f"{{{p[2]}}}"


def p_function_call(p):
    '''function_call : IDENTIFIER LPAREN expression_list RPAREN
                    | IDENTIFIER LPAREN RPAREN'''
    if len(p) == 5:
        p[0] = f"{p[1]}({p[3]})"
    else:
        p[0] = f"{p[1]}()"


def p_expression_list(p):
    '''expression_list : expression
                      | expression_list COMMA expression'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = f"{p[1]}, {p[3]}"


def p_fill_pattern(p):
    '''fill_pattern : APOSTROPHE NUMBER
                   | APOSTROPHE IDENTIFIER'''
    p[0] = f"'{p[2]}"


def p_system_task_call(p):
    '''system_task_call : DOLLAR IDENTIFIER LPAREN expression_list RPAREN
                       | DOLLAR IDENTIFIER LPAREN RPAREN
                       | DOLLAR IDENTIFIER'''
    if len(p) == 6:
        p[0] = f"${p[2]}({p[4]})"
    elif len(p) == 5:
        p[0] = f"${p[2]}()"
    else:
        p[0] = f"${p[2]}"


def p_comment_or_empty(p):
    '''comment_or_empty : COMMENT_LINE
                       | COMMENT_BLOCK
                       | empty'''
    pass


def p_empty(p):
    '''empty :'''
    pass


def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} ('{p.value}') at line {p.lineno}")
    else:
        print("Syntax error at EOF")


def extract_port_groups(port_list, tokens):
    """Extract port groups from parsed port list"""
    if not port_list:
        return []

    port_groups = []
    current_group = None

    for port_info in port_list:
        if isinstance(port_info, dict):
            port_name = port_info.get('name', '')
            port_direction = port_info.get('direction', '')
            port_type = port_info.get('type', 'logic')
            port_range = port_info.get('range', '')

            # Create SystemVerilog port
            port = SystemVerilogPort(port_name, port_type, port_direction)

            # Create port group
            port_group = HDLPortGroup()
            port_group.add_port(port)
            port_groups.append(port_group)

    return port_groups


def parse_systemverilog(filename: str, source_text: str, hdl_lrm) -> HDLLibrary:
    """Parse SystemVerilog source code"""
    global current_library, current_tokens

    # Convert HDL_LRM enum to string for library language field
    language_str = hdl_lrm.value if hasattr(hdl_lrm, 'value') else str(hdl_lrm)
    
    current_library = HDLLibrary(filename, language_str)
    current_tokens = []

    try:
        # Build lexer and parser
        lexer = lex.lex()
        parser = yacc.yacc(debug=False)

        # Parse the source text
        result = parser.parse(source_text, lexer=lexer)

        return current_library

    except Exception as e:
        print(f"Error parsing SystemVerilog: {e}")
        return current_library


class SystemVerilogParser(BaseHDLParser):
    """SystemVerilog Parser using PLY"""

    def __init__(self, hdl_lrm):
        super().__init__(hdl_lrm)

    def _setup_lexer(self):
        """Setup SystemVerilog lexer"""
        self.lexer = lex.lex()

    def _setup_parser(self):
        """Setup SystemVerilog parser"""
        self.parser = yacc.yacc(debug=False)

    def parse(self, filename: str, source_text: str, library_name: str = "work") -> HDLLibrary:
        """Parse SystemVerilog source code"""
        return parse_systemverilog(filename, source_text, self.hdl_lrm)


def p_hierarchical_identifier(p):
    '''hierarchical_identifier : IDENTIFIER DOT IDENTIFIER
                              | hierarchical_identifier DOT IDENTIFIER'''
    if len(p) == 4:
        p[0] = f"{p[1]}.{p[3]}"
    else:
        p[0] = f"{p[1]}.{p[3]}"
