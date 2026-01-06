#!/usr/bin/env python3.11
"""
Enhanced occupancies.py - Flexible nuclear shell model occupation number analyzer

Compares occupation numbers between nuclear states from CoSMo XML output files.
"""

import xml.etree.ElementTree as ET
import argparse
import sys
from pathlib import Path


def parse_xml_state(filename, state_id):
    """
    Extract occupation numbers for a specific state from an XML file.
    
    Args:
        filename (str): Path to XML file
        state_id (int): State ID number to extract
        
    Returns:
        tuple: (state_info dict, occupations dict)
            state_info contains: J, P, T, E, Ex
            occupations: {orbital_name: {'N': float, 'Z': float}}
    """
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        
        # Find the state with wavefunction having matching id
        # ElementTree doesn't support complex XPath predicates, so we iterate
        state = None
        for s in root.findall('.//state'):
            wf = s.find('wavefunction')
            if wf is not None and wf.get('id') == str(state_id):
                state = s
                break
        
        if state is None:
            raise ValueError(f"State with id={state_id} not found in {filename}")
        
        # Extract state information
        state_info = {
            'id': state_id,
            'J': state.get('J'),
            'P': state.get('P'),
            'T': state.get('T'),
            'E': float(state.get('E', 0)),
            'Ex': float(state.get('Ex', 0)),
            'name': state.get('name', f'State {state_id}')
        }
        
        # Extract occupation numbers
        occupations = {}
        for occ in state.findall('occupation'):
            name = occ.get('name')
            occupations[name] = {
                'N': float(occ.get('N')),
                'Z': float(occ.get('Z'))
            }
        
        return state_info, occupations
        
    except ET.ParseError as e:
        print(f"Error parsing XML file {filename}: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {filename}", file=sys.stderr)
        sys.exit(1)


def get_all_states(filename):
    """
    Extract all states from an XML file.
    
    Args:
        filename (str): Path to XML file
        
    Returns:
        list: List of (state_info, occupations) tuples for each state
    """
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        
        states_data = []
        for state in root.findall('.//state'):
            # Get id from wavefunction child element
            wavefunction = state.find('wavefunction')
            if wavefunction is None:
                continue
            
            state_id = wavefunction.get('id')
            if state_id is None:
                continue
                
            state_info = {
                'id': int(state_id),
                'J': state.get('J'),
                'P': state.get('P'),
                'T': state.get('T'),
                'E': float(state.get('E', 0)),
                'Ex': float(state.get('Ex', 0)),
                'name': state.get('name', f'State {state_id}')
            }
            
            occupations = {}
            for occ in state.findall('occupation'):
                name = occ.get('name')
                occupations[name] = {
                    'N': float(occ.get('N')),
                    'Z': float(occ.get('Z'))
                }
            
            states_data.append((state_info, occupations))
        
        return states_data
        
    except ET.ParseError as e:
        print(f"Error parsing XML file {filename}: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {filename}", file=sys.stderr)
        sys.exit(1)


def calculate_differences(base_occupations, compare_occupations):
    """
    Calculate occupation number differences between two states.
    
    Args:
        base_occupations (dict): Reference state occupations
        compare_occupations (dict): Comparison state occupations
        
    Returns:
        dict: {orbital: {'dN': float, 'dZ': float, 'dTotal': float}}
    """
    all_orbitals = sorted(set(base_occupations.keys()) | set(compare_occupations.keys()))
    
    differences = {}
    for orbital in all_orbitals:
        base = base_occupations.get(orbital, {'N': 0.0, 'Z': 0.0})
        comp = compare_occupations.get(orbital, {'N': 0.0, 'Z': 0.0})
        
        dN = comp['N'] - base['N']
        dZ = comp['Z'] - base['Z']
        dTotal = dN + dZ
        
        differences[orbital] = {
            'dN': dN,
            'dZ': dZ,
            'dTotal': dTotal
        }
    
    return differences


def format_table_output(base_info, base_file, comparison_results, compare_file):
    """
    Format comparison results as a nice ASCII table.
    
    Args:
        base_info (dict): Information about the base state
        base_file (str): Base filename
        comparison_results (list): List of (state_info, differences) tuples
        compare_file (str): Comparison filename
    """
    # Print header
    print("=" * 80)
    print(f"Base State: {Path(base_file).stem}")
    print(f"  State: {base_info['name']} (J={base_info['J']}, P={base_info['P']}, "
          f"Ex={base_info['Ex']:.3f} MeV, id={base_info['id']})")
    print("=" * 80)
    print()
    print(f"Comparing to states in: {Path(compare_file).name}")
    print()
    
    # Print each comparison
    for state_info, differences in comparison_results:
        print(f"State id={state_info['id']}: {state_info['name']} "
              f"(J={state_info['J']}, P={state_info['P']}, Ex={state_info['Ex']:.3f} MeV)")
        print("-" * 80)
        
        # Table header
        print(f"{'Orbital':<10} {'ΔN':>12} {'ΔZ':>12} {'ΔTotal':>12}")
        print("-" * 80)
        
        # Filter and sort by |dTotal| to show most significant changes first
        sorted_orbitals = sorted(differences.keys(), 
                                key=lambda x: abs(differences[x]['dTotal']), 
                                reverse=True)
        
        for orbital in sorted_orbitals:
            diff = differences[orbital]
            # Only show if there's a non-negligible difference
            if abs(diff['dTotal']) > 0.001:
                print(f"{orbital:<10} {diff['dN']:>12.6f} {diff['dZ']:>12.6f} {diff['dTotal']:>12.6f}")
        
        print()


def format_csv_output(base_info, base_file, comparison_results, compare_file):
    """
    Format comparison results as CSV.
    """
    # Print CSV header
    print("base_file,base_id,base_state,compare_file,compare_id,compare_state,"
          "compare_J,compare_P,compare_Ex,orbital,dN,dZ,dTotal")
    
    base_state = f"{base_info['name']}(J={base_info['J']}{base_info['P']})"
    
    for state_info, differences in comparison_results:
        compare_state = f"{state_info['name']}(J={state_info['J']}{state_info['P']})"
        
        for orbital, diff in differences.items():
            if abs(diff['dTotal']) > 0.001:
                print(f"{base_file},{base_info['id']},{base_state},"
                      f"{compare_file},{state_info['id']},{compare_state},"
                      f"{state_info['J']},{state_info['P']},{state_info['Ex']:.3f},"
                      f"{orbital},{diff['dN']:.6f},{diff['dZ']:.6f},{diff['dTotal']:.6f}")


def main():
    """Main function with CLI interface."""
    parser = argparse.ArgumentParser(
        description='Compare nuclear state occupation numbers from CoSMo XML files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare all 32Si states against 34S ground state
  python3.11 occupancies.py -b 34S_fsu9-.xml -i 0 -c 32Si_fsu9-.xml
  
  # Compare specific states
  python3.11 occupancies.py -b 32Si_fsu9-.xml -i 0 -c 32Si_fsu9-.xml -o csv
        """
    )
    
    parser.add_argument('-b', '--base', required=True,
                       help='XML file containing the base/reference state')
    parser.add_argument('-i', '--base-id', type=int, required=True,
                       help='State ID number for the base state (e.g., 0 for ground state)')
    parser.add_argument('-c', '--compare', required=True,
                       help='XML file containing states to compare')
    parser.add_argument('-o', '--output', choices=['table', 'csv'], default='table',
                       help='Output format (default: table)')
    parser.add_argument('--threshold', type=float, default=0.001,
                       help='Minimum |ΔTotal| to display (default: 0.001)')
    
    args = parser.parse_args()
    
    # Parse base state
    base_info, base_occupations = parse_xml_state(args.base, args.base_id)
    
    # Parse all comparison states
    comparison_states = get_all_states(args.compare)
    
    if not comparison_states:
        print(f"No states found in {args.compare}", file=sys.stderr)
        sys.exit(1)
    
    # Calculate differences for each comparison state
    comparison_results = []
    for state_info, occupations in comparison_states:
        differences = calculate_differences(base_occupations, occupations)
        comparison_results.append((state_info, differences))
    
    # Output results
    if args.output == 'csv':
        format_csv_output(base_info, args.base, comparison_results, args.compare)
    else:
        format_table_output(base_info, args.base, comparison_results, args.compare)


if __name__ == '__main__':
    main()
