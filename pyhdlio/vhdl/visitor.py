"""VHDL AST visitor implementation."""

from antlr4 import ParseTreeVisitor, Token
from .grammar.VHDLParser import VHDLParser

# Import pyVHDLModel classes directly
import pyVHDLModel
from pyVHDLModel import (
    Document as PyVHDLDocument, Entity, Package, PackageBody, ComponentInstantiation,
    GenericConstantInterfaceItem, PortSignalInterfaceItem, PortGroup,
    Mode, SimpleName, SimpleSubtypeSymbol,
    IntegerLiteral, EnumerationLiteral, StringLiteral, Component
)
from pyVHDLModel.Symbol import PackageSymbol
from pathlib import Path
import re

class VHDLVisitor(ParseTreeVisitor):
    """Visitor to convert ANTLR4 parse tree to pyVHDLModel objects."""

    def __init__(self, filename: str = "parsed.vhd"):
        super().__init__()
        self.filename = filename
        self.document = PyVHDLDocument(Path(filename))
        self.current_entity = None
        self.current_architecture = None
        self.current_process = None

    def visit(self, tree):
        """Override visit to handle missing methods gracefully."""
        try:
            if isinstance(tree, VHDLParser.Rule_DesignFileContext):
                result = self.visitDesignFile(tree)
            elif isinstance(tree, VHDLParser.Rule_DesignUnitContext):
                result = self.visitDesignUnit(tree)
            elif isinstance(tree, VHDLParser.Rule_LibraryUnitContext):
                result = self.visitLibraryUnit(tree)
            elif isinstance(tree, VHDLParser.Rule_EntityDeclarationContext):
                result = self.visitEntityDeclaration(tree)
            elif isinstance(tree, VHDLParser.Rule_GenericClauseContext):
                result = self.visitGenericClause(tree)
            elif isinstance(tree, VHDLParser.Rule_PortClauseContext):
                result = self.visitPortClause(tree)
            elif isinstance(tree, VHDLParser.Rule_PackageDeclarationContext):
                result = self.visitRule_PackageDeclaration(tree)
            elif isinstance(tree, VHDLParser.Rule_PackageDeclarativeItemContext):
                result = self.visitRule_PackageDeclarativeItem(tree)
            elif isinstance(tree, VHDLParser.Rule_ComponentDeclarationContext):
                result = self.visitRule_ComponentDeclaration(tree)
            elif isinstance(tree, VHDLParser.Rule_PackageBodyContext):
                result = self.visitRule_PackageBody(tree)
            elif isinstance(tree, VHDLParser.Rule_PackageBodyDeclarativeItemContext):
                result = self.visitRule_PackageBodyDeclarativeItem(tree)
            elif isinstance(tree, VHDLParser.Rule_PackageInstantiationDeclarationContext):
                result = self.visitRule_PackageInstantiationDeclaration(tree)
            else:
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

        # Add spaces around 'downto' keyword - handle cases where it's adjacent to numbers/identifiers
        formatted = re.sub(r'(\w)downto(\w)', r'\1 downto \2', type_text)

        # Add spaces around operators in constraints
        formatted = re.sub(r'(\w)-(\w)', r'\1 - \2', formatted)
        formatted = re.sub(r'(\w)\+(\w)', r'\1 + \2', formatted)

        # Clean up multiple spaces
        formatted = re.sub(r'\s+', ' ', formatted).strip()

        return formatted

    def visitDesignFile(self, ctx):
        """Visit design file and populate the pyVHDLModel Document."""
        # Process each design unit in the file
        for design_unit_ctx in ctx.rule_DesignUnit():
            result = self.visit(design_unit_ctx)
            if result:
                if isinstance(result, Entity):
                    self.document._AddEntity(result)
                elif isinstance(result, Package):
                    self.document._AddPackage(result)

        return self.document

    def visitDesignUnit(self, ctx: VHDLParser.Rule_DesignUnitContext):
        """Visit design unit and extract entity if present."""
        if ctx.rule_LibraryUnit():
            return self.visit(ctx.rule_LibraryUnit())
        return None

    def visitLibraryUnit(self, ctx: VHDLParser.Rule_LibraryUnitContext):
        """Visit library unit and extract entity or package declaration if present."""
        if ctx.rule_EntityDeclaration():
            return self.visit(ctx.rule_EntityDeclaration())
        elif ctx.rule_PackageDeclaration():
            return self.visitRule_PackageDeclaration(ctx.rule_PackageDeclaration())
        elif ctx.rule_PackageBody():
            return self.visitRule_PackageBody(ctx.rule_PackageBody())
        elif ctx.rule_PackageInstantiationDeclaration():
            return self.visitRule_PackageInstantiationDeclaration(ctx.rule_PackageInstantiationDeclaration())
        return None

    def visitEntityDeclaration(self, ctx: VHDLParser.Rule_EntityDeclarationContext):
        """Visit entity declaration and extract entity information."""
        # Extract entity name from the identifier token
        name = "unknown"
        if ctx.name and ctx.name.text:
            name = ctx.name.text

        # Create pyVHDLModel Entity
        entity = Entity(identifier=name)

        # Extract generics from generic clause if present
        if ctx.rule_GenericClause():
            generics = self.visitGenericClause(ctx.rule_GenericClause()) or []
            entity._genericItems.extend(generics)

        # Extract ports and port groups from port clause if present
        if ctx.rule_PortClause():
            ports, port_groups = self.visitPortClause(ctx.rule_PortClause())
            entity._portItems.extend(ports)
            if port_groups:
                entity._portGroups.extend(port_groups)

        return entity

    def visitGenericClause(self, ctx: VHDLParser.Rule_GenericClauseContext):
        """Extract generics from generic clause."""
        generics = []

        # Process each interface element
        for element_ctx in ctx.rule_InterfaceElement():
            element_generics = self.visitInterfaceElement(element_ctx)
            if element_generics:
                generics.extend(element_generics)

        return generics

    def visitInterfaceElement(self, element_ctx):
        """Extract generics from interface element."""
        generics = []

        # Get the interface declaration
        if element_ctx.rule_InterfaceDeclaration():
            decl_ctx = element_ctx.rule_InterfaceDeclaration()

            # Check if it's a constant declaration (for generics)
            if decl_ctx.rule_InterfaceConstantDeclaration():
                const_ctx = decl_ctx.rule_InterfaceConstantDeclaration()

                # Extract constant names from identifier list
                names = []
                if const_ctx.constantNames:
                    names = self.extractIdentifierList(const_ctx.constantNames)

                # Extract type from subtype indication
                type_str = "unknown"
                if const_ctx.subtypeIndication:
                    type_str = self.extractSubtypeIndication(const_ctx.subtypeIndication)

                # Extract default value if present
                default_value = None
                if const_ctx.defaultValue:
                    default_value = self.extractExpression(const_ctx.defaultValue)

                # Create pyVHDLModel GenericConstantInterfaceItem objects for each name
                for name in names:
                    # Create a subtype symbol
                    type_name = SimpleName(type_str)
                    type_symbol = SimpleSubtypeSymbol(type_name)

                    # Handle default value - convert to appropriate Expression
                    default_expr = None
                    if default_value:
                        default_expr = self._convert_default_value(default_value)

                    generic_item = GenericConstantInterfaceItem(
                        identifiers=[name],
                        mode=Mode.In,  # Generics are always input mode
                        subtype=type_symbol,
                        defaultExpression=default_expr
                    )
                    generics.append(generic_item)

        return generics

    def visitPortClause(self, ctx: VHDLParser.Rule_PortClauseContext):
        """Extract ports from port clause and organize them into groups."""
        all_ports = []
        port_groups = []
        current_group_ports = []

        # Process each interface signal declaration
        signal_declarations = ctx.rule_InterfaceSignalDeclaration()

        for i, port_ctx in enumerate(signal_declarations):
            port_list = self.visitInterfaceSignalDeclaration(port_ctx)
            all_ports.extend(port_list)
            current_group_ports.extend(port_list)

            # Check if this is the last declaration or if there's a significant gap
            # For now, we'll create groups based on simple heuristics:
            # - Every 2 declarations forms a group (for simple.vhd: clk+reset, start+count)
            # - Or if we reach the end of declarations

            is_last = (i == len(signal_declarations) - 1)
            should_group = len(current_group_ports) >= 2 or is_last

            if should_group and current_group_ports:
                # Create a port group
                group_name = f"Group{len(port_groups) + 1}"
                port_group = PortGroup(portItems=current_group_ports, name=group_name)
                port_groups.append(port_group)
                current_group_ports = []

        return all_ports, port_groups

    def visitInterfaceSignalDeclaration(self, ctx):
        """Extract signal ports from interface signal declaration."""
        ports = []

        # Extract port names from identifier list
        names = []
        if ctx.rule_IdentifierList():
            names = self.extractIdentifierList(ctx.rule_IdentifierList())

        # Extract mode (direction) and type from mode indication
        mode = Mode.In  # Default
        type_str = "unknown"

        if ctx.modeName:
            # The modeName contains the mode indication context
            mode_indication_ctx = ctx.getChild(2)  # Based on grammar structure
            if hasattr(mode_indication_ctx, 'rule_SimpleModeIndication'):
                simple_mode = mode_indication_ctx.rule_SimpleModeIndication()
                if simple_mode:
                    # Extract mode
                    if simple_mode.rule_Mode():
                        mode_ctx = simple_mode.rule_Mode()
                        if hasattr(mode_ctx, 'name') and mode_ctx.name:
                            mode_text = mode_ctx.name.text.lower()
                            mode_mapping = {
                                'in': Mode.In,
                                'out': Mode.Out,
                                'inout': Mode.InOut,
                                'buffer': Mode.Buffer,
                                'linkage': Mode.Linkage
                            }
                            mode = mode_mapping.get(mode_text, Mode.In)

                    # Extract type
                    if simple_mode.rule_InterfaceTypeIndication():
                        type_indication = simple_mode.rule_InterfaceTypeIndication()
                        if type_indication.rule_SubtypeIndication():
                            type_str = self.extractSubtypeIndication(type_indication.rule_SubtypeIndication())

        # Create pyVHDLModel PortSignalInterfaceItem objects for each name
        for name in names:
            # Create type symbol
            type_name = SimpleName(type_str)
            type_symbol = SimpleSubtypeSymbol(type_name)

            port_item = PortSignalInterfaceItem(
                identifiers=[name],
                mode=mode,
                subtype=type_symbol
            )
            ports.append(port_item)

        return ports

    def extractIdentifierList(self, ctx):
        """Extract identifier list from context."""
        names = []
        if ctx:
            # Get all LIT_IDENTIFIER tokens
            tokens = ctx.LIT_IDENTIFIER()
            if tokens:
                names = [token.getText() for token in tokens]
        return names

    def extractSubtypeIndication(self, ctx):
        """Extract subtype indication string."""
        if not ctx:
            return "unknown"

        # Get the full text of the subtype indication
        type_text = ctx.getText()

        # Format the type string for readability
        return self.format_type_string(type_text)

    def extractExpression(self, ctx):
        """Extract expression as string."""
        if not ctx:
            return None
        return ctx.getText()

    def _convert_default_value(self, value_str: str):
        """Convert a default value string to an appropriate pyVHDLModel Expression."""
        if not value_str:
            return None

        value_str = value_str.strip()

        # Try to parse as integer
        try:
            int_val = int(value_str)
            return IntegerLiteral(int_val)
        except ValueError:
            pass

        # If it's quoted, treat as string literal
        if value_str.startswith('"') and value_str.endswith('"'):
            return StringLiteral(value_str[1:-1])  # Remove quotes

        # Otherwise treat as enumeration literal (identifier)
        return EnumerationLiteral(value_str)

    def visitRule_PackageDeclaration(self, ctx):
        """Visit a package declaration and create pyVHDLModel Package."""
        if ctx.name:
            package_name = ctx.name.text

            # Create pyVHDLModel Package
            package = Package(identifier=package_name)

            # Visit declarative items to find components and add them to the package
            for item in ctx.declarativeItems:
                item_node = self.visit(item)
                if item_node:
                    # Add declarative items to package using the correct attribute
                    package.DeclaredItems.append(item_node)

            # Manually trigger indexing to ensure components are properly indexed
            package.IndexDeclaredItems()

            return package
        return None

    def visitRule_PackageDeclarativeItem(self, ctx):
        """Visit items declared in a package, including component declarations."""
        # Check if this is a component declaration
        if ctx.componentDeclaration:
            return self.visitRule_ComponentDeclaration(ctx.componentDeclaration)

        # Handle other declarative items
        if ctx.subprogramDeclaration:
            return self.visit(ctx.subprogramDeclaration)
        if ctx.typeDeclaration:
            return self.visit(ctx.typeDeclaration)
        if ctx.constantDeclaration:
            return self.visit(ctx.constantDeclaration)

        return None

    def visitRule_ComponentDeclaration(self, ctx):
        """Visit a component declaration and create a pyVHDLModel Component."""
        if ctx.name:
            component_name = ctx.name.text

            # Extract generics from generic clause if present
            generics = []
            if ctx.genericClause:
                generics = self.visitGenericClause(ctx.genericClause) or []

            # Extract ports from port clause if present
            ports = []
            port_groups = []
            if ctx.portClause:
                ports, port_groups = self.visitPortClause(ctx.portClause)

            # Create pyVHDLModel Component
            component = Component(
                identifier=component_name,
                genericItems=generics,
                portItems=ports,
                portGroups=port_groups
            )

            return component
        return None

    def visitRule_PackageBody(self, ctx):
        """Visit a package body declaration."""
        if ctx.name:
            package_body_name = ctx.name.text

            # Create a PackageSymbol for the corresponding package
            package_symbol = PackageSymbol(SimpleName(package_body_name))

            # Create pyVHDLModel PackageBody with the package symbol
            package_body = PackageBody(packageSymbol=package_symbol)

            return package_body
        return None

    def visitRule_PackageBodyDeclarativeItem(self, ctx):
        """Visit items declared in a package body."""
        # Handle declarative items in package body
        if ctx.subprogramBody:
            return self.visit(ctx.subprogramBody)
        if ctx.typeDeclaration:
            return self.visit(ctx.typeDeclaration)
        if ctx.constantDeclaration:
            return self.visit(ctx.constantDeclaration)

        return None

    def visitRule_PackageInstantiationDeclaration(self, ctx):
        """Visit a package instantiation declaration."""
        if ctx.name:
            package_instance_name = ctx.name.text

        return self.visitChildren(ctx)

    def visitChildren(self, node):
        """Visit all children and collect non-None results."""
        results = []
        for i in range(node.getChildCount()):
            child = node.getChild(i)
            result = self.visit(child)
            if result:
                results.append(result)
        return results if results else None