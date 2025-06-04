from antlr4 import ParseTreeVisitor, Token
from .grammar.vhdlParser import vhdlParser
from .ast import Generic, Port, PortGroup, Entity, VHDLAST
import re

class VHDLVisitor(ParseTreeVisitor):
    """Visitor to convert ANTLR4 parse tree to AST with port grouping."""

    def visit(self, tree):
        """Override visit to handle missing methods gracefully."""
        try:
            # Call specific visitor methods based on node type
            if isinstance(tree, vhdlParser.Design_fileContext):
                result = self.visitDesign_file(tree)
            elif isinstance(tree, vhdlParser.Design_unitContext):
                result = self.visitDesign_unit(tree)
            elif isinstance(tree, vhdlParser.Library_unitContext):
                result = self.visitLibrary_unit(tree)
            elif isinstance(tree, vhdlParser.Primary_unitContext):
                result = self.visitPrimary_unit(tree)
            elif isinstance(tree, vhdlParser.Entity_declarationContext):
                result = self.visitEntity_declaration(tree)
            elif isinstance(tree, vhdlParser.Generic_clauseContext):
                result = self.visitGeneric_clause(tree)
            elif isinstance(tree, vhdlParser.Port_clauseContext):
                result = self.visitPort_clause_with_grouping(tree)
            else:
                # For other node types, return None
                result = None

            return result
        except AttributeError as e:
            # If a visitor method is missing, return None instead of crashing
            print(f"Warning: Missing visitor method for {tree.__class__.__name__}: {e}")
            return None
        except Exception as e:
            print(f"Error visiting {tree.__class__.__name__}: {e}")
            import traceback
            traceback.print_exc()
            return None

    def format_type_string(self, type_text):
        """Format type string to have proper spacing in constraints."""
        if not type_text:
            return type_text

        # Add spaces around 'downto' and 'to' keywords
        formatted = re.sub(r'(\w)downto(\w)', r'\1 downto \2', type_text)
        formatted = re.sub(r'(\w)to(\w)', r'\1 to \2', formatted)

        # Add spaces around operators in constraints
        formatted = re.sub(r'(\w)-(\w)', r'\1 - \2', formatted)
        formatted = re.sub(r'(\w)\+(\w)', r'\1 + \2', formatted)

        return formatted

    def visitDesign_file(self, ctx):
        """Visit design file and return VHDLAST with all entities."""
        entities = []

        # Process each design unit in the file
        for design_unit_ctx in ctx.design_unit():
            entity = self.visit(design_unit_ctx)
            if entity:
                entities.append(entity)

        return VHDLAST(entities=entities)

    def visitDesign_unit(self, ctx: vhdlParser.Design_unitContext):
        """Visit design unit and extract entity if present."""
        if ctx.library_unit():
            return self.visit(ctx.library_unit())
        return None

    def visitLibrary_unit(self, ctx: vhdlParser.Library_unitContext):
        """Visit library unit and extract primary unit if present."""
        if ctx.primary_unit():
            return self.visit(ctx.primary_unit())
        return None

    def visitPrimary_unit(self, ctx: vhdlParser.Primary_unitContext):
        """Visit primary unit and extract entity declaration if present."""
        if ctx.entity_declaration():
            return self.visit(ctx.entity_declaration())
        return None

    def visitEntity_declaration(self, ctx: vhdlParser.Entity_declarationContext):
        """Visit entity declaration and extract entity information."""
        # Extract entity name - should be the first identifier
        name = "unknown"
        if ctx.identifier() and len(ctx.identifier()) > 0:
            name = ctx.identifier(0).getText()

        generics = []
        ports = []
        port_groups = []

        # Extract generics and ports from entity header if present
        if ctx.entity_header():
            entity_header = ctx.entity_header()

            # Extract generics
            if entity_header.generic_clause():
                generics = self.visitGeneric_clause(entity_header.generic_clause()) or []

            # Extract ports
            if entity_header.port_clause():
                ports, port_groups = self.visitPort_clause_with_grouping(entity_header.port_clause())

        return Entity(name=name, generics=generics, ports=ports, port_groups=port_groups)

    def visitGeneric_clause(self, ctx: vhdlParser.Generic_clauseContext):
        """Extract generics from generic clause."""
        generics = []
        if ctx.generic_list():
            # generic_list contains interface_constant_declarations separated by SEMI
            for interface_const in ctx.generic_list().interface_constant_declaration():
                extracted_generics = self.visitGeneric_interface(interface_const)
                if extracted_generics:
                    generics.extend(extracted_generics)
        return generics

    def visitGeneric_interface(self, interface_const):
        """Extract generic from interface_constant_declaration."""
        generics = []
        if interface_const.identifier_list() and interface_const.subtype_indication():
            type_str = self.format_type_string(interface_const.subtype_indication().getText())
            default = None
            if interface_const.expression():
                default = interface_const.expression().getText()

            for identifier in interface_const.identifier_list().identifier():
                generics.append(Generic(
                    name=identifier.getText(),
                    type=type_str,
                    default_value=default
                ))
        return generics

    def visitPort_clause_with_grouping(self, ctx: vhdlParser.Port_clauseContext):
        """Extract ports from port clause with source-proximity-based grouping."""
        ports = []
        port_groups = []

        if ctx.port_list() and ctx.port_list().interface_port_list():
            # Collect all ports first and analyze their source positions
            all_interface_ports = ctx.port_list().interface_port_list().interface_port_declaration()

            current_group = []

            for i, interface_port in enumerate(all_interface_ports):
                interface_ports = self.visitPort_interface(interface_port)
                ports.extend(interface_ports)
                current_group.extend(interface_ports)

                # Check if this is the last interface declaration
                is_last = (i == len(all_interface_ports) - 1)

                # Determine if there's a significant gap to the next interface
                should_end_group = False

                if not is_last:
                    # Get line information for current and next interface
                    current_line = interface_port.stop.line if interface_port.stop else 0
                    next_interface = all_interface_ports[i + 1]
                    next_line = next_interface.start.line if next_interface.start else 0

                    # If there's more than one line gap, consider it a group boundary
                    # This detects blank lines between port declarations
                    line_gap = next_line - current_line
                    if line_gap > 1:  # More than just the next line = blank line(s) in between
                        should_end_group = True
                else:
                    # Last interface - end the current group
                    should_end_group = True

                if should_end_group and current_group:
                    port_groups.append(PortGroup(ports=current_group.copy()))
                    current_group = []

            # Handle any remaining ports in current group
            if current_group:
                port_groups.append(PortGroup(ports=current_group.copy()))

        return ports, port_groups

    def visitPort_interface(self, interface_port):
        """Extract ports from interface_port_declaration."""
        ports = []
        if interface_port.identifier_list() and interface_port.subtype_indication():
            direction = "in"  # default
            if interface_port.signal_mode():
                direction = interface_port.signal_mode().getText()

            type_str = self.format_type_string(interface_port.subtype_indication().getText())

            for identifier in interface_port.identifier_list().identifier():
                ports.append(Port(
                    name=identifier.getText(),
                    direction=direction,
                    type=type_str,
                    constraint=None  # TODO: Extract constraints if needed
                ))
        return ports

    def visitChildren(self, node):
        """Visit all children and collect non-None results."""
        results = []
        for i in range(node.getChildCount()):
            child = node.getChild(i)
            result = self.visit(child)
            if result:
                results.append(result)
        return results if results else None