from antlr4 import ParseTreeVisitor, Token
from .grammar.VHDLParser import VHDLParser
from .ast import Generic, Port, PortGroup, Entity, VHDLAST
import re

class VHDLVisitor(ParseTreeVisitor):
    """Visitor to convert ANTLR4 parse tree to AST."""

    def visit(self, tree):
        """Override visit to handle missing methods gracefully."""
        try:
            # Call specific visitor methods based on node type using match-case
            match tree:
                case VHDLParser.Rule_DesignFileContext():
                    result = self.visitDesignFile(tree)
                case VHDLParser.Rule_DesignUnitContext():
                    result = self.visitDesignUnit(tree)
                case VHDLParser.Rule_LibraryUnitContext():
                    result = self.visitLibraryUnit(tree)
                case VHDLParser.Rule_EntityDeclarationContext():
                    result = self.visitEntityDeclaration(tree)
                case VHDLParser.Rule_GenericClauseContext():
                    result = self.visitGenericClause(tree)
                case VHDLParser.Rule_PortClauseContext():
                    result = self.visitPortClauseWithGrouping(tree)
                case _:
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

        # Add spaces around 'downto' keyword (but not inside words like "vector")
        formatted = re.sub(r'\bdownto\b', ' downto ', type_text)
        # Add spaces around standalone 'to' keyword in range expressions (but not inside words like "vector")
        formatted = re.sub(r'\b(\d+|[a-zA-Z_]\w*)\s*to\s*(\d+|[a-zA-Z_]\w*)\b', r'\1 to \2', formatted)

        # Add spaces around operators in constraints
        formatted = re.sub(r'(\w)-(\w)', r'\1 - \2', formatted)
        formatted = re.sub(r'(\w)\+(\w)', r'\1 + \2', formatted)

        # Clean up multiple spaces
        formatted = re.sub(r'\s+', ' ', formatted).strip()

        return formatted

    def visitDesignFile(self, ctx):
        """Visit design file and return VHDLAST with all entities."""
        entities = []

        # Process each design unit in the file
        for design_unit_ctx in ctx.rule_DesignUnit():
            entity = self.visit(design_unit_ctx)
            if entity:
                entities.append(entity)

        return VHDLAST(entities=entities)

    def visitDesignUnit(self, ctx: VHDLParser.Rule_DesignUnitContext):
        """Visit design unit and extract entity if present."""
        if ctx.rule_LibraryUnit():
            return self.visit(ctx.rule_LibraryUnit())
        return None

    def visitLibraryUnit(self, ctx: VHDLParser.Rule_LibraryUnitContext):
        """Visit library unit and extract entity declaration if present."""
        if ctx.rule_EntityDeclaration():
            return self.visit(ctx.rule_EntityDeclaration())
        return None

    def visitEntityDeclaration(self, ctx: VHDLParser.Rule_EntityDeclarationContext):
        """Visit entity declaration and extract entity information."""
        # Extract entity name from the identifier token
        name = "unknown"
        if ctx.name and ctx.name.text:
            name = ctx.name.text

        generics = []
        ports = []
        port_groups = []

        # Extract generics from generic clause if present
        if ctx.rule_GenericClause():
            generics = self.visitGenericClause(ctx.rule_GenericClause()) or []

        # Extract ports from port clause if present
        if ctx.rule_PortClause():
            ports, port_groups = self.visitPortClauseWithGrouping(ctx.rule_PortClause())

        return Entity(name=name, generics=generics, ports=ports, port_groups=port_groups)

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

                # Create Generic objects for each name
                for name in names:
                    generics.append(Generic(
                        name=name,
                        type=type_str,
                        default_value=default_value or "0"
                    ))

        return generics

    def visitPortClauseWithGrouping(self, ctx: VHDLParser.Rule_PortClauseContext):
        """Extract ports from port clause with logical grouping based on signal types and patterns."""
        ports = []
        port_groups = []

        # Process each interface signal declaration
        for port_ctx in ctx.rule_InterfaceSignalDeclaration():
            port_list = self.visitInterfaceSignalDeclaration(port_ctx)
            ports.extend(port_list)

        # Implement intelligent grouping based on signal types and names
        if ports:
            groups = self.create_logical_port_groups(ports)
            port_groups.extend(groups)

        return ports, port_groups

    def create_logical_port_groups(self, ports):
        """Create logical port groups based on signal types and naming patterns."""
        if not ports:
            return []

        # Define common control signal patterns
        control_patterns = ['clk', 'clock', 'reset', 'rst', 'enable', 'en', 'valid', 'ready']

        control_ports = []
        data_ports = []

        for port in ports:
            port_name_lower = port.name.lower()
            is_control = False

            # Check if it's a control signal
            for pattern in control_patterns:
                if pattern in port_name_lower:
                    is_control = True
                    break

            # Also consider single-bit signals as potential control signals
            if not is_control and ('std_logic' in port.type.lower() and '(' not in port.type):
                is_control = True

            if is_control:
                control_ports.append(port)
            else:
                data_ports.append(port)

        # Create groups
        groups = []

        if control_ports:
            groups.append(PortGroup(ports=control_ports))

        if data_ports:
            groups.append(PortGroup(ports=data_ports))

        # If we only have one type, still create a single group (fallback)
        if not groups:
            groups.append(PortGroup(ports=ports))

        return groups

    def visitInterfaceSignalDeclaration(self, ctx):
        """Extract ports from interface signal declaration."""
        ports = []

        # Extract port names from identifier list
        names = []
        if ctx.rule_IdentifierList():
            names = self.extractIdentifierList(ctx.rule_IdentifierList())

        # Extract mode indication (direction and type)
        direction = "in"
        port_type = "std_logic"
        constraint = None

        if ctx.modeName:
            direction, port_type, constraint = self.extractModeIndication(ctx.modeName)

        # Create Port objects for each name
        for name in names:
            ports.append(Port(
                name=name,
                direction=direction,
                type=port_type,
                constraint=constraint
            ))

        return ports

    def extractIdentifierList(self, ctx):
        """Extract list of identifiers from IdentifierList context."""
        names = []
        if ctx and hasattr(ctx, 'LIT_IDENTIFIER'):
            # Get all identifier tokens from the context
            identifier_tokens = ctx.LIT_IDENTIFIER()
            if identifier_tokens:
                names = [token.getText() for token in identifier_tokens]
        return names

    def extractSubtypeIndication(self, ctx):
        """Extract type string from SubtypeIndication context."""
        if not ctx:
            return "unknown"

        # SubtypeIndication has: [ResolutionIndication] Name [Constraint]
        type_parts = []
        constraint_text = None

        # Extract the main type name
        if ctx.rule_Name():
            name_ctx = ctx.rule_Name()

            # Check if this is a SliceName (which represents array types with constraints)
            if type(name_ctx).__name__ == 'Rule_SliceNameContext':
                # Extract base type name (child 0 should be the prefix)
                if name_ctx.getChildCount() >= 1:
                    base_name_ctx = name_ctx.getChild(0)
                    base_type = base_name_ctx.getText() if hasattr(base_name_ctx, 'getText') else str(base_name_ctx)
                    type_parts.append(base_type)

                # Extract constraint from DiscreteRange (child 2)
                if name_ctx.getChildCount() >= 3:
                    discrete_range_ctx = name_ctx.getChild(2)
                    if hasattr(discrete_range_ctx, 'getText'):
                        constraint_text = self.formatConstraintText(discrete_range_ctx.getText())
            else:
                # Regular name without constraint
                type_name = name_ctx.getText()
                type_parts.append(type_name)

        # Extract explicit constraint if present (for arrays like std_logic_vector(7 downto 0))
        if ctx.rule_Constraint():
            explicit_constraint = self.extractConstraint(ctx.rule_Constraint())
            if explicit_constraint:
                constraint_text = explicit_constraint

        # Build result - for now, include constraint in type for compatibility
        if constraint_text:
            result = type_parts[0] + "(" + constraint_text + ")"
        else:
            result = "".join(type_parts)

        return result

    def formatConstraintText(self, constraint_text):
        """Format constraint text to add proper spacing."""
        if not constraint_text:
            return constraint_text

        # Add spaces around operators first
        formatted = constraint_text
        # Add spaces around arithmetic operators if not already present
        formatted = re.sub(r'(\w)-(\w)', r'\1 - \2', formatted)
        formatted = re.sub(r'(\w)\+(\w)', r'\1 + \2', formatted)

        # Add spaces around 'downto' and 'to' (but keep them as single words)
        formatted = re.sub(r'(\w)downto(\w)', r'\1 downto \2', formatted)
        formatted = re.sub(r'(\w)to(\w)', r'\1 to \2', formatted)

        # Clean up multiple spaces
        formatted = ' '.join(formatted.split())

        return formatted

    def extractConstraint(self, ctx):
        """Extract constraint text (like array bounds) from Constraint context."""
        if not ctx:
            return ""

        # Constraint can be SimpleRange, RangeConstraint, ArrayConstraint, or RecordConstraint
        if ctx.rule_ArrayConstraint():
            return self.extractArrayConstraint(ctx.rule_ArrayConstraint())
        elif ctx.rule_SimpleRange():
            return self.extractSimpleRange(ctx.rule_SimpleRange())
        elif ctx.rule_RangeConstraint():
            range_ctx = ctx.rule_RangeConstraint()
            if range_ctx.rule_Range():
                return self.extractRange(range_ctx.rule_Range())

        # Fallback to getText for other constraint types
        return ctx.getText()

    def extractArrayConstraint(self, ctx):
        """Extract array constraint like (7 downto 0)."""
        if not ctx:
            return ""

        # ArrayConstraint has IndexConstraint [ElementConstraint]
        if ctx.rule_IndexConstraint():
            return self.extractIndexConstraint(ctx.rule_IndexConstraint())

        return ctx.getText()

    def extractIndexConstraint(self, ctx):
        """Extract index constraint like (7 downto 0)."""
        if not ctx:
            return ""

        # IndexConstraint is (DiscreteRange, DiscreteRange, ...)
        parts = []
        if hasattr(ctx, 'ranges') and ctx.ranges:
            for range_ctx in ctx.ranges:
                range_text = self.extractDiscreteRange(range_ctx)
                if range_text:
                    parts.append(range_text)

        if parts:
            return "(" + ", ".join(parts) + ")"

        return ctx.getText()

    def extractDiscreteRange(self, ctx):
        """Extract discrete range like 'WIDTH - 1 downto 0'."""
        if not ctx:
            return ""

        # DiscreteRange can be SubtypeIndication or Range
        if hasattr(ctx, 'range_') and ctx.range_:
            return self.extractRange(ctx.range_)
        elif hasattr(ctx, 'subtypeIndication') and ctx.subtypeIndication:
            return self.extractSubtypeIndication(ctx.subtypeIndication)

        return ctx.getText()

    def extractRange(self, ctx):
        """Extract range like 'WIDTH - 1 downto 0'."""
        if not ctx:
            return ""

        # Range can be Name, SimpleRange, or Expression
        if ctx.rule_SimpleRange():
            return self.extractSimpleRange(ctx.rule_SimpleRange())
        elif ctx.rule_Name():
            return ctx.rule_Name().getText()
        elif ctx.rule_Expression():
            return ctx.rule_Expression().getText()

        return ctx.getText()

    def extractSimpleRange(self, ctx):
        """Extract simple range with proper spacing like 'WIDTH - 1 downto 0'."""
        if not ctx:
            return ""

        # SimpleRange has leftBound Direction rightBound
        parts = []

        # Extract left bound
        if hasattr(ctx, 'leftBound') and ctx.leftBound:
            left_text = self.extractExpression(ctx.leftBound)
            parts.append(left_text)

        # Extract direction
        if hasattr(ctx, 'direction') and ctx.direction:
            direction_text = self.extractDirection(ctx.direction)
            parts.append(direction_text)

        # Extract right bound
        if hasattr(ctx, 'rightBound') and ctx.rightBound:
            right_text = self.extractExpression(ctx.rightBound)
            parts.append(right_text)

        return " ".join(parts)

    def extractDirection(self, ctx):
        """Extract direction like 'downto' or 'to'."""
        if not ctx:
            return ""

        # Direction has a direction token
        if hasattr(ctx, 'direction') and ctx.direction:
            return ctx.direction.text

        return ctx.getText()

    def extractExpression(self, ctx):
        """Extract expression text from Expression context with basic formatting."""
        if not ctx:
            return ""

        # For now, get the expression text and apply minimal formatting for operators
        expr_text = ctx.getText()

        # Add spaces around operators (but be careful not to break existing formatting)
        formatted = expr_text
        # Only add spaces if there aren't already spaces
        formatted = re.sub(r'(\w)-(\w)', r'\1 - \2', formatted)
        formatted = re.sub(r'(\w)\+(\w)', r'\1 + \2', formatted)

        return formatted

    def extractModeIndication(self, ctx):
        """Extract direction, type, and constraint from ModeIndication context."""
        direction = "in"
        port_type = "std_logic"
        constraint = None

        if not ctx:
            return direction, port_type, constraint

        # ModeIndication can be SimpleModeIndication, ArrayModeViewIndication, or RecordModeViewIndication
        if ctx.rule_SimpleModeIndication():
            simple_ctx = ctx.rule_SimpleModeIndication()

            # Extract mode (direction) - optional, defaults to 'in'
            if simple_ctx.rule_Mode():
                mode_ctx = simple_ctx.rule_Mode()
                if hasattr(mode_ctx, 'name') and mode_ctx.name:
                    direction = mode_ctx.name.text.lower()

            # Extract type from interface type indication
            if simple_ctx.rule_InterfaceTypeIndication():
                type_indication_ctx = simple_ctx.rule_InterfaceTypeIndication()
                port_type = self.extractInterfaceTypeIndication(type_indication_ctx)

        return direction, port_type, constraint

    def extractInterfaceTypeIndication(self, ctx):
        """Extract type from InterfaceTypeIndication context."""
        if not ctx:
            return "std_logic"

        # InterfaceTypeIndication contains a SubtypeIndication
        if hasattr(ctx, 'rule_SubtypeIndication') and ctx.rule_SubtypeIndication():
            return self.extractSubtypeIndication(ctx.rule_SubtypeIndication())

        # Fallback to getText if structure is different
        return ctx.getText()

    def visitChildren(self, node):
        """Visit all children and collect non-None results."""
        results = []
        for i in range(node.getChildCount()):
            child = node.getChild(i)
            result = self.visit(child)
            if result:
                results.append(result)
        return results if results else None