#%%
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import re  # Import the regular expression module
import json


color =    ["#8cc640", "#fcbe58", "#b15d28", "#058752","#b499cb", "#1ca1de", "#f6a05b", "#ef4238"]
colorgrad = [color[0],color[1],color[2]]
pio.templates["mycolor"] = go.layout.Template(layout_colorway=color)
pio.templates.default = "mycolor"
pio.templates["mycolor"].layout.xaxis.linewidth = 2
pio.templates["mycolor"].layout.yaxis.linewidth = 2
pio.templates["mycolor"].layout.yaxis.mirror = True
pio.templates["mycolor"].layout.xaxis.mirror = True

pio.templates["mycolor"].data.scatter = [
    go.Scatter(marker=dict(symbol="circle", size=16)),
    go.Scatter(marker=dict(symbol="square", size=16)),
    go.Scatter(marker=dict(symbol="diamond", size=16)),
]

def parse_spectroscopic_data(file_path):
    """
    Parses the spectroscopic data file, extracting parent and daughter values
    from the columns directly.

    Args:
        file_path (str): The path to the data file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row
              of the data with keys 'Parent', 'Daughter', 'Ex(p)', 'Ex(d)', 'L', and 'SF'.
    """
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            values = line.strip().split()
            if len(values) == 6:
                try:
                    parent_str = values[0]
                    daughter_str = values[2]
                    parent_match = re.search(r'(\d+)', parent_str)
                    daughter_match = re.search(r'(\d+)', daughter_str)
                    parent_val = int(parent_match.group(1)) if parent_match else None
                    daughter_val = int(daughter_match.group(1)) if daughter_match else None
                    parent_ex = float(values[1])
                    daughter_ex = float(values[3])
                    l_value = int(values[4])
                    sf = float(values[5])
                    data.append({
                        'Parent': parent_val,
                        'Daughter': daughter_val,
                        'Ex(p)': parent_ex,
                        'Ex(d)': daughter_ex,
                        'L': l_value,
                        'SF': sf
                    })
                except ValueError:
                    print(f"Warning: Skipping line due to invalid numeric format: {line.strip()}")
                except AttributeError:
                    print(f"Warning: Skipping line due to inability to parse parent/daughter values: {line.strip()}")
            else:
                print(f"Warning: Skipping line due to incorrect number of columns: {line.strip()}")
    return data


def filter_data_by_daughter_ex(data, daughter_ex_value):
    """
    Filters the spectroscopic data based on the daughter excitation energy.

    Args:
        data (list): A list of dictionaries containing the spectroscopic data.
        daughter_ex_value (float): The value of Ex(d) to filter by.

    Returns:
        list: A new list containing only the data points where Ex(d)
              matches the daughter_ex_value.
    """
    filtered_data = [item for item in data if item['Ex(d)'] == daughter_ex_value]
    return filtered_data

def create_plotly_bar_plot(df,df_data):
    """
    Creates a Plotly bar plot of SF vs Ex(d), colored by L.

    Args:
        data (list): A list of dictionaries containing the filtered spectroscopic data.
        daughter_ex_value (float): The daughter excitation energy value used for filtering.
    """
    # if not data:
    #     print(f"No data available for Ex(d) = {daughter_ex_value}")
    #     return

    # Convert the list of dictionaries to a Pandas DataFrame for easier handling with Plotly
    # df = pd.DataFrame(data)
    # Assign a color to each unique L value
    unique_L = sorted(df['L'].unique())
    color_map = {l: color[i % len(color)] for i, l in enumerate(unique_L)}
    bar_colors = df['L'].map(color_map)
    print(bar_colors)
    # Increase bar width by setting width parameter
    bar_width = 0.08

    fig = go.Figure(data=[go.Bar(
        x=df['Ex(p)'],
        y=df['G'],
        marker_color=bar_colors,
        width=[bar_width]*len(df),
        # text=df['Parent'],
        hovertemplate='Ex(p): %{x}<br>G: %{y}<br>J: %{text}<extra></extra>'
    )])
    # Add annotations for each of the 4 colors with numbers 1 - 4 in a vertical row at fixed x position
    fixed_x = 6.5  # Set a fixed x position (e.g., right side of plot)
    base_y = df['G'].max() * 1.05  # Start above the highest bar
    y_step = df['G'].max() * 0.15  # Vertical spacing between annotations

    for i, l in enumerate(unique_L[:4]):
        fig.add_annotation(
            x=fixed_x,
            y=base_y - i * y_step,
            text=str(i),
            showarrow=False,
            font=dict(size=28, color='black'),
            bgcolor=color[i],
            bordercolor='black',
            borderwidth=2,
            xanchor='center',
            yanchor='bottom',
            yshift=10
        )
    #add scatter plot of exp data with error bars on top
    # fig.add_trace(go.Scatter(
    #     x=df_data['ex'],
    #     y=df_data['G_norm'],
    #     mode='markers',
    #     marker=dict(color='white', size=18, line=dict(color='black', width=2)),
    #     error_y=dict(type='data', array=df_data['Gerr_norm'], visible=True, color='black'),
    #     hovertemplate='Ex(p): %{x}<br>G: %{y}<extra></extra>'
    # ))
    fig.update_xaxes(showticklabels=True, ticks="inside")
    fig.update_yaxes(showticklabels=True, ticks="inside")
    fig.update_xaxes(showgrid=False, mirror='all')
    fig.update_yaxes(showgrid=False, mirror='all')
    fig.update_layout(
        font=dict(size=24),
        xaxis=dict(
            mirror=True,
            showline=True,
            range=[0, 7],
            title_font=dict(size=24),
            tickfont=dict(size=24)
        ),
        yaxis=dict(
            mirror=True,
            showline=True,
            title_font=dict(size=24),
            tickfont=dict(size=24)
        )
    )
    fig.update_layout(
        xaxis_title='excitation energy [MeV]',
        yaxis_title='G<sub>+</sub>',
        width=800,height=600,
        showlegend=False # If you want a legend for the colors (L values)
    )

    fig.show()
    
# --- Example Usage ---
#%%
file_path = '/Users/calemhoffman/Documents/GitHub/cosmo/results/32Si_31Si_pos.out'  
file_path = '/Users/calemhoffman/Documents/GitHub/cosmo/results/30Mg_29Mg_pos.out'  
file_path = '/Users/calemhoffman/Documents/GitHub/cosmo/results/35Cl_34Cl_pos.out'  
pos_data = parse_spectroscopic_data(file_path)
file_path = '/Users/calemhoffman/Documents/GitHub/cosmo/results/32Si_31Si_neg.out' 
file_path = '/Users/calemhoffman/Documents/GitHub/cosmo/results/30Mg_29Mg_neg.out' 
file_path = '/Users/calemhoffman/Documents/GitHub/cosmo/results/35Cl_34Cl_neg.out' 
neg_data = parse_spectroscopic_data(file_path)
for item in neg_data:
    item['Ex(p)'] += 2.74
# Filter for daughter excitation energies of 0.0 (3+ ground state) and 0.024 (0+ first excited state)
all_data = pos_data + neg_data
selected_daughter_ex = [0.0, 0.024]
filtered_data = [item for item in all_data if item['Ex(d)'] in selected_daughter_ex]

print("Parsed Data (first 5 entries):")
print(all_data)
print(f"\nFiltered Data for Ex(d) = {selected_daughter_ex} (first 5 entries):")
print(filtered_data[:5])

df = pd.DataFrame(filtered_data)
df['SF_norm'] = df['SF'] / 0.734084 #norm to SF of 5-, prob better to norm data to THeory?
df['G'] = (2.*df['Parent'] + 1)/4.*df['SF']
df['G_norm'] = (2.*df['Parent'] + 1)/4.*df['SF_norm']

print(df.tail())
#%%
#read in exp data csv file into df
df_data = pd.read_csv('/Users/calemhoffman/Documents/GitHub/digios_crh/analysis/working/expc2sdata.csv')
df_data['G'] = (df_data['j']*2.+1)/4. * df_data['c2s']
df_data['Gerr'] = (df_data['j']*2.+1)/4. * df_data['c2serr']
df_data['c2s_norm'] = df_data['c2s'] * 0.734084
df_data['c2serr_norm'] = df_data['c2serr'] * 0.734084
df_data['G_norm'] = (df_data['j']*2.+1)/4. * df_data['c2s_norm']
df_data['Gerr_norm'] = (df_data['j']*2.+1)/4. * df_data['c2serr_norm']
fitype = 1
fitype2 = 3
if fitype2 > 0:
    df_data = df_data[(df_data['fittype'] == fitype) | (df_data['fittype'] == fitype2)]
else:
    df_data = df_data[df_data['fittype'] == fitype]
print(df_data.tail())
# Create the Plotly bar plot with the filtered data
create_plotly_bar_plot(df,df_data)
# %%
# Export data to JSON for the web viewer
import json
df_export = df.copy()
df_export = df_export.round(4)  # Round to 4 decimal places
json_data = df_export.to_dict(orient='records')

with open('theory_data.json', 'w') as f:
    json.dump(json_data, f, indent=2)

print(f"\nExported {len(json_data)} records to theory_data.json")
# %%
df
# %%
