import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import os

def get_energies(filename):
    data = []
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        system = root.find('system')
        if system is not None:
            for state in system.findall('state'):
                e_val = state.get('E')
                j_val = state.get('J')
                if e_val:
                    data.append((float(e_val), j_val))
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
    return data

def plot_energies(files):
    plt.figure(figsize=(12, 8)) # Increased figure size for labels
    
    # Collect all energies first to find the global minimum
    all_data_per_file = []
    global_min = float('inf')
    
    for filename in files:
        data = get_energies(filename)
        if data:
            energies = [d[0] for d in data]
            current_min = min(energies)
            if current_min < global_min:
                global_min = current_min
            all_data_per_file.append(data)
        else:
            all_data_per_file.append([])
            print(f"No energies found for {filename}")

    if global_min == float('inf'):
        print("No energies found in any file.")
        return

    # Define some x-positions for the scatter/line plot
    
    for i, (filename, data) in enumerate(zip(files, all_data_per_file)):
        if not data:
            continue
            
        # Filter to keep only the first and second energy values for a specific J value
        filtered_data = []
        j_counts = {}
        for e, j in data:
            count = j_counts.get(j, 0)
            if count < 2:
                filtered_data.append((e, j))
                j_counts[j] = count + 1
        
        if not filtered_data:
            continue

        # Normalize energies
        normalized_energies = [d[0] - global_min for d in filtered_data]
        j_values = [d[1] for d in filtered_data]
        
        # Plot each energy as a horizontal line
        x_center = i
        width = 0.4
        x_vals = [x_center - width/2, x_center + width/2]
        
        label_name = os.path.basename(filename)
        
        # Plot the first one with a label for the legend
        plt.plot(x_vals, [normalized_energies[0], normalized_energies[0]], color=f'C{i}', label=label_name)
        if j_values[0]:
            plt.text(x_center + width/2 + 0.05, normalized_energies[0], f'J={j_values[0]}', va='center', fontsize=8)
        
        # Plot the rest
        for e, j in zip(normalized_energies[1:], j_values[1:]):
            plt.plot(x_vals, [e, e], color=f'C{i}')
            if j:
                plt.text(x_center + width/2 + 0.05, e, f'J={j}', va='center', fontsize=8)
            
    plt.xticks(range(len(files)), [os.path.basename(f) for f in files])
    plt.ylabel('Energy (MeV)')
    plt.title(f'Normalized Energy Levels (E - {global_min:.3f})')
    plt.legend()
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Adjust x-axis limits to make room for labels
    plt.xlim(-0.5, len(files) - 0.5 + 0.5) # Add some space on the right
    
    output_file = 'energy_levels.png'
    plt.savefig(output_file)
    print(f"Plot saved to {output_file}")

if __name__ == "__main__":
    files = ['38Cl_fsu9+_merged.xml', '38Cl_fsu9-_merged.xml', '38Cl_fsu9_2hw-_merged.xml', '38Cl_fsu9+3hw_merged.xml']
    # Ensure we are using absolute paths or relative to the script location if running from there
    # The user is in /Users/calemhoffman/Documents/GitHub/cosmo/results/ based on the file paths
    # I will assume the script is run from that directory or I should provide full paths.
    # Let's use full paths to be safe, based on where I'm saving this script.
    
    base_dir = '/Users/calemhoffman/Documents/GitHub/cosmo/results'
    full_paths = [os.path.join(base_dir, f) for f in files]
    
    plot_energies(full_paths)
