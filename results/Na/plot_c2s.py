import os
import re
import pandas as pd
import plotly.graph_objects as go

def parse_c2s_file(filepath):
    data = []
    current_parent_ex = None
    current_parent_jpi = None
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
        
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Match Parent line: Parent: 1+(1) Ex=0 E=-92.2269
        parent_match = re.match(r"Parent:\s+([0-9\+/()\.-]+)\s+Ex=([\d\.]+)", line)
        if parent_match:
            current_parent_jpi = parent_match.group(1)
            current_parent_ex = float(parent_match.group(2))
            i += 1
            continue
            
        # Match Daughter line: Daughter: 5/2+(1) Ex=0 E=-86.6209
        # We only want the ground state (Ex=0)
        daughter_match = re.match(r"Daughter:\s+5/2\+\(1\)\s+Ex=0", line)
        if daughter_match and current_parent_ex is not None:
            i += 1
            total_c2s = 0
            orbitals = {}
            # Read subsequent lines for C2S until next Daughter, Parent or blank line
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line or next_line.startswith("Daughter") or next_line.startswith("Parent"):
                    break
                
                # Match orbital line: 0d3/2 C2S=0.240484 A=0.490392
                orb_match = re.match(r"([0-9a-z/]+)\s+C2S=([\d\.eE+-]+)", next_line)
                if orb_match:
                    orb_name = orb_match.group(1)
                    c2s_val = float(orb_match.group(2))
                    total_c2s += c2s_val
                    orbitals[orb_name] = c2s_val
                i += 1
            
            if total_c2s > 0:
                data.append({
                    'Parent_Ex': current_parent_ex,
                    'Parent_Jpi': current_parent_jpi,
                    'Total_C2S': total_c2s,
                    **orbitals
                })
            continue
        
        i += 1
    return data

directory = '/Users/calemhoffman/Documents/GitHub/cosmo/results/Na'
interactions = ['usd', 'usda', 'usdb']
all_results = []

for interact in interactions:
    filename = f"26Na_25Na_{interact}+.txt"
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        print(f"Parsing {filename}...")
        parsed_data = parse_c2s_file(filepath)
        for entry in parsed_data:
            entry['Interaction'] = interact.upper()
            all_results.append(entry)

df = pd.DataFrame(all_results)
# Fill NaN with 0 for orbital columns
df = df.fillna(0)
csv_out = os.path.join(directory, 'c2s_26Na_25Nags.csv')
df.to_csv(csv_out, index=False)
print(f"Saved extracted data to {csv_out}")

from plotly.subplots import make_subplots

# Helper to parse J from strings like "1+(1)" or "3/2+(1)"
def parse_j(jpi_str):
    match = re.match(r"(\d+)/?(\d+)?", jpi_str)
    if not match:
        return 0
    num = float(match.group(1))
    den = float(match.group(2)) if match.group(2) else 1.0
    return num / den

df['J'] = df['Parent_Jpi'].apply(parse_j)
df['2Jplus1'] = 2 * df['J'] + 1

# Plotting
orbital_colors = {'0d3/2': '#636EFA', '0d5/2': '#EF553B', '1s1/2': '#00CC96'}
orbitals = ['0d3/2', '0d5/2', '1s1/2']
orbital_2jplus1 = {'0d3/2': 4, '0d5/2': 6, '1s1/2': 2}
orbital_offsets = {'0d3/2': -0.02, '0d5/2': 0, '1s1/2': 0.02}
interactions = ['USD', 'USDA', 'USDB']

fig = make_subplots(
    rows=3, cols=1, 
    subplot_titles=interactions,
    shared_xaxes=True,
    vertical_spacing=0.08
)

for i, interact in enumerate(interactions):
    row_num = i + 1
    subset = df[df['Interaction'] == interact].sort_values('Parent_Ex')
    
    # Identify Parent Ground State J0 (where Ex=0)
    parent_gs = subset[subset['Parent_Ex'] == 0].iloc[0]
    twoJ0plus1 = parent_gs['2Jplus1']
    print(f"Interaction {interact}: Parent GS J={parent_gs['J']}, 2J0+1={twoJ0plus1}")
    
    for orb in orbitals:
        if orb in subset.columns:
            orb_subset = subset[subset[orb] > 0]
            
            x_vals = orb_subset['Parent_Ex'] + orbital_offsets[orb]
            y_vals = orb_subset[orb]
            
            # Stem lines
            stem_x, stem_y = [], []
            for x, y in zip(x_vals, y_vals):
                stem_x.extend([x, x, None])
                stem_y.extend([0, y, None])
            
            fig.add_trace(go.Scatter(
                x=stem_x, y=stem_y, mode='lines',
                line=dict(color=orbital_colors[orb], width=1.5),
                legendgroup=orb, showlegend=False, hoverinfo='skip'
            ), row=row_num, col=1)
            
            # Top markers
            fig.add_trace(go.Scatter(
                x=x_vals, y=y_vals, mode='markers',
                marker=dict(color=orbital_colors[orb], size=6),
                name=orb, legendgroup=orb, showlegend=(row_num == 1),
                hoverinfo='text',
                text=[f"Interaction: {interact}<br>State: {jpi}<br>Ex: {ex} MeV<br>Orbital: {orb}<br>C2S: {val:.4f}" 
                      for jpi, ex, val in zip(orb_subset['Parent_Jpi'], orb_subset['Parent_Ex'], orb_subset[orb])]
            ), row=row_num, col=1)
            
            # Calculate Centroid: sum((2J+1) * C2S * Ex) / sum((2J+1) * C2S)
            weights = orb_subset['2Jplus1'] * orb_subset[orb]
            weighted_sum_ex = (weights * orb_subset['Parent_Ex']).sum()
            total_weight = weights.sum()
            
            if total_weight > 0:
                centroid_ex = weighted_sum_ex / total_weight
                
                # Add thick vertical line for centroid
                fig.add_trace(go.Scatter(
                    x=[centroid_ex, centroid_ex],
                    y=[0, 0.9],
                    mode='lines',
                    line=dict(color=orbital_colors[orb], width=4, dash='solid'),
                    name=f"{orb} Centroid",
                    legendgroup=orb,
                    showlegend=False,
                    hoverinfo='text',
                    text=f"Centroid ({orb}): {centroid_ex:.3f} MeV"
                ), row=row_num, col=1)

    fig.update_yaxes(title_text="C²S", range=[0, 0.9], row=row_num, col=1)

fig.update_xaxes(title_text="26Na Excitation Energy (MeV)", range=[-0.1, 4.0], row=3, col=1)

fig.update_layout(
    title_text="Spectroscopic Factors (C²S) to 25Na Ground State (5/2+)<br>Thick Lines = Centroid Energies (2J+1 weighted)",
    template="plotly_white", height=900, width=1000, legend_title="Orbital"
)

# Save PNG
img_out = os.path.join(directory, 'c2s_vs_ex_combined.png')
fig.write_image(img_out)
print(f"Saved combined plot to {img_out}")
