"""
Verilog Parser implementation using PLY
(Currently a basic implementation - can be expanded with full Verilog grammar)
"""

from typing import List, Dict, Any, Optional
from .base_parser import BaseHDLParser
from ..verilog import VerilogModule, VerilogPort
from ..base import HDLToken, HDLPortGroup

import ply.lex as lex
import ply.yacc as yacc


class VerilogParser(BaseHDLParser):
    """Verilog Parser using PLY"""

    # Basic Verilog tokens
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
        'NEWLINE',
        'WHITESPACE',

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
        'FOR',
        'WHILE',
        'ALWAYS',
        'INITIAL',
        'POSEDGE',
        'NEGEDGE'
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
        'for': 'FOR',
        'while': 'WHILE',
        'always': 'ALWAYS',
        'initial': 'INITIAL',
        'posedge': 'POSEDGE',
        'negedge': 'NEGEDGE'
    }

    def __init__(self, language: str):
        self.current_tokens = []
        super().__init__(language)

    def _setup_lexer(self):
        """Setup Verilog lexer"""

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
        t_ASSIGN = r'='

        def t_COMMENT_BLOCK(t):
            r'/\*(.|\n)*?\*/'
            t.lexer.lineno += t.value.count('\n')
            self.current_tokens.append(
                HDLToken('COMMENT_BLOCK', t.value, t.lineno, self._find_column(t))
            )
            return t

        def t_COMMENT_LINE(t):
            r'//.*'
            self.current_tokens.append(
                HDLToken('COMMENT_LINE', t.value, t.lineno, self._find_column(t))
            )
            return t

        def t_STRING_LITERAL(t):
            r'"([^"\\]|\\.)*"'
            return t

        def t_NUMBER(t):
            r'\d+(\.\d+)?([eE][+-]?\d+)?'
            return t

        def t_IDENTIFIER(t):
            r'[a-zA-Z_][a-zA-Z_0-9]*'
            t.type = self.reserved.get(t.value.lower(), 'IDENTIFIER')
            return t

        def t_NEWLINE(t):
            r'\n+'
            t.lexer.lineno += len(t.value)
            self.current_tokens.append(
                HDLToken('NEWLINE', t.value, t.lineno, self._find_column(t))
            )
            return t

        def t_WHITESPACE(t):
            r'[ \t]+'
            self.current_tokens.append(
                HDLToken('WHITESPACE', t.value, t.lineno, self._find_column(t))
            )
            return t

        def t_error(t):
            print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
            t.lexer.skip(1)

        self.lexer = lex.lex(module=self)

    def _setup_parser(self):
        """Setup Verilog parser"""

        # Basic grammar rules for Verilog
        def p_source_text(p):
            '''source_text : description_list'''
            pass

        def p_description_list(p):
            '''description_list : description
                               | description_list description'''
            pass

        def p_description(p):
            '''description : module_declaration'''
            pass

        def p_module_declaration(p):
            '''module_declaration : MODULE IDENTIFIER LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE'''
            module_name = p[2]
            module = VerilogModule(module_name)

            # Extract ports
            if len(p) > 4 and p[4]:
                port_groups = self.extract_port_groups(p[4], self.current_tokens)
                for group in port_groups:
                    module.add_port_group(group)

            self.current_document.add_design_unit(module)

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
                p[0] = p[1] + [p[3]]

        def p_port(p):
            '''port : IDENTIFIER'''
            # Simple port for now - can be expanded
            port = VerilogPort(p[1], "wire", "")
            p[0] = port

        def p_module_items(p):
            '''module_items :
                           | module_items module_item'''
            pass

        def p_module_item(p):
            '''module_item : port_declaration
                          | parameter_declaration'''
            pass

        def p_port_declaration(p):
            '''port_declaration : INPUT range IDENTIFIER SEMICOLON
                               | OUTPUT range IDENTIFIER SEMICOLON
                               | INOUT range IDENTIFIER SEMICOLON'''
            direction = p[1]
            port_name = p[3]
            port_type = "wire"

            port = VerilogPort(port_name, port_type, direction)
            # Note: This is a simplified implementation

        def p_range(p):
            '''range :
                    | LBRACKET NUMBER COLON NUMBER RBRACKET'''
            pass

        def p_parameter_declaration(p):
            '''parameter_declaration : PARAMETER IDENTIFIER ASSIGN NUMBER SEMICOLON'''
            pass

        def p_error(p):
            if p:
                raise RuntimeError(f"Syntax error at token {p.type} ('{p.value}') on line {p.lineno}")
            else:
                raise RuntimeError("Syntax error at end of file")

        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)

    def _find_column(self, token):
        """Find the column position of a token"""
        line_start = self.lexer.lexdata.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1