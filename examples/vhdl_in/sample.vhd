-- Comprehensive VHDL Test File
-- Contains examples of various design units for testing the dump.py example

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

-- ============================================================================
-- CONTEXT DECLARATION
-- ============================================================================
context work_context is
    library ieee;
    use ieee.std_logic_1164.all;
    use ieee.numeric_std.all;
end context work_context;

-- ============================================================================
-- PACKAGE DECLARATION
-- ============================================================================
package utilities_pkg is
    constant DATA_WIDTH : positive := 8;
    constant ADDR_WIDTH : positive := 16;

    type state_type is (IDLE, ACTIVE, DONE);
    type data_array_type is array (natural range <>) of std_logic_vector(DATA_WIDTH-1 downto 0);

    -- Function declaration
    function reverse_bits(input : std_logic_vector) return std_logic_vector;

    -- Component declarations
    component counter is
        generic (
            WIDTH : positive := 8;
            RESET_VALUE : natural := 0
        );
        port (
            clk     : in  std_logic;
            reset   : in  std_logic;
            enable  : in  std_logic;

            count   : out std_logic_vector(WIDTH-1 downto 0);
            overflow: out std_logic
        );
    end component counter;

    component memory is
        generic (
            ADDR_WIDTH : positive := 8;
            DATA_WIDTH : positive := 16
        );
        port (
            clk    : in  std_logic;
            reset  : in  std_logic;

            we     : in  std_logic;
            addr   : in  std_logic_vector(ADDR_WIDTH-1 downto 0);

            din    : in  std_logic_vector(DATA_WIDTH-1 downto 0);
            dout   : out std_logic_vector(DATA_WIDTH-1 downto 0)
        );
    end component memory;

end package utilities_pkg;

-- ============================================================================
-- PACKAGE BODY
-- ============================================================================
package body utilities_pkg is

    function reverse_bits(input : std_logic_vector) return std_logic_vector is
        variable result : std_logic_vector(input'range);
    begin
        for i in input'range loop
            result(i) := input(input'high - i + input'low);
        end loop;
        return result;
    end function reverse_bits;

end package body utilities_pkg;

-- ============================================================================
-- ENTITY DECLARATIONS
-- ============================================================================

-- Simple entity with basic ports
entity simple_gate is
    port (
        a : in  std_logic;
        b : in  std_logic;
        y : out std_logic
    );
end entity simple_gate;

-- Complex entity with generics and grouped ports
entity processor is
    generic (
        DATA_WIDTH    : positive := 32;
        ADDR_WIDTH    : positive := 32;
        CACHE_SIZE    : positive := 1024;
        ENABLE_CACHE  : boolean  := true
    );
    port (
        -- Clock and reset group
        clk           : in  std_logic;
        reset         : in  std_logic;

        -- Instruction interface group
        inst_addr     : out std_logic_vector(ADDR_WIDTH-1 downto 0);
        inst_data     : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        inst_valid    : in  std_logic;
        inst_ready    : out std_logic;

        -- Data interface group
        data_addr     : out std_logic_vector(ADDR_WIDTH-1 downto 0);
        data_rdata    : in  std_logic_vector(DATA_WIDTH-1 downto 0);
        data_wdata    : out std_logic_vector(DATA_WIDTH-1 downto 0);
        data_we       : out std_logic;
        data_valid    : in  std_logic;
        data_ready    : out std_logic;

        -- Control and status group
        interrupt     : in  std_logic_vector(7 downto 0);
        status        : out std_logic_vector(15 downto 0);
        debug_mode    : in  std_logic
    );
end entity processor;

-- ============================================================================
-- ARCHITECTURE DECLARATIONS
-- ============================================================================

architecture behavioral of simple_gate is
begin
    y <= a and b;
end architecture behavioral;

architecture rtl of simple_gate is
begin
    y <= a nand b;
end architecture rtl;

architecture behavioral of processor is

    signal pc : std_logic_vector(ADDR_WIDTH-1 downto 0);
    signal instruction : std_logic_vector(DATA_WIDTH-1 downto 0);
    signal state : state_type;

begin

    -- Simple process for demonstration
    process(clk, reset)
    begin
        if reset = '1' then
            pc <= (others => '0');
            state <= IDLE;
        elsif rising_edge(clk) then
            case state is
                when IDLE =>
                    if inst_valid = '1' then
                        state <= ACTIVE;
                    end if;
                when ACTIVE =>
                    pc <= std_logic_vector(unsigned(pc) + 4);
                    state <= DONE;
                when DONE =>
                    state <= IDLE;
            end case;
        end if;
    end process;

    inst_addr <= pc;
    inst_ready <= '1' when state = IDLE else '0';
    status <= x"DEAD" when debug_mode = '1' else x"BEEF";

end architecture behavioral;

-- ============================================================================
-- CONFIGURATION DECLARATIONS
-- ============================================================================

configuration simple_gate_config of simple_gate is
    for behavioral
    end for;
end configuration simple_gate_config;

configuration processor_config of processor is
    for behavioral
    end for;
end configuration processor_config;