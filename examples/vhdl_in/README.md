# PyHDLio `vhdl_in` Example

This directory contains a simple VHDL input example. A VHDL file is parsed and converted to an object hierarchy. Basic information about its design units is then printed. Entity and compoenent declarations are elaborated, with generics and ports listed. Note that port groups are inferred from source proximity (a group boundary occurs where there are one or more consecutive lines without port clauses).

## Files

- **`vhdl_in.py`** - Example code
- **`sample.vhd`** - Sample VHDL source with various design units
- **`README.md`** - This documentation

## Usage

```bash
python vhdl_in.py sample.vhd
```

## Output
```
Document instance created from: sample.vhd

  Contexts : 0

  Entities : 2

    Entity: simple_gate
      Generics: 0
      Ports: 3
        a: std_logic
        b: std_logic
        y: std_logic
      Port Groups: 1
        Group1: 3 ports
          a: std_logic
          b: std_logic
          y: std_logic

    Entity: processor
      Generics: 4
        DATA_WIDTH: positive
        ADDR_WIDTH: positive
        CACHE_SIZE: positive
        ENABLE_CACHE: boolean
      Ports: 15
        clk: std_logic
        reset: std_logic
        inst_addr: std_logic_vector(ADDR_WIDTH - 1 downto 0)
        inst_data: std_logic_vector(DATA_WIDTH - 1 downto 0)
        inst_valid: std_logic
        inst_ready: std_logic
        data_addr: std_logic_vector(ADDR_WIDTH - 1 downto 0)
        data_rdata: std_logic_vector(DATA_WIDTH - 1 downto 0)
        data_wdata: std_logic_vector(DATA_WIDTH - 1 downto 0)
        data_we: std_logic
        data_valid: std_logic
        data_ready: std_logic
        interrupt: std_logic_vector(7 downto 0)
        status: std_logic_vector(15 downto 0)
        debug_mode: std_logic
      Port Groups: 4
        Group1: 2 ports
          clk: std_logic
          reset: std_logic
        Group2: 4 ports
          inst_addr: std_logic_vector(ADDR_WIDTH - 1 downto 0)
          inst_data: std_logic_vector(DATA_WIDTH - 1 downto 0)
          inst_valid: std_logic
          inst_ready: std_logic
        Group3: 6 ports
          data_addr: std_logic_vector(ADDR_WIDTH - 1 downto 0)
          data_rdata: std_logic_vector(DATA_WIDTH - 1 downto 0)
          data_wdata: std_logic_vector(DATA_WIDTH - 1 downto 0)
          data_we: std_logic
          data_valid: std_logic
          data_ready: std_logic
        Group4: 3 ports
          interrupt: std_logic_vector(7 downto 0)
          status: std_logic_vector(15 downto 0)
          debug_mode: std_logic

  Architectures : 0

  Configurations : 0

  Packages : 1

    Package: utilities_pkg

      Components: 2
        Component: counter
          Generics: 2
          WIDTH: positive
          RESET_VALUE: natural
          Ports: 5
          clk: std_logic
          reset: std_logic
          enable: std_logic
          count: std_logic_vector(WIDTH - 1 downto 0)
          overflow: std_logic
          Port Groups: 1
          Group1: 5 ports
            clk: std_logic
            reset: std_logic
            enable: std_logic
            count: std_logic_vector(WIDTH - 1 downto 0)
            overflow: std_logic

        Component: memory
          Generics: 2
          ADDR_WIDTH: positive
          DATA_WIDTH: positive
          Ports: 6
          clk: std_logic
          reset: std_logic
          we: std_logic
          addr: std_logic_vector(ADDR_WIDTH - 1 downto 0)
          din: std_logic_vector(DATA_WIDTH - 1 downto 0)
          dout: std_logic_vector(DATA_WIDTH - 1 downto 0)
          Port Groups: 1
          Group1: 6 ports
            clk: std_logic
            reset: std_logic
            we: std_logic
            addr: std_logic_vector(ADDR_WIDTH - 1 downto 0)
            din: std_logic_vector(DATA_WIDTH - 1 downto 0)
            dout: std_logic_vector(DATA_WIDTH - 1 downto 0)


  Package Bodies : 0
```
