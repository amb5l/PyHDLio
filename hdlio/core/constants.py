"""
HDL Language Reference Manual (LRM) Constants
"""

from enum import Enum


class HDL_LRM(Enum):
    VHDL_1993          = "VHDL_1993"
    VHDL_2000          = "VHDL_2000"
    VHDL_2008          = "VHDL_2008"
    VHDL_2019          = "VHDL_2019"
    Verilog_1995       = "Verilog_1995"
    Verilog_2001       = "Verilog_2001"
    Verilog_2005       = "Verilog_2005"
    SystemVerilog_2005 = "SystemVerilog_2005"
    SystemVerilog_2009 = "SystemVerilog_2009"
    SystemVerilog_2012 = "SystemVerilog_2012"
    SystemVerilog_2017 = "SystemVerilog_2017"


# Convenience constants
VHDL_1993          = HDL_LRM.VHDL_1993
VHDL_2000          = HDL_LRM.VHDL_2000
VHDL_2008          = HDL_LRM.VHDL_2008
VHDL_2019          = HDL_LRM.VHDL_2019
Verilog_1995       = HDL_LRM.Verilog_1995
Verilog_2001       = HDL_LRM.Verilog_2001
Verilog_2005       = HDL_LRM.Verilog_2005
SystemVerilog_2005 = HDL_LRM.SystemVerilog_2005
SystemVerilog_2009 = HDL_LRM.SystemVerilog_2009
SystemVerilog_2012 = HDL_LRM.SystemVerilog_2012
SystemVerilog_2017 = HDL_LRM.SystemVerilog_2017

# Version group constants for parser factory
VHDL_VERSIONS = (VHDL_1993, VHDL_2000, VHDL_2008, VHDL_2019)
VERILOG_VERSIONS = (Verilog_1995, Verilog_2001, Verilog_2005)
SYSTEMVERILOG_VERSIONS = (SystemVerilog_2005, SystemVerilog_2009, SystemVerilog_2012, SystemVerilog_2017)
