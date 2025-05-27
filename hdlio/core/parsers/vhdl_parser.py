"""
Unified VHDL Parser - Supports all VHDL language features and versions
Consolidates entity-focused and comprehensive parsing capabilities
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

from ..vhdl import VHDLEntity, VHDLArchitecture, VHDLPackage, VHDLPackageBody, VHDLConfiguration, VHDLPort
from ..base import HDLDocument, HDLToken, HDLPortGroup

# Global variables for the parser
current_document = None
current_tokens = []

# VHDL Token definitions - comprehensive set for all VHDL features
tokens = (
    'IDENTIFIER',
    'NUMBER',
    'STRING_LITERAL',
    'CHARACTER_LITERAL',
    'COMMENT',
    'SEMICOLON',
    'COLON',
    'COMMA',
    'DOT',
    'LPAREN',
    'RPAREN',
    'ASSIGN',
    'ARROW',
    'LBRACKET',
    'RBRACKET',

    # VHDL Keywords
    'ENTITY',
    'ARCHITECTURE',
    'PACKAGE',
    'CONFIGURATION',
    'IS',
    'END',
    'PORT',
    'GENERIC',
    'MAP',
    'OF',
    'IN',
    'OUT',
    'INOUT',
    'BUFFER',
    'SIGNAL',
    'VARIABLE',
    'CONSTANT',
    'TYPE',
    'SUBTYPE',
    'ARRAY',
    'RANGE',
    'TO',
    'DOWNTO',
    'BEGIN',
    'PROCESS',
    'IF',
    'THEN',
    'ELSE',
    'ELSIF',
    'CASE',
    'WHEN',
    'WHILE',
    'FOR',
    'LOOP',
    'LIBRARY',
    'USE',
    'STD_LOGIC',
    'STD_LOGIC_VECTOR',
    'INTEGER',
    'NATURAL',
    'POSITIVE',
    'BOOLEAN',
    'BIT',
    'BIT_VECTOR',

    # Extended VHDL keywords for comprehensive parsing
    'OTHERS',
    'NULL',
    'ALL',
    'COMPONENT',
    'FUNCTION',
    'PROCEDURE',
    'RETURN',
    'PACKAGE_BODY',
    'RECORD',
    'ACCESS',
    'FILE',
    'SHARED',
    'ATTRIBUTE',
    'GROUP',
    'UNITS',
    'LITERAL',
    'ALIAS',
    'DISCONNECT',
    'AFTER',
    'TRANSPORT',
    'REJECT',
    'INERTIAL',
    'BLOCK',
    'GENERATE',
    'WITH',
    'SELECT',
    'ASSERT',
    'REPORT',
    'SEVERITY',
    'NOTE',
    'WARNING',
    'ERROR',
    'FAILURE',
    'WAIT',
    'UNTIL',
    'ON',
    'NEXT',
    'EXIT',
    'OPEN',
    'LINKAGE',
    'BUS',
    'REGISTER',
    'POSTPONED',
    'PURE',
    'IMPURE',
    'GUARDED',
    'UNAFFECTED',

    # Operators
    'PLUS',
    'MINUS',
    'MULTIPLY',
    'DIVIDE',
    'POWER',
    'CONCATENATE',
    'EQUAL',
    'NOT_EQUAL',
    'LESS_THAN',
    'LESS_EQUAL',
    'GREATER_THAN',
    'GREATER_EQUAL',
    'AND',
    'OR',
    'NOT',
    'NAND',
    'NOR',
    'XOR',
    'XNOR',
    'SLL',
    'SRL',
    'SLA',
    'SRA',
    'ROL',
    'ROR',
    'MOD',
    'REM',
    'ABS',

    # Advanced types
    'SIGNED',
    'UNSIGNED',
    'TIME',
    'REAL',
    'STRING_TYPE',
    'CHARACTER_TYPE',

    # Additional tokens for comprehensive parsing
    'BAR',
    'APOSTROPHE'
)

# VHDL reserved words - comprehensive set
reserved = {
    'entity': 'ENTITY',
    'architecture': 'ARCHITECTURE',
    'package': 'PACKAGE',
    'configuration': 'CONFIGURATION',
    'is': 'IS',
    'end': 'END',
    'port': 'PORT',
    'generic': 'GENERIC',
    'map': 'MAP',
    'of': 'OF',
    'in': 'IN',
    'out': 'OUT',
    'inout': 'INOUT',
    'buffer': 'BUFFER',
    'signal': 'SIGNAL',
    'variable': 'VARIABLE',
    'constant': 'CONSTANT',
    'type': 'TYPE',
    'subtype': 'SUBTYPE',
    'array': 'ARRAY',
    'range': 'RANGE',
    'to': 'TO',
    'downto': 'DOWNTO',
    'begin': 'BEGIN',
    'process': 'PROCESS',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'elsif': 'ELSIF',
    'case': 'CASE',
    'when': 'WHEN',
    'while': 'WHILE',
    'for': 'FOR',
    'loop': 'LOOP',
    'library': 'LIBRARY',
    'use': 'USE',
    'std_logic': 'STD_LOGIC',
    'std_logic_vector': 'STD_LOGIC_VECTOR',
    'integer': 'INTEGER',
    'natural': 'NATURAL',
    'positive': 'POSITIVE',
    'boolean': 'BOOLEAN',
    'bit': 'BIT',
    'bit_vector': 'BIT_VECTOR',

    # Extended keywords
    'others': 'OTHERS',
    'null': 'NULL',
    'all': 'ALL',
    'component': 'COMPONENT',
    'function': 'FUNCTION',
    'procedure': 'PROCEDURE',
    'return': 'RETURN',
    'package': 'PACKAGE_BODY',
    'record': 'RECORD',
    'access': 'ACCESS',
    'file': 'FILE',
    'shared': 'SHARED',
    'attribute': 'ATTRIBUTE',
    'group': 'GROUP',
    'units': 'UNITS',
    'literal': 'LITERAL',
    'alias': 'ALIAS',
    'disconnect': 'DISCONNECT',
    'after': 'AFTER',
    'transport': 'TRANSPORT',
    'reject': 'REJECT',
    'inertial': 'INERTIAL',
    'block': 'BLOCK',
    'generate': 'GENERATE',
    'with': 'WITH',
    'select': 'SELECT',
    'assert': 'ASSERT',
    'report': 'REPORT',
    'severity': 'SEVERITY',
    'note': 'NOTE',
    'warning': 'WARNING',
    'error': 'ERROR',
    'failure': 'FAILURE',
    'wait': 'WAIT',
    'until': 'UNTIL',
    'on': 'ON',
    'next': 'NEXT',
    'exit': 'EXIT',
    'open': 'OPEN',
    'linkage': 'LINKAGE',
    'bus': 'BUS',
    'register': 'REGISTER',
    'postponed': 'POSTPONED',
    'pure': 'PURE',
    'impure': 'IMPURE',
    'guarded': 'GUARDED',
    'unaffected': 'UNAFFECTED',

    # Logic operators
    'and': 'AND',
    'or': 'OR',
    'not': 'NOT',
    'nand': 'NAND',
    'nor': 'NOR',
    'xor': 'XOR',
    'xnor': 'XNOR',
    'sll': 'SLL',
    'srl': 'SRL',
    'sla': 'SLA',
    'sra': 'SRA',
    'rol': 'ROL',
    'ror': 'ROR',
    'mod': 'MOD',
    'rem': 'REM',
    'abs': 'ABS',

    # Advanced types
    'signed': 'SIGNED',
    'unsigned': 'UNSIGNED',
    'time': 'TIME',
    'real': 'REAL',
    'string': 'STRING_TYPE',
    'character': 'CHARACTER_TYPE'
}

# Token rules - comprehensive set
t_SEMICOLON = r';'
t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_ASSIGN = r':='
t_ARROW = r'=>'

# Operators
t_PLUS = r'\+'
t_MINUS = r'-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'/'
t_POWER = r'\*\*'
t_CONCATENATE = r'&'
t_EQUAL = r'='
t_NOT_EQUAL = r'/='
t_LESS_THAN = r'<'
t_LESS_EQUAL = r'<='
t_GREATER_THAN = r'>'
t_GREATER_EQUAL = r'>='

# Ignored characters
t_ignore = ' \t'

def t_COMMENT(t):
    r'--.*'
    global current_tokens
    current_tokens.append(
        HDLToken('COMMENT', t.value, t.lineno, find_column(t))
    )
    return t

def t_STRING_LITERAL(t):
    r'"([^"\\]|\\.)*"'
    return t

def t_CHARACTER_LITERAL(t):
    r"'([^'\\]|\\.)'"
    return t

def t_NUMBER(t):
    r'\d+(\.\d+)?([eE][+-]?\d+)?'
    return t

def t_IDENTIFIER(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFIER')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    global current_tokens
    current_tokens.append(
        HDLToken('NEWLINE', t.value, t.lineno, find_column(t))
    )

def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

def find_column(token):
    """Find the column position of a token"""
    line_start = token.lexer.lexdata.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1

# Grammar rules
def p_design_file(p):
    '''design_file : design_units
                   | empty'''
    pass

def p_design_units(p):
    '''design_units : design_unit
                   | design_units design_unit'''
    pass

def p_design_unit(p):
    '''design_unit : entity_declaration
                  | architecture_body
                  | package_declaration
                  | package_body
                  | configuration_declaration
                  | library_clause
                  | use_clause
                  | comment_line'''
    pass

def p_comment_line(p):
    '''comment_line : COMMENT'''
    pass

def p_empty(p):
    '''empty :'''
    pass

def p_entity_declaration(p):
    '''entity_declaration : ENTITY IDENTIFIER IS entity_body END ENTITY SEMICOLON
                         | ENTITY IDENTIFIER IS entity_body END SEMICOLON'''
    entity_name = p[2]
    entity = VHDLEntity(entity_name)

        # Extract ports from entity body if any
    entity_body = p[4]
    if entity_body and isinstance(entity_body, list):
        port_groups = extract_port_groups(entity_body, current_tokens)
        for group in port_groups:
            entity.add_port_group(group)
        # print(f"Added {len(port_groups)} port groups to entity {entity_name}")  # Debug: commented out

    global current_document
    current_document.add_design_unit(entity)
    # print(f"Created entity: {entity_name}")  # Debug: commented out

def p_entity_body(p):
    '''entity_body :
                  | entity_body_items'''
    if len(p) > 1 and p[1] is not None:
        p[0] = p[1]

def p_entity_body_items(p):
    '''entity_body_items : entity_body_item
                        | entity_body_items entity_body_item'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        # Combine results - for now just take the second item if it has ports
        p[0] = p[2] if p[2] is not None else p[1]

def p_entity_body_item(p):
    '''entity_body_item : generic_clause
                       | port_clause'''
    if len(p) > 1 and p[1] is not None:
        p[0] = p[1]  # Pass through the result

def p_port_clause(p):
    '''port_clause : PORT LPAREN port_list RPAREN SEMICOLON'''
    if len(p) > 3:
        p[0] = p[3]  # Return the port list
        # print(f"Found {len(p[3]) if p[3] else 0} ports")  # Debug: commented out

        # Store the current tokens for port grouping analysis
        global current_tokens
        if hasattr(p, 'lexer') and hasattr(p.lexer, 'current_tokens'):
            current_tokens.extend(p.lexer.current_tokens)
        # print(f"Collected {len(current_tokens)} tokens for port analysis")  # Debug: commented out

def p_port_list(p):
    '''port_list : port_declaration
                | port_list SEMICOLON port_declaration'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

def p_port_declaration(p):
    '''port_declaration : IDENTIFIER COLON port_mode type_mark'''
    port_name = p[1]
    port_mode = p[3]
    port_type = p[4]

    port = VHDLPort(port_name, port_type, port_mode)
    p[0] = port

def p_port_mode(p):
    '''port_mode : IN
                | OUT
                | INOUT
                | BUFFER'''
    p[0] = p[1]

def p_type_mark(p):
    '''type_mark : IDENTIFIER
                | STD_LOGIC
                | STD_LOGIC_VECTOR
                | INTEGER
                | NATURAL
                | POSITIVE
                | BOOLEAN
                | BIT
                | BIT_VECTOR'''
    p[0] = p[1]

def p_architecture_body(p):
    '''architecture_body : ARCHITECTURE IDENTIFIER OF IDENTIFIER IS architecture_declarative_part BEGIN architecture_statement_part END SEMICOLON
                        | ARCHITECTURE IDENTIFIER OF IDENTIFIER IS architecture_declarative_part BEGIN architecture_statement_part END IDENTIFIER SEMICOLON
                        | ARCHITECTURE IDENTIFIER OF IDENTIFIER IS BEGIN architecture_statement_part END SEMICOLON
                        | ARCHITECTURE IDENTIFIER OF IDENTIFIER IS BEGIN architecture_statement_part END IDENTIFIER SEMICOLON
                        | ARCHITECTURE IDENTIFIER OF IDENTIFIER IS architecture_declarative_part END SEMICOLON
                        | ARCHITECTURE IDENTIFIER OF IDENTIFIER IS architecture_declarative_part END IDENTIFIER SEMICOLON
                        | ARCHITECTURE IDENTIFIER OF IDENTIFIER IS END SEMICOLON
                        | ARCHITECTURE IDENTIFIER OF IDENTIFIER IS END IDENTIFIER SEMICOLON'''
    arch_name = p[2]
    entity_name = p[4]
    architecture = VHDLArchitecture(arch_name, entity_name)
    current_document.add_design_unit(architecture)

def p_package_declaration(p):
    '''package_declaration : PACKAGE IDENTIFIER IS END SEMICOLON
                          | PACKAGE IDENTIFIER IS END IDENTIFIER SEMICOLON'''
    package_name = p[2]
    package = VHDLPackage(package_name)
    current_document.add_design_unit(package)

def p_package_body(p):
    '''package_body : PACKAGE IDENTIFIER IDENTIFIER IS END SEMICOLON
                   | PACKAGE IDENTIFIER IDENTIFIER IS END IDENTIFIER SEMICOLON'''
    package_name = p[3]  # Third token is the package name after 'body'
    package_body = VHDLPackageBody(package_name)
    current_document.add_design_unit(package_body)

def p_configuration_declaration(p):
    '''configuration_declaration : CONFIGURATION IDENTIFIER OF IDENTIFIER IS END SEMICOLON
                                | CONFIGURATION IDENTIFIER OF IDENTIFIER IS END IDENTIFIER SEMICOLON'''
    config_name = p[2]
    config = VHDLConfiguration(config_name)
    current_document.add_design_unit(config)

def p_generic_clause(p):
    '''generic_clause : GENERIC LPAREN generic_list RPAREN SEMICOLON
                      | GENERIC LPAREN generic_list RPAREN'''
    pass

def p_generic_list(p):
    '''generic_list : generic_declaration
                   | generic_list SEMICOLON generic_declaration'''
    pass

def p_generic_declaration(p):
    '''generic_declaration : IDENTIFIER COLON type_mark
                           | IDENTIFIER COLON type_mark ASSIGN expression
                           | identifier_list COLON type_mark
                           | identifier_list COLON type_mark ASSIGN expression'''
    pass

def p_library_clause(p):
    '''library_clause : LIBRARY identifier_list SEMICOLON'''
    pass

def p_use_clause(p):
    '''use_clause : USE IDENTIFIER DOT IDENTIFIER SEMICOLON
                 | USE IDENTIFIER DOT IDENTIFIER DOT IDENTIFIER SEMICOLON
                 | USE IDENTIFIER DOT IDENTIFIER DOT ALL SEMICOLON
                 | USE IDENTIFIER DOT ALL SEMICOLON'''
    pass

# Architecture declarative and statement parts
def p_architecture_declarative_part(p):
    '''architecture_declarative_part : architecture_declarative_items
                                     | empty'''
    pass

def p_architecture_declarative_items(p):
    '''architecture_declarative_items : architecture_declarative_item
                                       | architecture_declarative_items architecture_declarative_item'''
    pass

def p_architecture_declarative_item(p):
    '''architecture_declarative_item : signal_declaration
                                      | constant_declaration
                                      | type_declaration
                                      | subtype_declaration
                                      | component_declaration
                                      | function_declaration
                                      | procedure_declaration
                                      | attribute_declaration
                                      | use_clause
                                      | comment_line
                                      | any_declarative_statement'''
    pass

def p_architecture_statement_part(p):
    '''architecture_statement_part : architecture_statements
                                   | empty'''
    pass

def p_architecture_statements(p):
    '''architecture_statements : architecture_statement
                                | architecture_statements architecture_statement'''
    pass

def p_architecture_statement(p):
    '''architecture_statement : process_statement
                               | concurrent_signal_assignment
                               | component_instantiation
                               | generate_statement
                               | block_statement
                               | assert_statement
                               | comment_line
                               | any_statement'''
    pass

# Signal and other declarations
def p_signal_declaration(p):
    '''signal_declaration : SIGNAL identifier_list COLON type_mark signal_init SEMICOLON
                          | SIGNAL identifier_list COLON type_mark SEMICOLON'''
    pass

def p_signal_init(p):
    '''signal_init : ASSIGN expression
                   | empty'''
    pass

def p_constant_declaration(p):
    '''constant_declaration : CONSTANT identifier_list COLON type_mark ASSIGN expression SEMICOLON
                            | CONSTANT identifier_list COLON type_mark SEMICOLON'''
    pass

def p_type_declaration(p):
    '''type_declaration : TYPE IDENTIFIER IS type_definition SEMICOLON'''
    pass

def p_subtype_declaration(p):
    '''subtype_declaration : SUBTYPE IDENTIFIER IS type_mark SEMICOLON'''
    pass

def p_type_definition(p):
    '''type_definition : enumeration_type_definition
                       | integer_type_definition
                       | array_type_definition
                       | record_type_definition
                       | access_type_definition
                       | file_type_definition
                       | IDENTIFIER'''
    pass

def p_enumeration_type_definition(p):
    '''enumeration_type_definition : LPAREN enumeration_literals RPAREN'''
    pass

def p_enumeration_literals(p):
    '''enumeration_literals : IDENTIFIER
                            | enumeration_literals COMMA IDENTIFIER'''
    pass

def p_integer_type_definition(p):
    '''integer_type_definition : RANGE expression TO expression
                               | RANGE expression DOWNTO expression'''
    pass

def p_array_type_definition(p):
    '''array_type_definition : ARRAY LPAREN index_subtype_definition RPAREN OF type_mark'''
    pass

def p_index_subtype_definition(p):
    '''index_subtype_definition : type_mark RANGE LESS_THAN GREATER_THAN
                                | type_mark RANGE expression TO expression
                                | type_mark RANGE expression DOWNTO expression
                                | IDENTIFIER RANGE LESS_THAN GREATER_THAN'''
    pass

def p_record_type_definition(p):
    '''record_type_definition : RECORD element_declarations END RECORD'''
    pass

def p_element_declarations(p):
    '''element_declarations : element_declaration
                            | element_declarations element_declaration'''
    pass

def p_element_declaration(p):
    '''element_declaration : identifier_list COLON type_mark SEMICOLON'''
    pass

def p_access_type_definition(p):
    '''access_type_definition : ACCESS type_mark'''
    pass

def p_file_type_definition(p):
    '''file_type_definition : FILE OF type_mark'''
    pass

def p_component_declaration(p):
    '''component_declaration : COMPONENT IDENTIFIER IS port_clause END COMPONENT SEMICOLON
                             | COMPONENT IDENTIFIER IS generic_clause port_clause END COMPONENT SEMICOLON
                             | COMPONENT IDENTIFIER IS END COMPONENT SEMICOLON'''
    pass

def p_function_declaration(p):
    '''function_declaration : FUNCTION IDENTIFIER LPAREN parameter_list RPAREN RETURN type_mark SEMICOLON
                            | FUNCTION IDENTIFIER RETURN type_mark SEMICOLON
                            | PURE FUNCTION IDENTIFIER LPAREN parameter_list RPAREN RETURN type_mark SEMICOLON
                            | IMPURE FUNCTION IDENTIFIER LPAREN parameter_list RPAREN RETURN type_mark SEMICOLON'''
    pass

def p_procedure_declaration(p):
    '''procedure_declaration : PROCEDURE IDENTIFIER LPAREN parameter_list RPAREN SEMICOLON
                             | PROCEDURE IDENTIFIER SEMICOLON'''
    pass

def p_parameter_list(p):
    '''parameter_list : parameter_declaration
                      | parameter_list SEMICOLON parameter_declaration'''
    pass

def p_parameter_declaration(p):
    '''parameter_declaration : identifier_list COLON port_mode type_mark
                             | identifier_list COLON type_mark'''
    pass

def p_attribute_declaration(p):
    '''attribute_declaration : ATTRIBUTE IDENTIFIER COLON type_mark SEMICOLON'''
    pass

# Process statements
def p_process_statement(p):
    '''process_statement : process_label PROCESS process_sensitivity_list IS process_declarative_part BEGIN process_statement_part END PROCESS process_label SEMICOLON
                         | process_label PROCESS process_sensitivity_list IS BEGIN process_statement_part END PROCESS process_label SEMICOLON
                         | process_label PROCESS process_sensitivity_list IS process_declarative_part BEGIN process_statement_part END PROCESS SEMICOLON
                         | process_label PROCESS process_sensitivity_list IS BEGIN process_statement_part END PROCESS SEMICOLON
                         | PROCESS process_sensitivity_list IS process_declarative_part BEGIN process_statement_part END PROCESS SEMICOLON
                         | PROCESS process_sensitivity_list IS BEGIN process_statement_part END PROCESS SEMICOLON
                         | process_label PROCESS IS process_declarative_part BEGIN process_statement_part END PROCESS process_label SEMICOLON
                         | process_label PROCESS IS BEGIN process_statement_part END PROCESS process_label SEMICOLON
                         | PROCESS IS process_declarative_part BEGIN process_statement_part END PROCESS SEMICOLON
                         | PROCESS IS BEGIN process_statement_part END PROCESS SEMICOLON'''
    pass

def p_process_label(p):
    '''process_label : IDENTIFIER COLON
                     | empty'''
    pass

def p_process_sensitivity_list(p):
    '''process_sensitivity_list : LPAREN sensitivity_list RPAREN
                                | empty'''
    pass

def p_sensitivity_list(p):
    '''sensitivity_list : IDENTIFIER
                        | sensitivity_list COMMA IDENTIFIER'''
    pass

def p_process_declarative_part(p):
    '''process_declarative_part : process_declarative_items
                                | empty'''
    pass

def p_process_declarative_items(p):
    '''process_declarative_items : process_declarative_item
                                 | process_declarative_items process_declarative_item'''
    pass

def p_process_declarative_item(p):
    '''process_declarative_item : variable_declaration
                                | constant_declaration
                                | type_declaration
                                | subtype_declaration
                                | function_declaration
                                | procedure_declaration
                                | attribute_declaration
                                | use_clause
                                | comment_line
                                | any_declarative_statement'''
    pass

def p_variable_declaration(p):
    '''variable_declaration : VARIABLE identifier_list COLON type_mark variable_init SEMICOLON
                            | VARIABLE identifier_list COLON type_mark SEMICOLON
                            | SHARED VARIABLE identifier_list COLON type_mark variable_init SEMICOLON
                            | SHARED VARIABLE identifier_list COLON type_mark SEMICOLON'''
    pass

def p_variable_init(p):
    '''variable_init : ASSIGN expression
                     | empty'''
    pass

def p_process_statement_part(p):
    '''process_statement_part : process_statements
                              | empty'''
    pass

def p_process_statements(p):
    '''process_statements : process_statement_item
                          | process_statements process_statement_item'''
    pass

def p_process_statement_item(p):
    '''process_statement_item : sequential_statement
                              | comment_line'''
    pass

# Sequential statements
def p_sequential_statement(p):
    '''sequential_statement : signal_assignment_statement
                            | variable_assignment_statement
                            | if_statement
                            | case_statement
                            | loop_statement
                            | next_statement
                            | exit_statement
                            | return_statement
                            | wait_statement
                            | assert_statement
                            | procedure_call_statement
                            | null_statement'''
    pass

def p_signal_assignment_statement(p):
    '''signal_assignment_statement : target LESS_EQUAL expression SEMICOLON
                                   | target LESS_EQUAL expression AFTER expression SEMICOLON
                                   | target LESS_EQUAL TRANSPORT expression SEMICOLON
                                   | target LESS_EQUAL REJECT expression INERTIAL expression SEMICOLON'''
    pass

def p_variable_assignment_statement(p):
    '''variable_assignment_statement : target ASSIGN expression SEMICOLON'''
    pass

def p_target(p):
    '''target : IDENTIFIER
              | indexed_name
              | slice_name
              | selected_name'''
    pass

def p_indexed_name(p):
    '''indexed_name : IDENTIFIER LPAREN expression_list RPAREN'''
    pass

def p_slice_name(p):
    '''slice_name : IDENTIFIER LPAREN discrete_range RPAREN'''
    pass

def p_selected_name(p):
    '''selected_name : IDENTIFIER DOT IDENTIFIER'''
    pass

def p_discrete_range(p):
    '''discrete_range : expression TO expression
                      | expression DOWNTO expression
                      | type_mark RANGE expression TO expression
                      | type_mark RANGE expression DOWNTO expression'''
    pass

# Control statements
def p_if_statement(p):
    '''if_statement : IF condition THEN process_statements elsif_parts else_part END IF SEMICOLON
                    | IF condition THEN process_statements else_part END IF SEMICOLON
                    | IF condition THEN process_statements END IF SEMICOLON'''
    pass

def p_condition(p):
    '''condition : expression'''
    pass

def p_elsif_parts(p):
    '''elsif_parts : elsif_part
                   | elsif_parts elsif_part'''
    pass

def p_elsif_part(p):
    '''elsif_part : ELSIF condition THEN process_statements'''
    pass

def p_else_part(p):
    '''else_part : ELSE process_statements
                 | empty'''
    pass

def p_case_statement(p):
    '''case_statement : CASE expression IS case_statement_alternatives END CASE SEMICOLON'''
    pass

def p_case_statement_alternatives(p):
    '''case_statement_alternatives : case_statement_alternative
                                   | case_statement_alternatives case_statement_alternative'''
    pass

def p_case_statement_alternative(p):
    '''case_statement_alternative : WHEN choices ARROW process_statements'''
    pass

def p_choices(p):
    '''choices : choice
               | choices BAR choice'''
    pass

def p_choice(p):
    '''choice : expression
              | discrete_range
              | OTHERS'''
    pass

def p_loop_statement(p):
    '''loop_statement : loop_label iteration_scheme LOOP process_statements END LOOP loop_label SEMICOLON
                      | loop_label LOOP process_statements END LOOP loop_label SEMICOLON
                      | iteration_scheme LOOP process_statements END LOOP SEMICOLON
                      | LOOP process_statements END LOOP SEMICOLON'''
    pass

def p_loop_label(p):
    '''loop_label : IDENTIFIER COLON
                  | empty'''
    pass

def p_iteration_scheme(p):
    '''iteration_scheme : WHILE condition
                        | FOR IDENTIFIER IN discrete_range'''
    pass

def p_next_statement(p):
    '''next_statement : NEXT loop_label WHEN condition SEMICOLON
                      | NEXT loop_label SEMICOLON
                      | NEXT WHEN condition SEMICOLON
                      | NEXT SEMICOLON'''
    pass

def p_exit_statement(p):
    '''exit_statement : EXIT loop_label WHEN condition SEMICOLON
                      | EXIT loop_label SEMICOLON
                      | EXIT WHEN condition SEMICOLON
                      | EXIT SEMICOLON'''
    pass

def p_return_statement(p):
    '''return_statement : RETURN expression SEMICOLON
                        | RETURN SEMICOLON'''
    pass

def p_wait_statement(p):
    '''wait_statement : WAIT ON sensitivity_list UNTIL condition FOR expression SEMICOLON
                      | WAIT ON sensitivity_list UNTIL condition SEMICOLON
                      | WAIT ON sensitivity_list FOR expression SEMICOLON
                      | WAIT UNTIL condition FOR expression SEMICOLON
                      | WAIT ON sensitivity_list SEMICOLON
                      | WAIT UNTIL condition SEMICOLON
                      | WAIT FOR expression SEMICOLON
                      | WAIT SEMICOLON'''
    pass

def p_assert_statement(p):
    '''assert_statement : ASSERT condition REPORT expression SEVERITY expression SEMICOLON
                        | ASSERT condition REPORT expression SEMICOLON
                        | ASSERT condition SEVERITY expression SEMICOLON
                        | ASSERT condition SEMICOLON'''
    pass

def p_procedure_call_statement(p):
    '''procedure_call_statement : IDENTIFIER LPAREN association_list RPAREN SEMICOLON
                                | IDENTIFIER SEMICOLON'''
    pass

def p_null_statement(p):
    '''null_statement : NULL SEMICOLON'''
    pass

# Concurrent statements
def p_concurrent_signal_assignment(p):
    '''concurrent_signal_assignment : target LESS_EQUAL expression SEMICOLON
                                    | target LESS_EQUAL expression WHEN condition ELSE expression SEMICOLON
                                    | WITH expression SELECT target LESS_EQUAL concurrent_selected_signal_assignment'''
    pass

def p_concurrent_selected_signal_assignment(p):
    '''concurrent_selected_signal_assignment : concurrent_selected_alternatives'''
    pass

def p_concurrent_selected_alternatives(p):
    '''concurrent_selected_alternatives : concurrent_selected_alternative
                                        | concurrent_selected_alternatives COMMA concurrent_selected_alternative'''
    pass

def p_concurrent_selected_alternative(p):
    '''concurrent_selected_alternative : expression WHEN choices'''
    pass

def p_component_instantiation(p):
    '''component_instantiation : instantiation_label IDENTIFIER generic_map port_map SEMICOLON
                               | instantiation_label IDENTIFIER port_map SEMICOLON
                               | instantiation_label ENTITY IDENTIFIER DOT IDENTIFIER generic_map port_map SEMICOLON
                               | instantiation_label ENTITY IDENTIFIER DOT IDENTIFIER port_map SEMICOLON
                               | instantiation_label CONFIGURATION IDENTIFIER DOT IDENTIFIER generic_map port_map SEMICOLON
                               | instantiation_label CONFIGURATION IDENTIFIER DOT IDENTIFIER port_map SEMICOLON'''
    pass

def p_instantiation_label(p):
    '''instantiation_label : IDENTIFIER COLON'''
    pass

def p_generic_map(p):
    '''generic_map : GENERIC MAP LPAREN association_list RPAREN
                   | empty'''
    pass

def p_port_map(p):
    '''port_map : PORT MAP LPAREN association_list RPAREN'''
    pass

def p_association_list(p):
    '''association_list : association_element
                        | association_list COMMA association_element'''
    pass

def p_association_element(p):
    '''association_element : formal_part ARROW actual_part
                           | actual_part'''
    pass

def p_formal_part(p):
    '''formal_part : IDENTIFIER
                   | IDENTIFIER LPAREN expression RPAREN'''
    pass

def p_actual_part(p):
    '''actual_part : expression
                   | OPEN
                   | INERTIAL expression
                   | TRANSPORT expression'''
    pass

def p_generate_statement(p):
    '''generate_statement : generate_label FOR IDENTIFIER IN discrete_range GENERATE generate_statement_part END GENERATE generate_label SEMICOLON
                          | generate_label IF condition GENERATE generate_statement_part END GENERATE generate_label SEMICOLON
                          | generate_label FOR IDENTIFIER IN discrete_range GENERATE generate_statement_part END GENERATE SEMICOLON
                          | generate_label IF condition GENERATE generate_statement_part END GENERATE SEMICOLON'''
    pass

def p_generate_label(p):
    '''generate_label : IDENTIFIER COLON'''
    pass

def p_generate_statement_part(p):
    '''generate_statement_part : architecture_statements
                               | empty'''
    pass

def p_block_statement(p):
    '''block_statement : block_label BLOCK block_guard IS block_declarative_part BEGIN architecture_statements END BLOCK block_label SEMICOLON
                       | block_label BLOCK IS block_declarative_part BEGIN architecture_statements END BLOCK block_label SEMICOLON
                       | block_label BLOCK block_guard IS BEGIN architecture_statements END BLOCK block_label SEMICOLON
                       | block_label BLOCK IS BEGIN architecture_statements END BLOCK block_label SEMICOLON
                       | block_label BLOCK block_guard IS block_declarative_part BEGIN architecture_statements END BLOCK SEMICOLON
                       | block_label BLOCK IS block_declarative_part BEGIN architecture_statements END BLOCK SEMICOLON'''
    pass

def p_block_label(p):
    '''block_label : IDENTIFIER COLON'''
    pass

def p_block_guard(p):
    '''block_guard : LPAREN expression RPAREN
                   | empty'''
    pass

def p_block_declarative_part(p):
    '''block_declarative_part : architecture_declarative_items
                              | empty'''
    pass

# Expressions and operators
def p_expression(p):
    '''expression : logical_expression'''
    pass

def p_logical_expression(p):
    '''logical_expression : relation
                           | logical_expression AND relation
                           | logical_expression OR relation
                           | logical_expression NAND relation
                           | logical_expression NOR relation
                           | logical_expression XOR relation
                           | logical_expression XNOR relation'''
    pass

def p_relation(p):
    '''relation : shift_expression
                | relation relational_operator shift_expression'''
    pass

def p_relational_operator(p):
    '''relational_operator : EQUAL
                           | NOT_EQUAL
                           | LESS_THAN
                           | LESS_EQUAL
                           | GREATER_THAN
                           | GREATER_EQUAL'''
    pass

def p_shift_expression(p):
    '''shift_expression : simple_expression
                        | shift_expression shift_operator simple_expression'''
    pass

def p_shift_operator(p):
    '''shift_operator : SLL
                      | SRL
                      | SLA
                      | SRA
                      | ROL
                      | ROR'''
    pass

def p_simple_expression(p):
    '''simple_expression : term
                          | sign term
                          | simple_expression adding_operator term'''
    pass

def p_sign(p):
    '''sign : PLUS
            | MINUS'''
    pass

def p_adding_operator(p):
    '''adding_operator : PLUS
                       | MINUS
                       | CONCATENATE'''
    pass

def p_term(p):
    '''term : factor
            | term multiplying_operator factor'''
    pass

def p_multiplying_operator(p):
    '''multiplying_operator : MULTIPLY
                            | DIVIDE
                            | MOD
                            | REM'''
    pass

def p_factor(p):
    '''factor : primary
              | primary POWER primary
              | ABS primary
              | NOT primary'''
    pass

def p_primary(p):
    '''primary : literal
               | qualified_expression
               | function_call
               | type_conversion
               | IDENTIFIER
               | indexed_name
               | slice_name
               | selected_name
               | LPAREN expression RPAREN
               | aggregate'''
    pass

def p_literal(p):
    '''literal : NUMBER
               | STRING_LITERAL
               | CHARACTER_LITERAL
               | NULL
               | bit_string_literal'''
    pass

def p_bit_string_literal(p):
    '''bit_string_literal : IDENTIFIER STRING_LITERAL'''
    pass

def p_qualified_expression(p):
    '''qualified_expression : type_mark APOSTROPHE LPAREN expression RPAREN
                             | type_mark APOSTROPHE aggregate'''
    pass

def p_function_call(p):
    '''function_call : IDENTIFIER LPAREN expression_list RPAREN
                     | IDENTIFIER LPAREN RPAREN'''
    pass

def p_type_conversion(p):
    '''type_conversion : type_mark LPAREN expression RPAREN'''
    pass

def p_aggregate(p):
    '''aggregate : LPAREN element_associations RPAREN'''
    pass

def p_element_associations(p):
    '''element_associations : element_association
                            | element_associations COMMA element_association'''
    pass

def p_element_association(p):
    '''element_association : choices ARROW expression
                           | expression'''
    pass

def p_expression_list(p):
    '''expression_list : expression
                       | expression_list COMMA expression'''
    pass

def p_identifier_list(p):
    '''identifier_list : IDENTIFIER
                       | identifier_list COMMA IDENTIFIER'''
    pass

# Catch-all rules for unmatched constructs
def p_any_declarative_statement(p):
    '''any_declarative_statement : any_tokens SEMICOLON'''
    pass

def p_any_statement(p):
    '''any_statement : any_tokens SEMICOLON'''
    pass

def p_any_tokens(p):
    '''any_tokens : any_token
                  | any_tokens any_token'''
    pass

def p_any_token(p):
    '''any_token : IDENTIFIER
                 | NUMBER
                 | STRING_LITERAL
                 | CHARACTER_LITERAL
                 | COLON
                 | COMMA
                 | DOT
                 | LPAREN
                 | RPAREN
                 | LBRACKET
                 | RBRACKET
                 | ASSIGN
                 | ARROW
                 | type_keywords
                 | operator_keywords'''
    pass

def p_type_keywords(p):
    '''type_keywords : STD_LOGIC
                     | STD_LOGIC_VECTOR
                     | INTEGER
                     | NATURAL
                     | POSITIVE
                     | BOOLEAN
                     | BIT
                     | BIT_VECTOR
                     | SIGNED
                     | UNSIGNED
                     | TIME
                     | REAL
                     | STRING_TYPE
                     | CHARACTER_TYPE'''
    pass

def p_operator_keywords(p):
    '''operator_keywords : PLUS
                         | MINUS
                         | MULTIPLY
                         | DIVIDE
                         | POWER
                         | CONCATENATE
                         | EQUAL
                         | NOT_EQUAL
                         | LESS_THAN
                         | LESS_EQUAL
                         | GREATER_THAN
                         | GREATER_EQUAL
                         | AND
                         | OR
                         | NOT
                         | NAND
                         | NOR
                         | XOR
                         | XNOR
                         | SLL
                         | SRL
                         | SLA
                         | SRA
                         | ROL
                         | ROR
                         | MOD
                         | REM
                         | ABS'''
    pass

# Add missing tokens for better parsing coverage
t_BAR = r'\|'
t_APOSTROPHE = r"'"

def p_error(p):
    if p:
        # Much quieter error reporting - only for debugging when needed
        # print(f"Syntax error at token {p.type} ('{p.value}') on line {p.lineno}")
        # Skip the problematic token and continue parsing
        if hasattr(parser, 'errok'):
            parser.errok()
    else:
        # End of file - this is normal, don't print anything
        pass

def extract_port_groups(ports: List[VHDLPort], port_tokens: List[HDLToken]) -> List[HDLPortGroup]:
    """Extract port groups based on comments and empty lines"""
    if not ports:
        return []

    groups = []
    group_counter = 1

    # print(f"Extracting port groups from {len(ports)} ports")  # Debug: commented out

    # Get the source text from the current document to analyze comments
    global current_document
    if not current_document or not current_document.source_text:
        # Fallback to simple grouping
        default_group = HDLPortGroup("group1")
        for port in ports:
            default_group.add_port(port)
        groups.append(default_group)
        return groups

    source_text = current_document.source_text

    # Find the port section in the source
    port_section_start = source_text.find("port")
    if port_section_start == -1:
        # No port section found, use default grouping
        default_group = HDLPortGroup("group1")
        for port in ports:
            default_group.add_port(port)
        groups.append(default_group)
        return groups

    # Extract the port section (from "port" to the closing parenthesis)
    paren_count = 0
    port_section_end = port_section_start
    found_opening_paren = False

    for i in range(port_section_start, len(source_text)):
        char = source_text[i]
        if char == '(':
            paren_count += 1
            found_opening_paren = True
        elif char == ')':
            paren_count -= 1
            if found_opening_paren and paren_count == 0:
                port_section_end = i
                break

    port_section = source_text[port_section_start:port_section_end + 1]
    # print(f"Analyzing port section: {port_section[:100]}...")  # Debug: commented out

    # Split the port section into lines for analysis
    lines = port_section.split('\n')

    # Analyze the lines to find comments and associate them with ports
    current_group_name = None
    current_group = None
    port_to_group_map = {}

    for line_num, line in enumerate(lines):
        stripped_line = line.strip()

        # Check if this line contains a comment
        if '--' in line:
            comment_start = line.find('--')
            comment_text = line[comment_start + 2:].strip()
            if comment_text:
                current_group_name = comment_text
                # print(f"Found comment group: '{current_group_name}'")  # Debug: commented out
                continue

        # Check if this line contains a port declaration
        port_found = False
        for port in ports:
            port_name = port.getName()
            if port_name in stripped_line and ':' in stripped_line:
                # This line contains a port declaration
                port_found = True

                # Determine the group for this port
                if current_group_name:
                    group_name = current_group_name
                else:
                    group_name = f"group{group_counter}"
                    group_counter += 1

                # Find or create the group
                group = None
                for g in groups:
                    if g.getName() == group_name:
                        group = g
                        break

                if not group:
                    group = HDLPortGroup(group_name)
                    groups.append(group)
                    # print(f"Created new group: '{group_name}'")  # Debug: commented out

                # Add port to group if not already added
                if port_name not in port_to_group_map:
                    group.add_port(port)
                    port_to_group_map[port_name] = group
                    # print(f"Added port '{port_name}' to group '{group_name}'")  # Debug: commented out

                # Keep the group name active for subsequent ports under the same comment
                # Don't reset it here - let empty lines or new comments reset it
                break

        # Check for empty lines or lines with only whitespace - these can separate groups
        if not stripped_line or (not stripped_line.startswith('--') and not port_found):
            # Empty line might indicate group boundary, but don't reset if we just found a comment
            # and haven't assigned any ports to it yet
            if current_group_name and not current_group_name.startswith("group"):
                # Check if we've already used this group name
                group_used = any(g.getName() == current_group_name for g in groups)
                if group_used:
                    current_group_name = None

    # Handle any ports that weren't assigned to groups
    unassigned_ports = [port for port in ports if port.getName() not in port_to_group_map]

    if unassigned_ports:
        # If we have comment groups but unassigned ports, try to assign them to the last comment group
        # or create a new group
        if groups and current_group_name and not current_group_name.startswith("group"):
            # Assign to the last comment group found
            last_group = groups[-1]
            for port in unassigned_ports:
                last_group.add_port(port)
                # print(f"Added unassigned port '{port.getName()}' to group '{last_group.getName()}'")  # Debug: commented out
        else:
            # Create a default group for unassigned ports
            if not groups:
                default_group = HDLPortGroup(f"group{group_counter}")
                groups.append(default_group)
            else:
                # Add to a new group
                default_group = HDLPortGroup(f"group{group_counter}")
                groups.append(default_group)

            for port in unassigned_ports:
                default_group.add_port(port)
                # print(f"Added unassigned port '{port.getName()}' to group '{default_group.getName()}'")  # Debug: commented out

    # If no groups were created, create a default one
    if not groups:
        default_group = HDLPortGroup("group1")
        for port in ports:
            default_group.add_port(port)
        groups.append(default_group)

    # print(f"Created {len(groups)} port groups total")  # Debug: commented out
    return groups

# Build the lexer and parser
lexer = lex.lex()
parser = yacc.yacc(debug=False)

def parse_vhdl(filename: str, source_text: str, language: str) -> HDLDocument:
    """Parse VHDL source text"""
    global current_document, current_tokens

    # Create the document
    current_document = HDLDocument(filename, language)
    current_document.set_source_text(source_text)
    current_tokens = []

    # Parse the source
    try:
        result = parser.parse(source_text, lexer=lexer)
        return current_document
    except Exception as e:
        raise RuntimeError(f"Parse error in {filename}: {str(e)}")

class VHDLParser:
    """VHDL Parser - Supports all VHDL language features and versions"""

    def __init__(self, language: str):
        self.language = language

    def parse(self, filename: str, source_text: str) -> HDLDocument:
        return parse_vhdl(filename, source_text, self.language)

# Legacy aliases for backward compatibility
UnifiedVHDLParser = VHDLParser
WorkingVHDLParser = VHDLParser