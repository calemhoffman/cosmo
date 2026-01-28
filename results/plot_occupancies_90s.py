import xml.etree.ElementTree as ET
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os

def parse_xml_for_all_states(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    system = root.find('system')
    
    # Store all states grouped by J
    states_by_j = {}
    for state in system.findall('state'):
        j = int(state.get('J'))
        energy = float(state.get('E'))
        
        if j not in states_by_j:
            states_by_j[j] = []
            
        occupancies = []
        for occ in state.findall('occupation'):
            occupancies.append({
                'orbital': occ.get('name'),
                'n': float(occ.get('N')),
                'z': float(occ.get('Z'))
            })
        
        states_by_j[j].append({
            'energy': energy,
            'name': state.get('name'),
            'occupancies': occupancies,
            'ex': float(state.get('Ex'))
        })
    
    # Sort states by energy for each J
    for j in states_by_j:
        states_by_j[j].sort(key=lambda x: x['energy'])
        
    return states_by_j

def create_plot(states_by_j, rank, title_suffix, filename_suffix, is_delta=False):
    """
    rank: 0 for yrast, 1 for yrare
    is_delta: if True, plot yrare - yrast
    """
    # Sort spins and filter to those that have the required rank
    # For delta, we need at least 2 states
    target_rank = 1 if is_delta else rank
    sorted_j = [j for j in sorted(states_by_j.keys()) if len(states_by_j[j]) > target_rank]
    n_rows = len(sorted_j)
    
    if n_rows == 0:
        print(f"No states found for rank {target_rank}")
        return

    # 90s Style Colors
    color_neutron = "#00FFFF" # Cyan
    color_proton = "#FF00FF"  # Neon Pink
    color_bg = "#1A0033"      # Deep Purple/Black
    color_grid = "#330066"    # Grid lines
    color_text = "#FFFF00"    # Yellow
    
    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        subplot_titles=[f"J={j}+ (Δ Energy = {states_by_j[j][1]['ex'] - states_by_j[j][0]['ex']:.3f} MeV)" if is_delta else f"J={j}+ (Ex={states_by_j[j][rank]['ex']:.3f} MeV)" for j in sorted_j],
        vertical_spacing=0.03
    )

    for i, j in enumerate(sorted_j):
        if is_delta:
            yrast = pd.DataFrame(states_by_j[j][0]['occupancies'])
            yrare = pd.DataFrame(states_by_j[j][1]['occupancies'])
            df = yrare.copy()
            df['n'] = yrare['n'] - yrast['n']
            df['z'] = yrare['z'] - yrast['z']
        else:
            df = pd.DataFrame(states_by_j[j][rank]['occupancies'])
        
        # Neutron occupancy
        fig.add_trace(
            go.Bar(
                x=df['orbital'],
                y=df['n'],
                name="Neutron (N)",
                marker_color=color_neutron,
                showlegend=(i == 0),
                hovertemplate="Orbital: %{x}<br>ΔN: %{y}<extra></extra>" if is_delta else "Orbital: %{x}<br>N: %{y}<extra></extra>"
            ),
            row=i+1, col=1
        )
        
        # Proton occupancy
        fig.add_trace(
            go.Bar(
                x=df['orbital'],
                y=df['z'],
                name="Proton (Z)",
                marker_color=color_proton,
                showlegend=(i == 0),
                hovertemplate="Orbital: %{x}<br>ΔZ: %{y}<extra></extra>" if is_delta else "Orbital: %{x}<br>Z: %{y}<extra></extra>"
            ),
            row=i+1, col=1
        )

    # Layout styling
    fig.update_layout(
        height=200 * n_rows,
        width=1000,
        title_text=f"38Cl Valence Orbitals Occupancies ({title_suffix})",
        title_font_size=24,
        title_font_color=color_text,
        paper_bgcolor=color_bg,
        plot_bgcolor=color_bg,
        font_color=color_text,
        barmode='group',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Update axes
    fig.update_xaxes(showgrid=True, gridcolor=color_grid, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=color_grid, zeroline=True, zerolinecolor=color_text if is_delta else color_grid, title="Occ." if not is_delta else "Δ Occ.")

    fig.update_annotations(font_size=16, font_color="#00FFAA")

    output_html = f"/Users/calemhoffman/Documents/GitHub/cosmo/results/38Cl_occupancies_{filename_suffix}.html"
    output_png = f"/Users/calemhoffman/Documents/GitHub/cosmo/results/38Cl_occupancies_{filename_suffix}.png"
    
    fig.write_html(output_html)
    
    try:
        fig.write_image(output_png)
        print(f"Plot saved to {output_html} and {output_png}")
    except Exception as e:
        print(f"Plot saved to {output_html} (static image export failed: {e})")

if __name__ == "__main__":
    xml_file = "/Users/calemhoffman/Documents/GitHub/cosmo/results/38Cl_fsu9+_merged.xml"
    all_data = parse_xml_for_all_states(xml_file)
    
    # Generate Yrast plot
    create_plot(all_data, rank=0, title_suffix="Yrast States", filename_suffix="yrast")
    
    # Generate Yrare plot
    create_plot(all_data, rank=1, title_suffix="Yrare States", filename_suffix="yrare")

    # Generate Delta plot (Yrare - Yrast)
    create_plot(all_data, rank=None, title_suffix="Delta: Yrare - Yrast", filename_suffix="delta", is_delta=True)
