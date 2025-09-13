# XDC to VHDL Converter

A Python script that converts Xilinx Design Constraint (XDC) files to VHDL entity declarations with optional signal generation and port assignments.

## Features

- Converts XDC pin constraints to VHDL entity declarations
- Supports direction comments (`#!` or `##!`) for automatic port direction detection
- Generates internal signals with `_Int` suffix for regular ports
- For INOUT ports, generates separate `_In`, `_Out`, and `_Dir` signals
- Creates automatic assignments between ports and internal signals
- Handles both scalar ports and bus ports
- Supports all port directions (IN, OUT, INOUT)

## Installation

### Windows
1. Download and install Python 3.x from [python.org](https://python.org)
2. Save the Python script as `xdc_to_vhdl.py`
3. Open Command Prompt and navigate to the script directory

### Linux
1. Most Linux distributions come with Python pre-installed
2. If not installed, use your package manager:
   - Ubuntu/Debian: `sudo apt install python3`
   - Fedora/RHEL: `sudo dnf install python3`
3. Save the Python script as `xdc_to_vhdl.py`

## Usage

```bash
python xdc_to_vhdl.py <input.xdc> <output.vhd> [options]
```

### Options

- `-s, --signals`: Generate internal signal declarations
- `-as, --assign-signals`: Generate both signal declarations and assignments between ports and signals

## Examples

### Input XDC File Example

```tcl
# Clock input
set_property -dict { PACKAGE_PIN U18  IOSTANDARD LVCMOS33 } [get_ports FP_SYS_CLK]; #! IN

# Single-bit output
set_property -dict { PACKAGE_PIN R14  IOSTANDARD LVCMOS33 } [get_ports READY]; ##! OUT

# Bus output
set_property -dict { PACKAGE_PIN P14  IOSTANDARD LVCMOS33 } [get_ports {DATA[0]}]; ##! OUT
set_property -dict { PACKAGE_PIN N16  IOSTANDARD LVCMOS33 } [get_ports {DATA[1]}]; #! OUT
set_property -dict { PACKAGE_PIN M14  IOSTANDARD LVCMOS33 } [get_ports {DATA[2]}]; ##! OUT

# Bus input
set_property -dict { PACKAGE_PIN W19  IOSTANDARD LVCMOS33 } [get_ports {ADDR[0]}]; #! IN
set_property -dict { PACKAGE_PIN T19  IOSTANDARD LVCMOS33 } [get_ports {ADDR[1]}]; ##! IN

# Inout port
set_property -dict { PACKAGE_PIN A10  IOSTANDARD LVCMOS33 } [get_ports BIDIR_PIN]; ##! INOUT
```

### Output Examples

#### 1. Basic Conversion (No Options)
```bash
python xdc_to_vhdl.py example.xdc example.vhd
```

**Output VHDL (excerpt):**
```vhdl
entity example is
    Port (
        ADDR : in  std_logic_vector(1 downto 0);
        BIDIR_PIN : inout std_logic;
        DATA : out std_logic_vector(2 downto 0);
        FP_SYS_CLK : in  std_logic;
        READY : out std_logic
    );
end entity example;

architecture Behavioral of example is
    -- Declare internal signals here if needed
begin
    -- Add your logic here
    -- Connect internal signals to ports if needed
end architecture Behavioral;
```

#### 2. With Signal Generation (-s Option)
```bash
python xdc_to_vhdl.py example.xdc example.vhd -s
```

**Output VHDL (excerpt):**
```vhdl
entity example is
    Port (
        ADDR : in  std_logic_vector(1 downto 0);
        BIDIR_PIN : inout std_logic;
        DATA : out std_logic_vector(2 downto 0);
        FP_SYS_CLK : in  std_logic;
        READY : out std_logic
    );
end entity example;

architecture Behavioral of example is
    -- Internal signals
    signal ADDR_Int : std_logic_vector(1 downto 0) := (others => '0');
    signal BIDIR_PIN_In  : std_logic; -- Input from BIDIR_PIN
    signal BIDIR_PIN_Out : std_logic := '0'; -- Output to BIDIR_PIN
    signal BIDIR_PIN_Dir : std_logic := '0'; -- Direction control for BIDIR_PIN (1=output, 0=input)
    signal DATA_Int : std_logic_vector(2 downto 0) := (others => '0');
    signal FP_SYS_CLK_Int : std_logic := '0';
    signal READY_Int : std_logic := '0';
begin
    -- Add your logic here
    -- Connect internal signals to ports if needed
end architecture Behavioral;
```

#### 3. With Signal Generation and Assignments (-as Option)
```bash
python xdc_to_vhdl.py example.xdc example.vhd -as
```

**Output VHDL (excerpt):**
```vhdl
entity example is
    Port (
        ADDR : in  std_logic_vector(1 downto 0);
        BIDIR_PIN : inout std_logic;
        DATA : out std_logic_vector(2 downto 0);
        FP_SYS_CLK : in  std_logic;
        READY : out std_logic
    );
end entity example;

architecture Behavioral of example is
    -- Internal signals
    signal ADDR_Int : std_logic_vector(1 downto 0) := (others => '0');
    signal BIDIR_PIN_In  : std_logic; -- Input from BIDIR_PIN
    signal BIDIR_PIN_Out : std_logic := '0'; -- Output to BIDIR_PIN
    signal BIDIR_PIN_Dir : std_logic := '0'; -- Direction control for BIDIR_PIN (1=output, 0=input)
    signal DATA_Int : std_logic_vector(2 downto 0) := (others => '0');
    signal FP_SYS_CLK_Int : std_logic := '0';
    signal READY_Int : std_logic := '0';
begin
    -- Port to signal assignments
    ADDR_Int <= ADDR;
    -- INOUT port BIDIR_PIN requires special handling
    BIDIR_PIN_In <= BIDIR_PIN;
    BIDIR_PIN <= BIDIR_PIN_Out when BIDIR_PIN_Dir = '1' else 'Z';
    -- Control BIDIR_PIN_Dir to switch between input and output modes
    DATA <= DATA_Int;
    FP_SYS_CLK_Int <= FP_SYS_CLK;
    READY <= READY_Int;

    -- Add your logic here
    -- Logic using internal signals
    -- Example usage for BIDIR_PIN:
    -- BIDIR_PIN_Out <= some_internal_signal; -- Drive output
    -- some_other_signal <= BIDIR_PIN_In;     -- Read input
    -- BIDIR_PIN_Dir <= '1' when output_enable else '0'; -- Control direction
end architecture Behavioral;
```

## Direction Comments

The script recognizes direction comments in the XDC file. Add one of the following comments to each `set_property` line:

- `#! IN` or `##! IN` for input ports
- `#! OUT` or `##! OUT` for output ports  
- `#! INOUT` or `##! INOUT` for bidirectional ports

Example:
```tcl
set_property -dict { PACKAGE_PIN R14  IOSTANDARD LVCMOS33 } [get_ports READY]; ##! OUT
```

## Notes

1. The entity name is derived from the output filename (without the .vhd extension)
2. All internal signals are initialized to 0
3. For INOUT ports, the script generates separate input, output, and direction control signals
4. The script only processes `set_property` lines and ignores other commands like `create_clock`
5. If no direction comment is provided, the port direction will be left blank in the VHDL file

## License

This script is provided as-is without any warranty. Feel free to modify and use as needed.

## Support

For issues or questions, please check the script comments or modify the code to suit your specific needs.
