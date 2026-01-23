#!/usr/bin/env python3.11
"""
Merge CoSMo XML files with duplicate detection and energy renormalization.

Merges two CoSMo shell model XML files, removing duplicate states based on
absolute energy matching and renormalizing excitation energies.
"""

import xml.etree.ElementTree as ET
import argparse
from copy import deepcopy


def parse_states(filename):
    """
    Extract all states from an XML file.
    
    Returns:
        tuple: (tree, root, system_element, list of state elements)
    """
    tree = ET.parse(filename)
    root = tree.getroot()
    system = root.find('.//system')
    
    if system is None:
        raise ValueError(f"No <system> element found in {filename}")
    
    states = system.findall('state')
    return tree, root, system, states


def are_duplicates(state1, state2, tolerance=0.001):
    """
    Check if two states are duplicates based on energy.
    
    Args:
        state1, state2: XML state elements
        tolerance: Energy difference tolerance in MeV
        
    Returns:
        bool: True if states are duplicates
    """
    try:
        E1 = float(state1.get('E'))
        E2 = float(state2.get('E'))
        return abs(E1 - E2) < tolerance
    except (TypeError, ValueError):
        return False


def merge_states(states1, states2, tolerance=0.001):
    """
    Merge two lists of states, removing duplicates.
    
    Args:
        states1: List of state elements from file 1 (priority)
        states2: List of state elements from file 2
        tolerance: Energy tolerance for duplicate detection
        
    Returns:
        list: Merged list of unique states
    """
    merged = list(states1)  # Start with all states from file 1
    duplicates_found = 0
    
    for state2 in states2:
        is_duplicate = False
        for state1 in states1:
            if are_duplicates(state1, state2, tolerance):
                is_duplicate = True
                E1 = float(state1.get('E'))
                E2 = float(state2.get('E'))
                J1 = state1.get('J')
                J2 = state2.get('J')
                print(f"  Duplicate found: J={J2}, E={E2:.3f} MeV (matches J={J1}, E={E1:.3f} MeV)")
                duplicates_found += 1
                break
        
        if not is_duplicate:
            merged.append(deepcopy(state2))
    
    print(f"\nTotal duplicates removed: {duplicates_found}")
    return merged


def renormalize_and_sort(states):
    """
    Renormalize Ex values and sort states by energy.
    
    Args:
        states: List of state elements
        
    Returns:
        list: Sorted states with renormalized Ex values
    """
    # Find minimum energy
    energies = [float(s.get('E')) for s in states]
    E_min = min(energies)
    
    print(f"\nGlobal ground state energy: {E_min:.3f} MeV")
    
    # Renormalize Ex values
    for state in states:
        E = float(state.get('E'))
        Ex_new = E - E_min
        state.set('Ex', f"{Ex_new:.3f}")
    
    # Sort by energy
    sorted_states = sorted(states, key=lambda s: float(s.get('E')))
    
    # Reassign sequential IDs
    for i, state in enumerate(sorted_states):
        state.set('id', str(i))
        # Update wavefunction id as well
        wf = state.find('wavefunction')
        if wf is not None:
            wf.set('id', str(i))
    
    return sorted_states


def create_merged_xml(input_files, output_file, tolerance=0.001):
    """
    Create merged XML file from multiple input files.
    
    Args:
        input_files: List of paths to XML files
        output_file: Path for output merged file
        tolerance: Energy tolerance for duplicate detection (MeV)
    """
    if not input_files:
        print("No input files provided.")
        return

    print(f"Merging {len(input_files)} files -> {output_file}")
    print(f"Energy tolerance: {tolerance} MeV\n")
    
    # Parse the first file for header and initial states
    file1 = input_files[0]
    tree1, root1, system1, merged_states = parse_states(file1)
    print(f"Initial file: {file1} ({len(merged_states)} states)")

    total_duplicates = 0

    # Iteratively merge subsequent files
    for file_next in input_files[1:]:
        _, _, _, states_next = parse_states(file_next)
        print(f"Merging {file_next} ({len(states_next)} states)...")
        
        duplicates_this_file = 0
        for state_next in states_next:
            is_duplicate = False
            for state_merged in merged_states:
                if are_duplicates(state_merged, state_next, tolerance):
                    is_duplicate = True
                    E_merged = float(state_merged.get('E'))
                    E_next = float(state_next.get('E'))
                    J_merged = state_merged.get('J')
                    J_next = state_next.get('J')
                    print(f"  Duplicate found: J={J_next}, E={E_next:.3f} MeV (matches J={J_merged}, E={E_merged:.3f} MeV)")
                    duplicates_this_file += 1
                    total_duplicates += 1
                    break
            
            if not is_duplicate:
                merged_states.append(deepcopy(state_next))
        
        print(f"  States added after de-duplication: {len(states_next) - duplicates_this_file}")

    print(f"\nTotal unique states: {len(merged_states)}")
    print(f"Total duplicates removed: {total_duplicates}")
    
    # Renormalize and sort
    sorted_states = renormalize_and_sort(merged_states)
    
    # Create output XML using file1 as template
    output_root = deepcopy(root1)
    output_system = output_root.find('.//system')
    
    # Remove all existing states
    for state in output_system.findall('state'):
        output_system.remove(state)
    
    # Add merged states
    for state in sorted_states:
        output_system.append(state)
    
    # Update system name to indicate merge
    original_name = output_system.get('name', '')
    output_system.set('name', f"{original_name}_merged")
    
    # Write output
    output_tree = ET.ElementTree(output_root)
    ET.indent(output_tree, space='\t', level=0)
    output_tree.write(output_file, encoding='utf-8', xml_declaration=True)
    
    print(f"\nMerged file written to: {output_file}")
    
    # Print summary statistics
    print("\n" + "="*60)
    print("MERGE SUMMARY")
    print("="*60)
    
    from collections import Counter
    j_counts = Counter([s.get('J') for s in sorted_states])
    
    print(f"\nTotal states: {len(sorted_states)}")
    print("\nStates by J:")
    for j in sorted(j_counts.keys(), key=lambda x: float(x) if '/' not in x else float(x.split('/')[0])/float(x.split('/')[1])):
        print(f"  J={j}: {j_counts[j]} states")
    
    # Show energy range
    E_values = [float(s.get('E')) for s in sorted_states]
    Ex_values = [float(s.get('Ex')) for s in sorted_states]
    print(f"\nEnergy range:")
    print(f"  E: {min(E_values):.3f} to {max(E_values):.3f} MeV")
    print(f"  Ex: {min(Ex_values):.3f} to {max(Ex_values):.3f} MeV")


def main():
    """Main function with CLI."""
    parser = argparse.ArgumentParser(
        description='Merge multiple CoSMo XML files with duplicate detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python3.11 merge_xml.py 38Cl_fsu9+.xml 38Cl_fsu9+_J5.xml 38Cl_fsu9+_J8.xml -o 38Cl_fsu9+_merged.xml
        """
    )
    
    parser.add_argument('input_files', nargs='+', help='XML files to merge')
    parser.add_argument('-o', '--output', required=True,
                       help='Output merged XML file')
    parser.add_argument('-t', '--tolerance', type=float, default=0.001,
                       help='Energy tolerance for duplicate detection in MeV (default: 0.001)')
    
    args = parser.parse_args()
    
    create_merged_xml(args.input_files, args.output, args.tolerance)



if __name__ == '__main__':
    main()
