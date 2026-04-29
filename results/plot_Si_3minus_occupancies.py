import xml.etree.ElementTree as ET
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os

def parse_xml_for_3minus(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    system = root.find('system')
    
    # Target lowest 3- state
    lowest_3minus = None
    
    for state in system.findall('state'):
        j = int(state.get('J'))
        if j == 3:
            energy = float(state.get('E'))
            if lowest_3minus is None or energy < lowest_3minus['energy']:
                occupancies = []
                for occ in state.findall('occupation'):
                    occupancies.append({
                        'orbital': occ.get('name'),
                        'n': float(occ.get('N')),
                        'z': float(occ.get('Z'))
                    })
                lowest_3minus = {
                    'energy': energy,
                    'name': state.get('name'),
                    'occupancies': occupancies,
                    'ex': float(state.get('Ex')),
                    'isotope': system.get('name').split('_')[0]
                }
    
    return lowest_3minus

def create_si_comparison_plot(states):
    n_rows = len(states)
    
    # 90s Style Colors
    color_neutron = "#00FFFF" # Cyan
    color_proton = "#FF00FF"  # Neon Pink
    color_bg = "#1A0033"      # Deep Purple/Black
    color_grid = "#330066"    # Grid lines
    color_text = "#FFFF00"    # Yellow
    
    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        subplot_titles=[f"{s['isotope']} 3- (Ex={s['ex']:.3f} MeV)" for s in states],
        vertical_spacing=0.05
    )

    for i, state in enumerate(states):
        df = pd.DataFrame(state['occupancies'])
        
        # Neutron occupancy
        fig.add_trace(
            go.Bar(
                x=df['orbital'],
                y=df['n'],
                name="Neutron (N)",
                marker_color=color_neutron,
                showlegend=(i == 0),
                hovertemplate="Orbital: %{x}<br>N: %{y}<extra></extra>"
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
                hovertemplate="Orbital: %{x}<br>Z: %{y}<extra></extra>"
            ),
            row=i+1, col=1
        )

    # Layout styling
    fig.update_layout(
        height=250 * n_rows,
        width=1000,
        title_text="Silicon Isotopes: Lowest 3- Orbital Occupancies",
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
    fig.update_yaxes(showgrid=True, gridcolor=color_grid, zeroline=True, zerolinecolor=color_grid, title="Occ.")

    fig.update_annotations(font_size=16, font_color="#00FFAA")

    output_dir = "/Users/calemhoffman/Documents/GitHub/cosmo/results"
    output_html = os.path.join(output_dir, "Si_3minus_occupancies.html")
    output_png = os.path.join(output_dir, "Si_3minus_occupancies.png")
    
    fig.write_html(output_html)
    
    try:
        fig.write_image(output_png)
        print(f"Plot saved to {output_html} and {output_png}")
    except Exception as e:
        print(f"Plot saved to {output_html} (static image export failed: {e})")

if __name__ == "__main__":
    results_dir = "/Users/calemhoffman/Documents/GitHub/cosmo/results"
    files = [
        "30Si_fsu9-.xml",
        "32Si_fsu9-.xml",
        "34Si_fsu9-.xml"
    ]
    
    si_states = []
    for f in files:
        path = os.path.join(results_dir, f)
        state = parse_xml_for_3minus(path)
        if state:
            si_states.append(state)
    
    if si_states:
        create_si_comparison_plot(si_states)
    else:
        print("No 3- states found in the specified files.")
