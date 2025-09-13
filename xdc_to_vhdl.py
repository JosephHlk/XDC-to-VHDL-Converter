# python xdc_to_vhdl.py <input.xdc> <output.vhd
#! Use the command line -s or --signals to generate internal signals out of the port names
#! Use the command line -as or --assignments to make the assignments between ports and internal signals

#!/usr/bin/env python3

import re
import sys
import os
import argparse
from collections import defaultdict

def parse_xdc(filename):
    """
    Parses an XDC file and extracts all port names along with their directions from comments.
    Handles both scalar ports (e.g., 'clk') and bus ports (e.g., 'leds[0]').
    Only processes set_property lines to avoid duplicates from other commands like create_clock.
    """
    port_regex = re.compile(r'get_ports\s+{?(\w+)\[(\d+)\]}|get_ports\s+{?(\w+)}?')
    # Updated to recognize both #! and ##! for direction comments
    direction_regex = re.compile(r'\s*#+!\s*(INOUT|IN|OUT)')
    
    ports_dict = defaultdict(list)  # Key: port base name, Value: list of (index, direction) tuples
    scalars = {}                    # Dictionary of scalar port names and their directions

    try:
        with open(filename, 'r') as f:
            for line in f:
                # Skip comment-only lines
                if line.strip().startswith('#'):
                    continue
                    
                # Only process lines that contain set_property to avoid duplicates
                if "set_property" not in line:
                    continue
                    
                # Find direction comment if present
                direction_match = direction_regex.search(line)
                direction = direction_match.group(1).lower() if direction_match else None
                
                # Find all matches for get_ports patterns
                match = port_regex.search(line)
                if match:
                    # Check if it's a bus or a scalar
                    if match.group(1) is not None:
                        # It's a bus: group(1) is base name, group(2) is index
                        base_name = match.group(1)
                        index = int(match.group(2))
                        
                        # Only add if this port+index combination hasn't been processed yet
                        if not any(idx == index for idx, _ in ports_dict[base_name]):
                            ports_dict[base_name].append((index, direction))
                    elif match.group(3) is not None:
                        # It's a scalar
                        port_name = match.group(3)
                        
                        # Only add if this port hasn't been processed yet
                        if port_name not in scalars:
                            scalars[port_name] = direction
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    return ports_dict, scalars

def generate_vhdl_entity(ports_dict, scalars, output_filename, generate_signals=False, generate_assignments=False):
    """
    Generates a complete VHDL entity declaration from the parsed port information.
    Uses direction comments from XDC file to set port directions.
    """
    # Extract entity name from filename (remove extension)
    entity_name = os.path.splitext(os.path.basename(output_filename))[0]
    
    with open(output_filename, 'w') as f:
        # Write VHDL header with standard libraries
        f.write("library IEEE;\n")
        f.write("use IEEE.STD_LOGIC_1164.ALL;\n")
        f.write("use IEEE.NUMERIC_STD.ALL;\n\n")
        f.write("-- Entity generated automatically from XDC file\n")
        f.write("-- Port directions extracted from #! or ##! comments\n")
        f.write(f"entity {entity_name} is\n")
        f.write("    Port (\n")

        # Collect all ports for proper comma/semicolon handling
        all_ports = []
        
        # Process scalar ports
        for port, direction in sorted(scalars.items()):
            dir_str = direction if direction else "   "
            all_ports.append(f"        {port} : {dir_str} std_logic")
        
        # Process bus ports
        for base_name, indices_directions in sorted(ports_dict.items()):
            if indices_directions:
                # Extract just the indices
                indices = [idx for idx, dir in indices_directions]
                indices.sort()
                high_index = max(indices)
                low_index = min(indices)
                
                # Determine direction (use the most common direction if multiple specified)
                directions = [dir for idx, dir in indices_directions if dir]
                direction = max(set(directions), key=directions.count) if directions else None
                dir_str = direction if direction else "   "
                
                # Determine if it's downto or to (assuming downto by convention)
                range_str = f"({high_index} downto {low_index})"
                all_ports.append(f"        {base_name} : {dir_str} std_logic_vector{range_str}")
        
        # Write all ports with proper punctuation
        for i, port_line in enumerate(all_ports):
            if i == len(all_ports) - 1:
                f.write(f"{port_line}\n")
            else:
                f.write(f"{port_line};\n")
        
        f.write("    );\n")
        f.write(f"end entity {entity_name};\n\n")
        
        # Add architecture with internal signals
        f.write(f"architecture Behavioral of {entity_name} is\n")
        
        # Generate signals if requested or if assignments are requested
        if generate_signals or generate_assignments:
            f.write("    -- Internal signals\n")
            
            # Declare internal signals for scalar ports
            for port, direction in sorted(scalars.items()):
                if direction == "inout":
                    # For INOUT ports, create _In, _Out, and _Dir signals
                    f.write(f"    signal {port}_In  : std_logic; -- Input from {port}\n")
                    f.write(f"    signal {port}_Out : std_logic := '0'; -- Output to {port}\n")
                    f.write(f"    signal {port}_Dir : std_logic := '0'; -- Direction control for {port} (1=output, 0=input)\n")
                else:
                    f.write(f"    signal {port}_Int : std_logic := '0';\n")
            
            # Declare internal signals for bus ports
            for base_name, indices_directions in sorted(ports_dict.items()):
                if indices_directions:
                    # Determine direction (use the most common direction if multiple specified)
                    directions = [dir for idx, dir in indices_directions if dir]
                    direction = max(set(directions), key=directions.count) if directions else None
                    
                    indices = [idx for idx, dir in indices_directions]
                    indices.sort()
                    high_index = max(indices)
                    low_index = min(indices)
                    range_str = f"({high_index} downto {low_index})"
                    
                    if direction == "inout":
                        # For INOUT buses, create _In, _Out, and _Dir signals
                        f.write(f"    signal {base_name}_In  : std_logic_vector{range_str}; -- Input from {base_name}\n")
                        f.write(f"    signal {base_name}_Out : std_logic_vector{range_str} := (others => '0'); -- Output to {base_name}\n")
                        f.write(f"    signal {base_name}_Dir : std_logic := '0'; -- Direction control for {base_name} (1=output, 0=input)\n")
                    else:
                        f.write(f"    signal {base_name}_Int : std_logic_vector{range_str} := (others => '0');\n")
        else:
            f.write("    -- Declare internal signals here if needed\n")
        
        f.write("begin\n")
        
        # Generate assignments if requested
        if generate_assignments:
            f.write("    -- Port to signal assignments\n")
            
            # Generate assignments for scalar ports
            for port, direction in sorted(scalars.items()):
                if direction == "in":
                    f.write(f"    {port}_Int <= {port};\n")
                elif direction == "out":
                    f.write(f"    {port} <= {port}_Int;\n")
                elif direction == "inout":
                    f.write(f"    -- INOUT port {port} requires special handling\n")
                    f.write(f"    {port}_In <= {port};\n")
                    f.write(f"    {port} <= {port}_Out when {port}_Dir = '1' else 'Z';\n")
                    f.write(f"    -- Control {port}_Dir to switch between input and output modes\n\n")
                else:
                    f.write(f"    -- Direction not specified for {port}, add assignment manually\n")
            
            # Generate assignments for bus ports
            for base_name, indices_directions in sorted(ports_dict.items()):
                if indices_directions:
                    # Determine direction (use the most common direction if multiple specified)
                    directions = [dir for idx, dir in indices_directions if dir]
                    direction = max(set(directions), key=directions.count) if directions else None
                    
                    if direction == "in":
                        f.write(f"    {base_name}_Int <= {base_name};\n")
                    elif direction == "out":
                        f.write(f"    {base_name} <= {base_name}_Int;\n")
                    elif direction == "inout":
                        f.write(f"    -- INOUT bus {base_name} requires special handling\n")
                        f.write(f"    {base_name}_In <= {base_name};\n")
                        f.write(f"    {base_name} <= {base_name}_Out when {base_name}_Dir = '1' else (others => 'Z');\n")
                        f.write(f"    -- Control {base_name}_Dir to switch between input and output modes\n\n")
                    else:
                        f.write(f"    -- Direction not specified for {base_name}, add assignment manually\n")
            
            f.write("\n")
        
        f.write("    -- Add your logic here\n")
        
        if generate_assignments:
            f.write("    -- Logic using internal signals\n")
            # Add examples for INOUT ports
            for port, direction in sorted(scalars.items()):
                if direction == "inout":
                    f.write(f"    -- Example usage for {port}:\n")
                    f.write(f"    -- {port}_Out <= some_internal_signal; -- Drive output\n")
                    f.write(f"    -- some_other_signal <= {port}_In;     -- Read input\n")
                    f.write(f"    -- {port}_Dir <= '1' when output_enable else '0'; -- Control direction\n\n")
            
            for base_name, indices_directions in sorted(ports_dict.items()):
                if indices_directions:
                    directions = [dir for idx, dir in indices_directions if dir]
                    direction = max(set(directions), key=directions.count) if directions else None
                    if direction == "inout":
                        f.write(f"    -- Example usage for {base_name}:\n")
                        f.write(f"    -- {base_name}_Out <= some_internal_bus; -- Drive output\n")
                        f.write(f"    -- some_other_bus <= {base_name}_In;     -- Read input\n")
                        f.write(f"    -- {base_name}_Dir <= '1' when output_enable else '0'; -- Control direction\n\n")
        else:
            f.write("    -- Connect internal signals to ports if needed\n")
        
        f.write("end architecture Behavioral;\n")

    print(f"Complete VHDL file written to {output_filename}")
    
    # Print summary of directions used
    print("\nDirection summary:")
    for port, direction in sorted(scalars.items()):
        dir_str = direction if direction else "NOT SPECIFIED"
        print(f"  {port}: {dir_str}")
        
    for base_name, indices_directions in sorted(ports_dict.items()):
        directions = [dir for idx, dir in indices_directions if dir]
        direction = max(set(directions), key=directions.count) if directions else "NOT SPECIFIED"
        print(f"  {base_name}: {direction}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Convert XDC file to VHDL entity with optional signal declarations and assignments')
    parser.add_argument('input_file', help='Input XDC file')
    parser.add_argument('output_file', help='Output VHDL file')
    parser.add_argument('-s', '--signals', action='store_true', 
                        help='Generate internal signal declarations')
    parser.add_argument('-as', '--assign-signals', action='store_true', 
                        help='Generate signal declarations and assignments between ports and signals')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output_file
    generate_signals = args.signals
    generate_assignments = args.assign_signals
    
    # If assignments are requested, signals are also needed
    if generate_assignments:
        generate_signals = True

    bus_ports, scalar_ports = parse_xdc(input_file)
    generate_vhdl_entity(bus_ports, scalar_ports, output_file, generate_signals, generate_assignments)