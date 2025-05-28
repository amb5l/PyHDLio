"""
HDLio - Python 3 HDL Parsing Solution
====================================

A Python library for parsing VHDL, Verilog, and SystemVerilog files
using PLY (Python Lex-Yacc) with complete source reconstruction capability.
"""

from .core.hdlio import HDLio
from .core.constants import (
    HDL_LRM,
    VHDL_1993, VHDL_2000, VHDL_2008, VHDL_2019,
    Verilog_1995, Verilog_2001, Verilog_2005,
    SystemVerilog_2005, SystemVerilog_2009, SystemVerilog_2012, SystemVerilog_2017
)

__version__ = "1.0.0"
__author__ = "HDLio Development Team"

# Export main classes and constants
__all__ = [
    'HDLio',
    'HDL_LRM',
    'VHDL_1993',
    'VHDL_2000',
    'VHDL_2008',
    'VHDL_2019',
    'Verilog_1995',
    'Verilog_2001',
    'Verilog_2005',
    'SystemVerilog_2005',
    'SystemVerilog_2009',
    'SystemVerilog_2012',
    'SystemVerilog_2017'
]
