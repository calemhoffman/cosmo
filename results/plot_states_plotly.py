import xml.etree.ElementTree as ET
import plotly.graph_objects as go
import os

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

def plot_38Cl_states():
    base_dir = '/Users/calemhoffman/Documents/GitHub/cosmo/results'
    files = [
        os.path.join(base_dir, '38Cl_fsu9+_merged.xml'),
        os.path.join(base_dir, '38Cl_fsu9-_merged.xml')
    ]

    all_states = []
    for f in files:
        all_states.extend(get_states_from_xml(f))

    if not all_states:
        print("No states found.")
        return

    # Find ground state energy
    global_min_e = min(s['E'] for s in all_states)
    print(f"Global Ground State Energy: {global_min_e:.3f} MeV")

    # Filter: Lowest two energy states for each (J, P)
    # Group by (J, P)
    grouped_states = {}
    for s in all_states:
        s['Ex'] = s['E'] - global_min_e
        key = (s['J'], s['P'])
        if key not in grouped_states:
            grouped_states[key] = []
        grouped_states[key].append(s)

    filtered_states = []
    for key, group in grouped_states.items():
        # Sort by absolute energy (most negative first)
        group.sort(key=lambda x: x['E'])
        # Take the lowest two
        filtered_states.extend(group[:2])

    # Plotly visualization
    fig = go.Figure()

    # Define colors
    colors = {'+': '#00CED1', '-': '#FF00FF'} # DarkCyan (+) and Magenta (-)
    
    # Process by parity for legend grouping
    for p in ['+', '-']:
        p_states = [s for s in filtered_states if s['P'] == p]
        if not p_states:
            continue
            
        fig.add_trace(go.Scatter(
            x=[s['J'] for s in p_states],
            y=[s['Ex'] for s in p_states],
            mode='markers+text',
            name=f'Parity {p}',
            text=[s['name'] for s in p_states],
            textposition="top center",
            marker=dict(
                size=12,
                color=colors[p],
                symbol='circle' if p == '+' else 'diamond',
                line=dict(width=1, color='White')
            ),
            hoverinfo='text',
            hovertext=[f"Name: {s['name']}<br>Ex: {s['Ex']:.3f} MeV<br>J: {s['J']}<br>E: {s['E']:.3f} MeV" for s in p_states]
        ))

    fig.update_layout(
        title=dict(
            text="38Cl Calculated Energy Levels (Lowest 2 per J<sup>π</sup>)",
            font=dict(size=24, color='white')
        ),
        xaxis=dict(
            title="Spin (J)",
            gridcolor='rgba(255,255,255,0.1)',
            dtick=1
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
            bgcolor='rgba(0,0,0,0)',
            bordercolor='rgba(255,255,255,0.3)',
            borderwidth=1
        ),
        margin=dict(l=50, r=50, t=80, b=50)
    )

    output_html = os.path.join(base_dir, '38Cl_energy_levels.html')
    fig.write_html(output_html)
    print(f"Plotly chart saved to {output_html}")
    
    # Also save as a high-quality static image if kaleido is installed
    try:
        output_png = os.path.join(base_dir, '38Cl_energy_levels_plotly.png')
        fig.write_image(output_png, scale=2)
        print(f"Static image saved to {output_png}")
    except Exception as e:
        print(f"Could not save static image: {e}")

if __name__ == "__main__":
    plot_38Cl_states()
