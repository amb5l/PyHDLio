"""
SystemVerilog Parser implementation using PLY
(Extends Verilog parser with SystemVerilog-specific features)
"""

from typing import List, Dict, Any, Optional
from .verilog_parser import VerilogParser
from ..systemverilog import SystemVerilogModule, SystemVerilogInterface, SystemVerilogPackage, SystemVerilogPort
from ..base import HDLToken, HDLPortGroup

import ply.lex as lex
import ply.yacc as yacc


class SystemVerilogParser(VerilogParser):
    """SystemVerilog Parser using PLY (extends Verilog parser)"""

    # SystemVerilog tokens (extends Verilog tokens)
    tokens = VerilogParser.tokens + (
        'INTERFACE',
        'ENDINTERFACE',
        'MODPORT',
        'PACKAGE',
        'ENDPACKAGE',
        'IMPORT',
        'EXPORT',
        'CLASS',
        'ENDCLASS',
        'FUNCTION',
        'ENDFUNCTION',
        'TASK',
        'ENDTASK',
        'LOGIC',
        'BIT',
        'BYTE',
        'SHORTINT',
        'INT',
        'LONGINT',
        'SHORTREAL',
        'REAL',
        'TIME',
        'REALTIME',
        'STRING',
        'CHANDLE',
        'EVENT',
        'VIRTUAL',
        'TYPEDEF',
        'ENUM',
        'STRUCT',
        'UNION',
        'PACKED',
        'UNPACKED'
    )

    # SystemVerilog reserved words (extends Verilog reserved words)
    reserved = dict(VerilogParser.reserved, **{
        'interface': 'INTERFACE',
        'endinterface': 'ENDINTERFACE',
        'modport': 'MODPORT',
        'package': 'PACKAGE',
        'endpackage': 'ENDPACKAGE',
        'import': 'IMPORT',
        'export': 'EXPORT',
        'class': 'CLASS',
        'endclass': 'ENDCLASS',
        'function': 'FUNCTION',
        'endfunction': 'ENDFUNCTION',
        'task': 'TASK',
        'endtask': 'ENDTASK',
        'logic': 'LOGIC',
        'bit': 'BIT',
        'byte': 'BYTE',
        'shortint': 'SHORTINT',
        'int': 'INT',
        'longint': 'LONGINT',
        'shortreal': 'SHORTREAL',
        'real': 'REAL',
        'time': 'TIME',
        'realtime': 'REALTIME',
        'string': 'STRING',
        'chandle': 'CHANDLE',
        'event': 'EVENT',
        'virtual': 'VIRTUAL',
        'typedef': 'TYPEDEF',
        'enum': 'ENUM',
        'struct': 'STRUCT',
        'union': 'UNION',
        'packed': 'PACKED',
        'unpacked': 'UNPACKED'
    })

    def __init__(self, language: str):
        super().__init__(language)

    def _setup_parser(self):
        """Setup SystemVerilog parser (extends Verilog parser)"""

        # Call parent setup first
        super()._setup_parser()

        # Additional SystemVerilog grammar rules
        def p_description_sv(p):
            '''description : module_declaration
                          | interface_declaration
                          | package_declaration'''
            pass

        def p_module_declaration_sv(p):
            '''module_declaration : MODULE IDENTIFIER LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE
                                  | MODULE IDENTIFIER module_parameters LPAREN port_list RPAREN SEMICOLON module_items ENDMODULE'''
            module_name = p[2]
            module = SystemVerilogModule(module_name)

            # Extract ports - check different positions based on whether parameters exist
            port_list_pos = 4 if len(p) == 9 else 5
            if len(p) > port_list_pos and p[port_list_pos]:
                port_groups = self.extract_port_groups(p[port_list_pos], self.current_tokens)
                for group in port_groups:
                    module.add_port_group(group)

            self.current_document.add_design_unit(module)

        def p_interface_declaration(p):
            '''interface_declaration : INTERFACE IDENTIFIER LPAREN port_list RPAREN SEMICOLON interface_items ENDINTERFACE
                                    | INTERFACE IDENTIFIER SEMICOLON interface_items ENDINTERFACE'''
            interface_name = p[2]
            interface = SystemVerilogInterface(interface_name)

            # Extract ports if they exist
            if len(p) > 5 and p[4] and isinstance(p[4], list):
                port_groups = self.extract_port_groups(p[4], self.current_tokens)
                for group in port_groups:
                    interface.add_port_group(group)

            self.current_document.add_design_unit(interface)

        def p_package_declaration_sv(p):
            '''package_declaration : PACKAGE IDENTIFIER SEMICOLON package_items ENDPACKAGE'''
            package_name = p[2]
            package = SystemVerilogPackage(package_name)
            self.current_document.add_design_unit(package)

        def p_module_parameters(p):
            '''module_parameters :
                                | LBRACKET parameter_list RBRACKET'''
            pass

        def p_parameter_list(p):
            '''parameter_list : parameter_declaration
                             | parameter_list COMMA parameter_declaration'''
            pass

        def p_interface_items(p):
            '''interface_items :
                              | interface_items interface_item'''
            pass

        def p_interface_item(p):
            '''interface_item : port_declaration
                             | modport_declaration
                             | parameter_declaration'''
            pass

        def p_package_items(p):
            '''package_items :
                            | package_items package_item'''
            pass

        def p_package_item(p):
            '''package_item : parameter_declaration
                           | typedef_declaration
                           | function_declaration
                           | task_declaration'''
            pass

        def p_modport_declaration(p):
            '''modport_declaration : MODPORT IDENTIFIER LPAREN modport_items RPAREN SEMICOLON'''
            pass

        def p_modport_items(p):
            '''modport_items : modport_item
                            | modport_items COMMA modport_item'''
            pass

        def p_modport_item(p):
            '''modport_item : INPUT IDENTIFIER
                           | OUTPUT IDENTIFIER
                           | INOUT IDENTIFIER'''
            pass

        def p_typedef_declaration(p):
            '''typedef_declaration : TYPEDEF data_type IDENTIFIER SEMICOLON'''
            pass

        def p_function_declaration(p):
            '''function_declaration : FUNCTION data_type IDENTIFIER LPAREN function_args RPAREN SEMICOLON ENDFUNCTION'''
            pass

        def p_task_declaration(p):
            '''task_declaration : TASK IDENTIFIER LPAREN task_args RPAREN SEMICOLON ENDTASK'''
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
            '''function_arg : data_type IDENTIFIER'''
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
            '''task_arg : data_type IDENTIFIER'''
            pass

        def p_data_type(p):
            '''data_type : LOGIC
                        | BIT
                        | BYTE
                        | SHORTINT
                        | INT
                        | LONGINT
                        | SHORTREAL
                        | REAL
                        | TIME
                        | REALTIME
                        | STRING
                        | CHANDLE
                        | EVENT
                        | IDENTIFIER'''
            p[0] = p[1]

        # Override port declaration to support SystemVerilog types
        def p_port_declaration_sv(p):
            '''port_declaration : INPUT data_type range IDENTIFIER SEMICOLON
                               | OUTPUT data_type range IDENTIFIER SEMICOLON
                               | INOUT data_type range IDENTIFIER SEMICOLON
                               | INPUT range IDENTIFIER SEMICOLON
                               | OUTPUT range IDENTIFIER SEMICOLON
                               | INOUT range IDENTIFIER SEMICOLON'''
            direction = p[1]

            if len(p) == 6:  # data_type included
                data_type = p[2]
                port_name = p[4]
            else:  # no data_type, default to logic
                data_type = "logic"
                port_name = p[3]

            port = SystemVerilogPort(port_name, data_type, direction)
            # Note: This is a simplified implementation

        # Re-create the parser with new rules
        self.parser = yacc.yacc(module=self, debug=False, write_tables=False)
