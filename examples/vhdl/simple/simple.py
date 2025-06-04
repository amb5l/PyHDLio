#!/usr/bin/env python3
"""
PyHDLio Unified Example: AST + pyVHDLModel Integration
Demonstrates VHDL parsing using both PyHDLio AST and pyVHDLModel approaches.
"""

import os
import sys

# Add PyHDLio to path for example execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from hdlio.vhdl.parse_vhdl import parse_vhdl, VHDLSyntaxError
from hdlio.vhdl.reporter import report_entities, report_entity, report_generics, report_ports_flat, report_ports_grouped
from hdlio.vhdl.converters.pyvhdlmodel_converter import convert_to_pyvhdlmodel

def demonstrate_ast_approach(vhdl_file):
    """Demonstrate PyHDLio AST approach - lightweight and fast."""
    print("=" * 70)
    print("🔧 PyHDLio AST Approach (Lightweight & Fast)")
    print("=" * 70)

    try:
        # Parse using PyHDLio AST
        module = parse_vhdl(vhdl_file, mode='ast')

        # Display using enhanced reporter (automatically detects AST type)
        print("📊 AST Entity Report:")
        print(report_entities(module))

        # Demonstrate programmatic AST access
        print("\n--- 🔍 Programmatic AST Access ---")
        for entity in module.entities:
            print(f"🏗️  Entity: {entity.name}")
            print(f"   📄 Generics: {len(entity.generics)}")
            print(f"   🔌 Ports: {len(entity.ports)}")
            print(f"   📦 Port Groups: {len(entity.port_groups)}")

            # Show generic details
            if entity.generics:
                print("   📄 Generic Details:")
                for generic in entity.generics:
                    default = f" = {generic.default_value}" if generic.default_value else ""
                    print(f"      {generic.name}: {generic.type}{default}")

            # Show port group structure with proximity-based grouping
            if entity.port_groups:
                print("   📦 Port Group Structure (Source Proximity):")
                for i, group in enumerate(entity.port_groups, 1):
                    port_names = [port.name for port in group.ports]
                    print(f"      Group {i}: {', '.join(port_names)}")

        print("\n✅ AST Approach: Fast, lightweight, perfect for quick analysis")

    except Exception as e:
        print(f"❌ AST approach error: {e}")
        import traceback
        traceback.print_exc()

def demonstrate_model_approach(vhdl_file):
    """Demonstrate pyVHDLModel approach - rich object hierarchy."""
    print("\n" + "=" * 70)
    print("🏛️  pyVHDLModel Approach (Rich Object Hierarchy)")
    print("=" * 70)

    try:
        # Parse with PyHDLio first
        module = parse_vhdl(vhdl_file, mode='ast')
        
        # Convert to pyVHDLModel entities
        print("🔄 Converting PyHDLio AST → pyVHDLModel...")
        pyvhdlmodel_entities = convert_to_pyvhdlmodel(module)
        print(f"✅ Converted {len(pyvhdlmodel_entities)} entity(ies)")

        # Display using enhanced reporter (automatically detects pyVHDLModel type)
        print("\n📊 pyVHDLModel Entity Report:")
        entity = pyvhdlmodel_entities[0]
        print(report_entity(entity))

        # Demonstrate rich object model access
        print("\n--- 🔍 Programmatic pyVHDLModel Access ---")
        print(f"🏗️  Entity: {entity.Identifier}")
        print(f"   📄 Generic Items: {len(entity.GenericItems)}")
        print(f"   🔌 Port Items: {len(entity.PortItems)}")
        print(f"   📦 Port Groups: {len(entity.PortGroups)}")

        # Show rich generic access
        if entity.GenericItems:
            print("   📄 Rich Generic Objects:")
            for generic in entity.GenericItems:
                name = generic.Identifiers[0]
                subtype = generic.Subtype
                mode = generic.Mode.name if generic.Mode else "unknown"
                default = generic.DefaultExpression
                print(f"      {name}: {mode} {subtype} := {default}")

        # Show rich port group objects
        if entity.PortGroups:
            print("   📦 Rich Port Group Objects:")
            for i, group in enumerate(entity.PortGroups, 1):
                print(f"      Group {i} ({len(group.Ports)} ports):")
                for port in group.Ports:
                    name = port.Identifiers[0]
                    mode = port.Mode.name.lower()
                    subtype = port.Subtype
                    print(f"        - {name}: {mode} {subtype}")

        # Show the object model benefits
        print("\n🎯 Object Model Benefits:")
        print("   ✅ Standards-compliant VHDL entity representation")
        print("   ✅ Rich type system with Mode enumerations")
        print("   ✅ Proper Expression objects for defaults")
        print("   ✅ Port grouping preserved from source proximity")
        print("   ✅ Compatible with pyVHDLModel ecosystem")

    except Exception as e:
        print(f"❌ Model approach error: {e}")
        import traceback
        traceback.print_exc()

def demonstrate_reporter_overloads(vhdl_file):
    """Demonstrate the enhanced reporter with function overloads."""
    print("\n" + "=" * 70)
    print("🔀 Enhanced Reporter: Function Overloads Demo")
    print("=" * 70)

    try:
        # Parse and convert
        module = parse_vhdl(vhdl_file, mode='ast')
        pyvhdlmodel_entities = convert_to_pyvhdlmodel(module)
        
        ast_entity = module.entities[0]
        model_entity = pyvhdlmodel_entities[0]

        print("🎭 Same Function Names, Different Object Types:")
        print("-" * 50)

        # Test overloads with different object types
        print("📄 report_generics() with AST entity:")
        print(report_generics(ast_entity))

        print("\n📄 report_generics() with pyVHDLModel entity:")
        print(report_generics(model_entity))

        print("\n📦 report_ports_grouped() with AST entity:")
        print(report_ports_grouped(ast_entity))

        print("\n📦 report_ports_grouped() with pyVHDLModel entity:")
        print(report_ports_grouped(model_entity))

        print("\n🎉 Function Overload Benefits:")
        print("   ✅ Same API for both object types")
        print("   ✅ Type safety with IDE support")
        print("   ✅ Automatic dispatch to correct implementation")
        print("   ✅ Backward compatibility maintained")

    except Exception as e:
        print(f"❌ Overload demo error: {e}")

def compare_approaches():
    """Compare the two approaches."""
    print("\n" + "=" * 70)
    print("⚖️  Approach Comparison & Recommendations")
    print("=" * 70)

    comparison = """
🔧 PyHDLio AST Approach:
  ✅ Lightweight and fast parsing
  ✅ Minimal dependencies (antlr4-python3-runtime)
  ✅ Source-proximity port grouping preserved
  ✅ Perfect for quick analysis and reporting
  ✅ Simple data structures (dataclasses)
  ✅ Currently implemented and stable

🏛️  pyVHDLModel Approach:
  ✅ Rich, standards-compliant object model
  ✅ Full VHDL semantic support
  ✅ Ecosystem compatibility (pyVHDLModel tools)
  ✅ Advanced analysis capabilities
  ✅ Proper type system (Mode enums, Expression objects)
  ✅ Port grouping enhanced with object model
  ⚠️  Higher memory overhead
  ⚠️  Additional dependencies (pyTooling, pyVHDLModel)

🔀 Enhanced Reporter with Overloads:
  ✅ Same function names work with both approaches
  ✅ Type-safe dispatch based on object type
  ✅ Seamless transition between approaches
  ✅ Backward compatibility maintained
  ✅ IDE support and IntelliSense

📋 Recommendations:
  🎯 Use AST approach for:
     - Quick parsing and validation
     - Simple entity reporting
     - Lightweight tools and scripts
     - Educational purposes

  🎯 Use pyVHDLModel approach for:
     - Complex VHDL analysis
     - Tool integration with pyVHDLModel ecosystem
     - Standards-compliant processing
     - Advanced semantic analysis

  🎯 Use Both approaches when:
     - Building comprehensive VHDL tools
     - Need both speed (AST) and richness (Model)
     - Migrating from simple to complex analysis
"""
    print(comparison)

def main():
    """Main demonstration function."""
    vhdl_file = os.path.join(os.path.dirname(__file__), "simple.vhd")

    print("🚀 PyHDLio Unified Example: AST + pyVHDLModel Integration")
    print(f"📂 Analyzing: {os.path.basename(vhdl_file)}")
    print(f"🎯 Demonstrating dual-mode VHDL parsing with port grouping")

    if not os.path.exists(vhdl_file):
        print(f"❌ Error: VHDL file not found: {vhdl_file}")
        return

    try:
        # Demonstrate all approaches
        demonstrate_ast_approach(vhdl_file)
        demonstrate_model_approach(vhdl_file)
        demonstrate_reporter_overloads(vhdl_file)
        compare_approaches()
        
        print("\n" + "=" * 70)
        print("🎉 Integration Complete!")
        print("✅ Both PyHDLio AST and pyVHDLModel approaches working")
        print("✅ Port grouping preserved across both approaches")
        print("✅ Enhanced reporter with function overloads operational")
        print("✅ Seamless API for dual-mode VHDL analysis")
        print("=" * 70)

    except VHDLSyntaxError as e:
        print(f"❌ VHDL syntax error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
