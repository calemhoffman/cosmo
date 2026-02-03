import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import os

def get_yrast_state(filename, target_j):
    tree = ET.parse(filename)
    root = tree.getroot()
    states = []
    for state in root.findall('.//state'):
        if state.get('J') == str(target_j):
            states.append(state)
    
    if not states:
        return None
        
    # Find the one with minimum E (Yrast)
    yrast = min(states, key=lambda s: float(s.get('E')))
    
    occupations = {}
    for occ in yrast.findall('occupation'):
        name = occ.get('name')
        occupations[name] = {
            'N': float(occ.get('N')),
            'Z': float(occ.get('Z'))
        }
    return yrast.get('name'), occupations

def plot_comparison():
    filename = '/Users/calemhoffman/Documents/GitHub/cosmo/results/38Cl_fsu9-_merged.xml'
    j6_name, j6_occ = get_yrast_state(filename, 6)
    j7_name, j7_occ = get_yrast_state(filename, 7)
    
    if not j6_occ or not j7_occ:
        print("Could not find yrast states for J=6 or J=7")
        return

    # Use orbitals that are in either (should be same for both)
    orbitals = sorted(list(set(j6_occ.keys()) | set(j7_occ.keys())))
    
    # Filter out core orbitals if they are constant (optional, but let's show all)
    # Let's filter out ones where both are nearly 0 or full if there are too many, 
    # but 38Cl valence space is small.
    
    n6 = [j6_occ[orb]['N'] for orb in orbitals]
    z6 = [j6_occ[orb]['Z'] for orb in orbitals]
    
    n7 = [j7_occ[orb]['N'] for orb in orbitals]
    z7 = [j7_occ[orb]['Z'] for orb in orbitals]
    
    dn = [n7[i] - n6[i] for i in range(len(orbitals))]
    dz = [z7[i] - z6[i] for i in range(len(orbitals))]
    
    x = np.arange(len(orbitals))
    width = 0.35
    
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # J=6 Plot
    axes[0].bar(x - width/2, n6, width, label='Neutrons (N)', color='skyblue')
    axes[0].bar(x + width/2, z6, width, label='Protons (Z)', color='salmon')
    axes[0].set_title(f'Yrast {j6_name} Occupancies')
    axes[0].set_ylabel('Occupation Number')
    axes[0].legend()
    axes[0].grid(axis='y', linestyle='--', alpha=0.7)
    
    # J=7 Plot
    axes[1].bar(x - width/2, n7, width, label='Neutrons (N)', color='skyblue')
    axes[1].bar(x + width/2, z7, width, label='Protons (Z)', color='salmon')
    axes[1].set_title(f'Yrast {j7_name} Occupancies')
    axes[1].set_ylabel('Occupation Number')
    axes[1].legend()
    axes[1].grid(axis='y', linestyle='--', alpha=0.7)
    
    # Difference Plot
    axes[2].bar(x - width/2, dn, width, label='ΔN (J=7 - J=6)', color='blue', alpha=0.6)
    axes[2].bar(x + width/2, dz, width, label='ΔZ (J=7 - J=6)', color='red', alpha=0.6)
    axes[2].axhline(0, color='black', linewidth=0.8)
    axes[2].set_title('Occupancy Differences (J=7 - J=6)')
    axes[2].set_ylabel('Difference')
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(orbitals, rotation=45)
    axes[2].legend()
    axes[2].grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.tight_layout()
    output_png = 'occupancy_comparison_6_7.png'
    plt.savefig(output_png)
    print(f"Plot saved to {output_png}")

if __name__ == "__main__":
    plot_comparison()
