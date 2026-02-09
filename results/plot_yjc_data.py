import plotly.graph_objects as go
import os
import re
import xml.etree.ElementTree as ET

def parse_jpi(jpi_str):
    """
    Parse Jπ string from YJC data.
    Returns: (J, parity, is_tentative)
    - J: spin value (float or None)
    - parity: '+', '-', or None
    - is_tentative: True if assignment is in parentheses
    """
    if not jpi_str or jpi_str.strip() == '()':
        return None, None, False
    
    # Remove whitespace
    jpi_str = jpi_str.strip()
    
    # Check if tentative (has parentheses)
    is_tentative = '(' in jpi_str
    
    # Remove all parentheses for parsing
    jpi_clean = jpi_str.replace('(', '').replace(')', '')
    
    if not jpi_clean:
        return None, None, False
    
    # Extract parity (last character should be + or -)
    parity = None
    if jpi_clean.endswith('+'):
        parity = '+'
        jpi_clean = jpi_clean[:-1]
    elif jpi_clean.endswith('-'):
        parity = '-'
        jpi_clean = jpi_clean[:-1]
    
    # Extract J (remaining should be a number)
    j = None
    if jpi_clean:
        try:
            j = float(jpi_clean)
        except ValueError:
            pass
    
    return j, parity, is_tentative

def get_states_from_xml(filename):
    """Parse XML file to extract calculated states."""
    states = []
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        system = root.find('system')
        if system is not None:
            parity = system.get('P')
            source = 'fsu9'
            if '2hw' in filename:
                source = 'fsu9_2hw'
            elif '3hw' in filename:
                source = 'fsu9_3hw'
                
            for state in system.findall('state'):
                e_val = state.get('E')
                j_val = state.get('J')
                name = state.get('name')
                if e_val:
                    states.append({
                        'E': float(e_val),
                        'J': float(j_val),
                        'P': parity,
                        'name': name,
                        'source': source
                    })
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
    return states

def parse_yjc_file(filename):
    """
    Parse the YJC ASCII GLS file.
    Returns list of level dictionaries.
    """
    levels = []
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Find where level data starts (after "** Level   Energy" header)
    level_start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith('** Level   Energy'):
            level_start_idx = i + 2  # Skip header and ++ line
            break
    
    if level_start_idx is None:
        print("Could not find level data in file")
        return levels
    
    # Parse level data
    i = level_start_idx
    while i < len(lines):
        line = lines[i].strip()
        
        # Stop at band data section
        if line.startswith('** Band'):
            break
        
        # Skip ++ continuation lines and empty lines
        if line.startswith('++') or not line:
            i += 1
            continue
        
        # Parse level line
        parts = line.split()
        if len(parts) >= 4:
            try:
                level_num = int(parts[0])
                energy_kev = float(parts[1])
                energy_err = float(parts[2])
                jpi_str = parts[3]
                
                j, parity, is_tentative = parse_jpi(jpi_str)
                
                levels.append({
                    'level': level_num,
                    'energy_kev': energy_kev,
                    'energy_mev': energy_kev / 1000.0,
                    'error': energy_err,
                    'jpi_str': jpi_str,
                    'J': j,
                    'parity': parity,
                    'is_tentative': is_tentative
                })
            except (ValueError, IndexError) as e:
                print(f"Error parsing line {i}: {line}")
                print(f"  Error: {e}")
        
        i += 1
    
    return levels

def create_parity_plot(levels, parity_filter, theory_states, output_basename):
    """
    Create a plot for a specific parity.
    parity_filter: '+' or '-'
    theory_states: list of calculated states from XML files
    """
    fig = go.Figure()
    
    # Color scheme
    if parity_filter == '+':
        definite_color = '#00CED1'  # Cyan
        tentative_color = '#7FFFD4'  # Lighter cyan
    else:  # '-'
        definite_color = '#FF00FF'  # Magenta
        tentative_color = '#FF69B4'  # Lighter magenta
    
    unknown_color = '#808080'  # Grey
    
    # Plot theory yrast lines first (so they appear behind experimental data)
    if theory_states:
        # Group by source and parity
        for source in ['fsu9', 'fsu9_2hw', 'fsu9_3hw']:
            source_states = [s for s in theory_states if s['source'] == source and s['P'] == parity_filter]
            if not source_states:
                continue
            
            # Sort by J
            source_states.sort(key=lambda x: x['J'])
            
            # Line style based on source
            if source == 'fsu9':
                line_style = dict(width=2, dash='solid')
                source_label = 'FSU9 0ħω'
            elif source == 'fsu9_2hw':
                line_style = dict(width=2, dash='dash')
                source_label = 'FSU9 2ħω'
            else:  # fsu9_3hw
                line_style = dict(width=2, dash='dot')
                source_label = 'FSU9 3ħω'
            
            fig.add_trace(go.Scatter(
                x=[s['J'] for s in source_states],
                y=[s['Ex'] for s in source_states],
                mode='lines',
                name=f'{source_label} π={parity_filter}',
                line=dict(color=definite_color, **line_style),
                hoverinfo='text',
                hovertext=[f"{s['name']}<br>Ex: {s['Ex']:.3f} MeV<br>J: {s['J']}" for s in source_states],
                legendgroup=f'theory_{source}'
            ))
    
    # Separate experimental levels by assignment type
    definite = [l for l in levels if l['parity'] == parity_filter and not l['is_tentative']]
    tentative = [l for l in levels if l['parity'] == parity_filter and l['is_tentative']]
    unknown = [l for l in levels if l['parity'] is None]
    
    # Plot definite assignments
    if definite:
        fig.add_trace(go.Scatter(
            x=[l['J'] for l in definite],
            y=[l['energy_mev'] for l in definite],
            mode='markers',
            name=f'Exp Definite π={parity_filter}',
            marker=dict(
                size=12,
                color=definite_color,
                symbol='circle',
                line=dict(width=2, color='white')
            ),
            hoverinfo='text',
            hovertext=[f"J={l['J']}{parity_filter}<br>E={l['energy_mev']:.3f} MeV<br>Level {l['level']}" 
                      for l in definite]
        ))
    
    # Plot tentative assignments
    if tentative:
        fig.add_trace(go.Scatter(
            x=[l['J'] for l in tentative],
            y=[l['energy_mev'] for l in tentative],
            mode='markers',
            name=f'Tentative π={parity_filter}',
            marker=dict(
                size=12,
                color=tentative_color,
                symbol='circle-open',
                line=dict(width=2, color=tentative_color)
            ),
            hoverinfo='text',
            hovertext=[f"({l['J']}{parity_filter})<br>E={l['energy_mev']:.3f} MeV<br>Level {l['level']}" 
                      for l in tentative]
        ))
    
    # Plot unknown parity (shown on both plots)
    if unknown:
        fig.add_trace(go.Scatter(
            x=[l['J'] if l['J'] is not None else 0 for l in unknown],
            y=[l['energy_mev'] for l in unknown],
            mode='markers',
            name='Unknown π',
            marker=dict(
                size=10,
                color=unknown_color,
                symbol='diamond',
                line=dict(width=1, color='white')
            ),
            hoverinfo='text',
            hovertext=[f"{l['jpi_str']}<br>E={l['energy_mev']:.3f} MeV<br>Level {l['level']}" 
                      for l in unknown]
        ))
    
    # Update layout
    parity_symbol = '+' if parity_filter == '+' else '−'
    fig.update_layout(
        title=dict(
            text=f"<sup>38</sup>Cl Energy Levels (π = {parity_symbol})",
            font=dict(size=24, color='white')
        ),
        xaxis=dict(
            title="Spin (J)",
            gridcolor='rgba(255,255,255,0.1)',
            dtick=1,
            range=[-0.5, 12.5]
        ),
        yaxis=dict(
            title="Excitation Energy (MeV)",
            gridcolor='rgba(255,255,255,0.1)',
            zerolinecolor='rgba(255,255,255,0.5)'
        ),
        plot_bgcolor='#1e1e1e',
        paper_bgcolor='#1e1e1e',
        font=dict(color='white'),
        legend=dict(
            bgcolor='rgba(0,0,0,0.5)',
            bordercolor='rgba(255,255,255,0.3)',
            borderwidth=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Save outputs
    base_dir = '/Users/calemhoffman/Documents/GitHub/cosmo/results'
    
    output_html = os.path.join(base_dir, f'{output_basename}.html')
    fig.write_html(output_html)
    print(f"Saved HTML: {output_html}")
    
    try:
        output_png = os.path.join(base_dir, f'{output_basename}.png')
        fig.write_image(output_png, scale=2)
        print(f"Saved PNG: {output_png}")
    except Exception as e:
        print(f"Could not save PNG: {e}")

def main():
    base_dir = '/Users/calemhoffman/Documents/GitHub/cosmo/results'
    yjc_file = os.path.join(base_dir, '38Cl_yjc.txt')
    
    # XML files for theory
    xml_files = [
        os.path.join(base_dir, '38Cl_fsu9+_merged.xml'),
        os.path.join(base_dir, '38Cl_fsu9-_merged.xml'),
        os.path.join(base_dir, '38Cl_fsu9_2hw-_merged.xml'),
    ]
    
    # Check for 3hw file
    xml_3hw = os.path.join(base_dir, '38Cl_fsu9+3hw_merged.xml')
    if os.path.exists(xml_3hw):
        xml_files.append(xml_3hw)
    
    print("Parsing theory XML files...")
    all_calc_states = []
    for f in xml_files:
        if os.path.exists(f):
            all_calc_states.extend(get_states_from_xml(f))
            print(f"  Loaded: {os.path.basename(f)}")
    
    if all_calc_states:
        # Find global ground state and calculate excitation energies
        global_min_e = min(s['E'] for s in all_calc_states)
        print(f"Theory ground state: {global_min_e:.3f} MeV")
        
        for s in all_calc_states:
            s['Ex'] = s['E'] - global_min_e
        
        # Group by (J, P, source) and keep only yrast (lowest) for each
        grouped = {}
        for s in all_calc_states:
            key = (s['J'], s['P'], s['source'])
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(s)
        
        yrast_states = []
        for key, group in grouped.items():
            group.sort(key=lambda x: x['E'])
            yrast_states.append(group[0])
        
        print(f"Theory yrast states: {len(yrast_states)}")
    else:
        yrast_states = []
        print("No theory data loaded")
    
    print("\nParsing YJC experimental data...")
    levels = parse_yjc_file(yjc_file)
    
    print(f"\nParsed {len(levels)} experimental levels:")
    print(f"  Positive parity: {len([l for l in levels if l['parity'] == '+'])}")
    print(f"  Negative parity: {len([l for l in levels if l['parity'] == '-'])}")
    print(f"  Unknown parity: {len([l for l in levels if l['parity'] is None])}")
    
    # Create separate plots
    print("\nCreating negative parity plot...")
    create_parity_plot(levels, '-', yrast_states, '38Cl_yjc_negative')
    
    print("\nCreating positive parity plot...")
    create_parity_plot(levels, '+', yrast_states, '38Cl_yjc_positive')
    
    print("\nDone!")

if __name__ == "__main__":
    main()
