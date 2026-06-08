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

from plotly.subplots import make_subplots

# Helper to parse J from strings like "1+(1)" or "3/2+(1)"
def parse_j(jpi_str):
    match = re.match(r"(\d+)/?(\d+)?", jpi_str)
    if not match:
        return 0
    num = float(match.group(1))
    den = float(match.group(2)) if match.group(2) else 1.0
    return num / den


def process_system(directory, parent_label, daughter_label, interactions,
                   x_max=4.0, y_max=None, dp_mode=False, daughter_J=2.5,
                   show_j_labels=True):
    """Parse C2S files for a parent->daughter system and produce CSV + combined PNG.

    dp_mode=True scales C²S by (2J_f+1)/(2J_i+1), i.e. the factor relevant for the
    inverse (d,p) stripping cross section onto the parent state. J_i is the daughter
    ground-state spin (default 5/2).
    """
    all_results = []
    for interact in interactions:
        filename = f"{parent_label}_{daughter_label}_{interact}+.txt"
        filepath = os.path.join(directory, filename)
        if os.path.exists(filepath):
            print(f"Parsing {filename}...")
            parsed_data = parse_c2s_file(filepath)
            for entry in parsed_data:
                entry['Interaction'] = interact.upper()
                all_results.append(entry)
        else:
            print(f"WARNING: {filename} not found, skipping.")

    if not all_results:
        print(f"No data found for {parent_label}->{daughter_label}, skipping.")
        return

    df = pd.DataFrame(all_results).fillna(0)
    df['J'] = df['Parent_Jpi'].apply(parse_j)
    df['2Jplus1'] = 2 * df['J'] + 1
    twoJi_plus_1 = 2 * daughter_J + 1

    suffix = '_dp' if dp_mode else ''
    csv_out = os.path.join(directory, f'c2s_{parent_label}_{daughter_label}gs{suffix}.csv')
    df.to_csv(csv_out, index=False)
    print(f"Saved extracted data to {csv_out}")

    orbital_colors = {'0d3/2': '#636EFA', '0d5/2': '#EF553B', '1s1/2': '#00CC96'}
    orbitals = ['0d3/2', '0d5/2', '1s1/2']
    orbital_offsets = {'0d3/2': -0.02, '0d5/2': 0, '1s1/2': 0.02}
    interactions_upper = [i.upper() for i in interactions]

    # Compute global y_max so all subplots share a comparable scale.
    if y_max is None:
        scale_max = 0.0
        for interact in interactions_upper:
            subset = df[df['Interaction'] == interact]
            for orb in orbitals:
                if orb not in subset.columns:
                    continue
                yv = subset[orb]
                if dp_mode:
                    yv = yv * subset['2Jplus1'] / twoJi_plus_1
                if not yv.empty:
                    scale_max = max(scale_max, float(yv.max()))
        y_max = max(0.9, scale_max * 1.15)

    fig = make_subplots(
        rows=len(interactions_upper), cols=1,
        subplot_titles=interactions_upper,
        shared_xaxes=True,
        vertical_spacing=0.08
    )

    for i, interact in enumerate(interactions_upper):
        row_num = i + 1
        subset = df[df['Interaction'] == interact].sort_values('Parent_Ex')
        if subset.empty:
            continue

        parent_gs = subset[subset['Parent_Ex'] == 0]
        if not parent_gs.empty:
            gs_row = parent_gs.iloc[0]
            print(f"{parent_label}->{daughter_label} {interact}: Parent GS J={gs_row['J']}, 2J0+1={gs_row['2Jplus1']}")

        # Per-state J labels, positioned above the tallest orbital at each Ex.
        state_peaks = {}

        for orb in orbitals:
            if orb not in subset.columns:
                continue
            orb_subset = subset[subset[orb] > 0]
            if orb_subset.empty:
                continue

            scale = (orb_subset['2Jplus1'] / twoJi_plus_1) if dp_mode else 1.0
            x_vals = orb_subset['Parent_Ex'] + orbital_offsets[orb]
            y_vals = orb_subset[orb] * scale

            for ex, jpi, yv in zip(orb_subset['Parent_Ex'], orb_subset['Parent_Jpi'], y_vals):
                if ex not in state_peaks or yv > state_peaks[ex][0]:
                    state_peaks[ex] = (float(yv), jpi)

            stem_x, stem_y = [], []
            for x, y in zip(x_vals, y_vals):
                stem_x.extend([x, x, None])
                stem_y.extend([0, y, None])

            fig.add_trace(go.Scatter(
                x=stem_x, y=stem_y, mode='lines',
                line=dict(color=orbital_colors[orb], width=1.5),
                legendgroup=orb, showlegend=False, hoverinfo='skip'
            ), row=row_num, col=1)

            y_label = "(2J_f+1)/(2J_i+1)·C²S" if dp_mode else "C²S"
            hover_vals = orb_subset[orb] * (scale if dp_mode else 1.0)
            fig.add_trace(go.Scatter(
                x=x_vals, y=y_vals, mode='markers',
                marker=dict(color=orbital_colors[orb], size=6),
                name=orb, legendgroup=orb, showlegend=(row_num == 1),
                hoverinfo='text',
                text=[f"Interaction: {interact}<br>State: {jpi}<br>Ex: {ex} MeV<br>Orbital: {orb}<br>{y_label}: {val:.4f}"
                      for jpi, ex, val in zip(orb_subset['Parent_Jpi'], orb_subset['Parent_Ex'], hover_vals)]
            ), row=row_num, col=1)

            # Centroid: weighted by (2J+1)·C²S (independent of dp scaling).
            weights = orb_subset['2Jplus1'] * orb_subset[orb]
            weighted_sum_ex = (weights * orb_subset['Parent_Ex']).sum()
            total_weight = weights.sum()

            if total_weight > 0:
                centroid_ex = weighted_sum_ex / total_weight
                fig.add_trace(go.Scatter(
                    x=[centroid_ex, centroid_ex],
                    y=[0, y_max],
                    mode='lines',
                    line=dict(color=orbital_colors[orb], width=4, dash='solid'),
                    name=f"{orb} Centroid",
                    legendgroup=orb,
                    showlegend=False,
                    hoverinfo='text',
                    text=f"Centroid ({orb}): {centroid_ex:.3f} MeV"
                ), row=row_num, col=1)

        if show_j_labels and state_peaks:
            label_x = [ex for ex in state_peaks]
            label_y = [min(y_max * 0.98, state_peaks[ex][0] + y_max * 0.04) for ex in state_peaks]
            label_t = [state_peaks[ex][1] for ex in state_peaks]
            fig.add_trace(go.Scatter(
                x=label_x, y=label_y, mode='text',
                text=label_t,
                textfont=dict(size=9, color='#444'),
                textposition='top center',
                showlegend=False, hoverinfo='skip'
            ), row=row_num, col=1)

        y_title = "(2J_f+1)/(2J_i+1)·C²S" if dp_mode else "C²S"
        fig.update_yaxes(title_text=y_title, range=[0, y_max], row=row_num, col=1)

    fig.update_xaxes(title_text=f"{parent_label} Excitation Energy (MeV)",
                     range=[-0.1, x_max], row=len(interactions_upper), col=1)

    if dp_mode:
        title = (f"(2J_f+1)/(2J_i+1)·C²S for {daughter_label}(d,p){parent_label} "
                 f"(J_i = {daughter_label} g.s. = {daughter_J:g})<br>"
                 f"Thick Lines = Centroid Energies (2J+1 weighted)")
    else:
        title = (f"Spectroscopic Factors (C²S) for {parent_label}→{daughter_label} "
                 f"Ground State<br>Thick Lines = Centroid Energies (2J+1 weighted)")

    fig.update_layout(
        title_text=title,
        template="plotly_white", height=900, width=1000, legend_title="Orbital"
    )

    img_out = os.path.join(directory, f'c2s_vs_ex_combined_{parent_label}_{daughter_label}{suffix}.png')
    fig.write_image(img_out)
    print(f"Saved combined plot to {img_out}")


directory = '/Users/calemhoffman/Documents/GitHub/cosmo/results/Na'
interactions = ['usd', 'usda', 'usdb']

# Bare C²S (neutron-removal convention from COSMO).
process_system(directory, '26Na', '25Na', interactions)
process_system(directory, '28Na', '27Na', interactions)

# (d,p) stripping-style: scale by (2J_f+1)/(2J_i+1) with J_i = daughter g.s. = 5/2.
process_system(directory, '26Na', '25Na', interactions, dp_mode=True, daughter_J=2.5)
process_system(directory, '28Na', '27Na', interactions, dp_mode=True, daughter_J=2.5)
