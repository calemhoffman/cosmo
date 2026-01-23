import xml.etree.ElementTree as ET
import plotly.graph_objects as go
import os
import csv
import re

def get_states_from_xml(filename):
    states = []
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
        system = root.find('system')
        if system is not None:
            parity = system.get('P')
            for state in system.findall('state'):
                e_val = state.get('E')
                j_val = state.get('J')
                name = state.get('name')
                if e_val:
                    states.append({
                        'E': float(e_val),
                        'J': float(j_val),
                        'P': parity,
                        'name': name
                    })
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
    return states

def parse_spin_parity(sp_str):
    """
    Parses strings like '(11+)', '11+', '2-', '4-', '3-/5-'
    Returns (J, P) or None
    """
    if not sp_str or sp_str == '-':
        return None
    
    # Handle multiple assignments by taking the first one
    sp_str = sp_str.split('/')[0]
    
    # Extract J and P
    # Matches optional parenthesis, then float/int, then + or -
    match = re.search(r'\(?(\d+\.?\d*)([+-])\)?', sp_str)
    if match:
        j = float(match.group(1))
        p = match.group(2)
        return j, p
    return None

def get_experimental_states(filename):
    exp_states = []
    try:
        with open(filename, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                energy_str = row.get('Energy (keV)')
                sp_str = row.get('Spin-Parity (Jπ)')
                
                if not energy_str or not sp_str:
                    continue
                
                # Handle cases like "755 / 671"
                energy_val = energy_str.split('/')[0].strip()
                try:
                    energy_mev = float(energy_val) / 1000.0
                except ValueError:
                    continue
                
                jp = parse_spin_parity(sp_str)
                if jp:
                    j, p = jp
                    exp_states.append({
                        'Ex': energy_mev,
                        'J': j,
                        'P': p,
                        'name': f"Exp {sp_str} ({energy_mev:.3f} MeV)",
                        'type': 'Exp'
                    })
    except Exception as e:
        print(f"Error parsing CSV {filename}: {e}")
    return exp_states

def plot_38Cl_states():
    base_dir = '/Users/calemhoffman/Documents/GitHub/cosmo/results'
    csv_file = '/Users/calemhoffman/.gemini/antigravity/brain/d9180346-defa-482e-b008-5e3341560215/spin_data.csv'
    
    xml_files = [
        os.path.join(base_dir, '38Cl_fsu9+_merged.xml'),
        os.path.join(base_dir, '38Cl_fsu9-_merged.xml')
    ]

    all_calc_states = []
    for f in xml_files:
        all_calc_states.extend(get_states_from_xml(f))

    if not all_calc_states:
        print("No calculated states found.")
        return

    # Find global ground state energy for calculated states
    global_min_e = min(s['E'] for s in all_calc_states)
    print(f"Calculated Global Ground State Energy: {global_min_e:.3f} MeV")

    for s in all_calc_states:
        s['Ex'] = s['E'] - global_min_e
        s['type'] = 'Calc'

    # Filter Calculated: Lowest two energy states for each (J, P)
    grouped_calc = {}
    for s in all_calc_states:
        key = (s['J'], s['P'])
        if key not in grouped_calc:
            grouped_calc[key] = []
        grouped_calc[key].append(s)

    filtered_calc = []
    lowest_calc_per_jp = {} # For line connections
    
    for key, group in grouped_calc.items():
        group.sort(key=lambda x: x['E'])
        filtered_calc.extend(group[:2])
        lowest_calc_per_jp[key] = group[0]

    # Get Experimental Data
    exp_states = get_experimental_states(csv_file)
    print(f"Found {len(exp_states)} experimental states with valid J-pi.")

    # Plotly visualization
    fig = go.Figure()

    # Colors
    colors = {'+': '#00CED1', '-': '#FF00FF'} # Cyan (+) and Magenta (-)
    
    # 1. Plot Calculated States and Connections
    for p in ['+', '-']:
        p_calc = [s for s in filtered_calc if s['P'] == p]
        if not p_calc:
            continue
            
        # Markers for lowest two states
        fig.add_trace(go.Scatter(
            x=[s['J'] for s in p_calc],
            y=[s['Ex'] for s in p_calc],
            mode='markers',
            name=f'Calc {p} (Lowest 2)',
            marker=dict(
                size=10,
                color=colors[p],
                symbol='circle',
                line=dict(width=1, color='White'),
                opacity=0.7
            ),
            hoverinfo='text',
            hovertext=[f"Calc {s['name']}<br>Ex: {s['Ex']:.3f} MeV<br>J: {s['J']}" for s in p_calc],
            legendgroup=f'calc_{p}'
        ))

        # Line connection for the very lowest calculated states per J
        lowest_p_calc = sorted([s for key, s in lowest_calc_per_jp.items() if key[1] == p], key=lambda x: x['J'])
        if len(lowest_p_calc) > 1:
            fig.add_trace(go.Scatter(
                x=[s['J'] for s in lowest_p_calc],
                y=[s['Ex'] for s in lowest_p_calc],
                mode='lines',
                name=f'Calc {p} yrast line',
                line=dict(color=colors[p], width=1, dash='dot'),
                showlegend=False,
                legendgroup=f'calc_{p}',
                hoverinfo='none'
            ))

    # 2. Plot Experimental States and Connections
    for p in ['+', '-']:
        p_exp = sorted([s for s in exp_states if s['P'] == p], key=lambda x: x['J'])
        if not p_exp:
            continue
            
        # Markers
        fig.add_trace(go.Scatter(
            x=[s['J'] for s in p_exp],
            y=[s['Ex'] for s in p_exp],
            mode='markers',
            name=f'Exp {p}',
            marker=dict(
                size=12,
                color=colors[p],
                symbol='diamond-open',
                line=dict(width=2, color=colors[p])
            ),
            hoverinfo='text',
            hovertext=[f"{s['name']}<br>Ex: {s['Ex']:.3f} MeV" for s in p_exp],
            legendgroup=f'exp_{p}'
        ))

        # Line connection
        if len(p_exp) > 1:
            fig.add_trace(go.Scatter(
                x=[s['J'] for s in p_exp],
                y=[s['Ex'] for s in p_exp],
                mode='lines',
                name=f'Exp {p} line',
                line=dict(color=colors[p], width=2),
                showlegend=False,
                legendgroup=f'exp_{p}',
                hoverinfo='none'
            ))

    fig.update_layout(
        title=dict(
            text="38Cl Calculated vs Experimental Energy Levels",
            font=dict(size=24, color='white')
        ),
        xaxis=dict(
            title="Spin (J)",
            gridcolor='rgba(255,255,255,0.1)',
            dtick=1,
            range=[-0.5, 14.5]
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
            borderwidth=1,
            groupclick='toggleitem'
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    output_html = os.path.join(base_dir, '38Cl_energy_levels_with_exp.html')
    fig.write_html(output_html)
    print(f"Updated plotly chart saved to {output_html}")
    
    try:
        output_png = os.path.join(base_dir, '38Cl_energy_levels_with_exp.png')
        fig.write_image(output_png, scale=2)
        print(f"Static image saved to {output_png}")
    except Exception as e:
        print(f"Could not save static image: {e}")

if __name__ == "__main__":
    plot_38Cl_states()
