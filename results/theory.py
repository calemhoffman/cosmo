#%%
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd

color =    ["#8cc640", "#b15d28", "#fcbe58", "#058752","#b499cb", "#1ca1de", "#f6a05b", "#ef4238"]
colorgrad = [color[0],color[1],color[2]]
pio.templates["mycolor"] = go.layout.Template(layout_colorway=color)
pio.templates.default = "mycolor"

def parse_spectroscopic_data(file_path):
    """
    Parses the spectroscopic data file.

    Args:
        file_path (str): The path to the data file.

    Returns:
        list: A list of dictionaries, where each dictionary represents a row
              of the data with keys 'Ex(p)', 'Ex(d)', 'L', and 'SF'.
    """
    data = []
    with open(file_path, 'r') as f:
        for line in f:
            # Skip comment lines starting with '#'
            if line.startswith('#'):
                continue
            # Split the line by spaces and handle potential multiple spaces
            values = line.strip().split()
            if len(values) == 5:
                try:
                    parent_ex = float(values[1])
                    daughter_ex = float(values[3])
                    l_value = int(values[4])
                    sf = float(values[5])
                    data.append({
                        'Ex(p)': parent_ex,
                        'Ex(d)': daughter_ex,
                        'L': l_value,
                        'SF': sf
                    })
                except ValueError:
                    print(f"Warning: Skipping line due to invalid numeric format: {line.strip()}")
            elif len(values) == 6:
                 try:
                    parent_ex = float(values[1])
                    daughter_ex = float(values[3])
                    l_value = int(values[4])
                    sf = float(values[5])
                    data.append({
                        'Ex(p)': parent_ex,
                        'Ex(d)': daughter_ex,
                        'L': l_value,
                        'SF': sf
                    })
                 except ValueError:
                    print(f"Warning: Skipping line due to invalid numeric format: {line.strip()}")
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

def create_plotly_bar_plot(data, daughter_ex_value):
    """
    Creates a Plotly bar plot of SF vs Ex(d), colored by L.

    Args:
        data (list): A list of dictionaries containing the filtered spectroscopic data.
        daughter_ex_value (float): The daughter excitation energy value used for filtering.
    """
    if not data:
        print(f"No data available for Ex(d) = {daughter_ex_value}")
        return

    # Convert the list of dictionaries to a Pandas DataFrame for easier handling with Plotly
    df = pd.DataFrame(data)
    # Assign a color to each unique L value
    unique_L = sorted(df['L'].unique())
    color_map = {l: color[i % len(color)] for i, l in enumerate(unique_L)}
    bar_colors = df['L'].map(color_map)
    print(bar_colors)
    # Increase bar width by setting width parameter
    bar_width = 0.2

    fig = go.Figure(data=[go.Bar(
        x=df['Ex(p)'],
        y=df['SF'],
        marker_color=bar_colors,
        width=[bar_width]*len(df),
        # text=df['L'],
        hovertemplate='Ex(p): %{x}<br>SF: %{y}<br>L: %{text}<extra></extra>'
    )])


    fig.update_layout(
        title=f'Spectroscopic Factors vs. Ex(d) for Ex(d) = {daughter_ex_value}',
        xaxis_title='Ex(p) (MeV)',
        yaxis_title='SF=|A|^2',
        showlegend=True # If you want a legend for the colors (L values)
    )

    fig.show()
    
# --- Example Usage ---

file_path = '/Users/calemhoffman/Documents/GitHub/cosmo/results/32Si_31Si_pos.out'  # Replace with the actual path to your file
pos_data = parse_spectroscopic_data(file_path)
file_path = '/Users/calemhoffman/Documents/GitHub/cosmo/results/32Si_31Si_neg.out'  # Replace with the actual path to your file
neg_data = parse_spectroscopic_data(file_path)
for item in neg_data:
    item['Ex(p)'] += 5
# Let's say you want to filter for daughter excitation energy of 0.0
all_data = pos_data + neg_data
selected_daughter_ex = 0.0
filtered_data = filter_data_by_daughter_ex(all_data, selected_daughter_ex)

print("Parsed Data (first 5 entries):")
print(all_data[:5])
print(f"\nFiltered Data for Ex(d) = {selected_daughter_ex} (first 5 entries):")
print(filtered_data[:5])

# Create the Plotly bar plot with the filtered data
create_plotly_bar_plot(filtered_data, selected_daughter_ex)
# %%
