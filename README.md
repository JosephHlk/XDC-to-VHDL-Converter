XDC to VHDL Converter
A Python script that converts Xilinx Design Constraint (XDC) files to VHDL entity declarations with optional signal generation and port assignments.

Features
Converts XDC pin constraints to VHDL entity declarations

Supports direction comments (#! or ##!) for automatic port direction detection

Generates internal signals with _Int suffix

Creates automatic assignments between ports and internal signals

Handles both scalar ports and bus ports

Supports all port directions (IN, OUT, INOUT)

Installation
No installation required. Just ensure you have Python 3.x installed on your system.

Usage
bash
python xdc_to_vhdl.py <input.xdc> <output.vhd> [options]

Options
-s, --signals: Generate internal signal declarations with _Int suffix

-as, --assign-signals: Generate both signal declarations and assignments between ports and signals

Examples
Input XDC File Example

tcl
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

Output Examples
1. Basic Conversion (No Options)

bash
python xdc_to_vhdl.py example.xdc example.vhd

Output VHDL (excerpt):

vhdl
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



2. With Signal Generation (-s Option)

bash
python xdc_to_vhdl.py example.xdc example.vhd -s
Output VHDL (excerpt):

vhdl
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
    -- Internal signals with _Int suffix
    signal ADDR_Int : std_logic_vector(1 downto 0) := (others => '0');
    signal BIDIR_PIN_Int : std_logic := '0';
    signal DATA_Int : std_logic_vector(2 downto 0) := (others => '0');
    signal FP_SYS_CLK_Int : std_logic := '0';
    signal READY_Int : std_logic := '0';
begin
    -- Add your logic here
    -- Connect internal signals to ports if needed
end architecture Behavioral;


3. With Signal Generation and Assignments (-as Option)
bash
python xdc_to_vhdl.py example.xdc example.vhd -as

Output VHDL (excerpt):

vhdl
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
    -- Internal signals with _Int suffix
    signal ADDR_Int : std_logic_vector(1 downto 0) := (others => '0');
    signal BIDIR_PIN_Int : std_logic := '0';
    signal DATA_Int : std_logic_vector(2 downto 0) := (others => '0');
    signal FP_SYS_CLK_Int : std_logic := '0';
    signal READY_Int : std_logic := '0';
begin
    -- Port to signal assignments
    ADDR_Int <= ADDR;
    -- inout port BIDIR_PIN requires special handling
    -- BIDIR_PIN_Int <= BIDIR_PIN;
    -- BIDIR_PIN <= BIDIR_PIN_Int when direction_control = '1' else 'Z';
    DATA <= DATA_Int;
    FP_SYS_CLK_Int <= FP_SYS_CLK;
    READY <= READY_Int;

    -- Add your logic here
    -- Logic using internal signals (_Int)
end architecture Behavioral;

Direction Comments
The script recognizes direction comments in the XDC file. Add one of the following comments to each set_property line:

#! IN or ##! IN for input ports

#! OUT or ##! OUT for output ports

#! INOUT or ##! INOUT for bidirectional ports

Example:

tcl
set_property -dict { PACKAGE_PIN R14  IOSTANDARD LVCMOS33 } [get_ports READY]; ##! OUT

Notes
The entity name is derived from the output filename (without the .vhd extension)

All internal signals are initialized to 0

For INOUT ports, the script provides commented templates for proper bidirectional handling

The script only processes set_property lines and ignores other commands like create_clock

If no direction comment is provided, the port direction will be left blank in the VHDL file

License
This script is provided as-is without any warranty. Feel free to modify and use as needed.

Support
For issues or questions, please check the script comments or modify the code to suit your specific needs.