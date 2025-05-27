"""
HDLio - Python 3 HDL Parsing Solution
====================================

A Python library for parsing VHDL, Verilog, and SystemVerilog files
using PLY (Python Lex-Yacc) with complete source reconstruction capability.
"""

from .core.hdlio import HDLio
from .core.constants import *

__version__ = "1.0.0"
__author__ = "HDLio Development Team"

# Export main classes and constants
__all__ = [
    'HDLio',
    'VHDL_1993',
    'VHDL_2000',
    'VHDL_2008',
    'VHDL_2019',
    'VERILOG_1995',
    'VERILOG_2001',
    'VERILOG_2005',
    'SYSTEMVERILOG_2005',
    'SYSTEMVERILOG_2009',
    'SYSTEMVERILOG_2012',
    'SYSTEMVERILOG_2017'
]
