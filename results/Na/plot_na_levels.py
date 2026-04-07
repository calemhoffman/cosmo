import pandas as pd
import plotly.graph_objects as go
import os

# Load the data
csv_path = '/Users/calemhoffman/Documents/GitHub/cosmo/results/Na/na_levels.csv'
df = pd.read_csv(csv_path)

def create_level_plot(nucleus, dataframe):
    nuc_df = dataframe[dataframe['Nucleus'] == nucleus]
    fig = go.Figure()

    interactions = sorted(nuc_df['Interaction'].unique())
    colors = {'USD': '#636EFA', 'USDA': '#EF553B', 'USDB': '#00CC96'}
    
    # Offsets for each interaction on the X-axis to separate them
    x_positions = {'USD': 0, 'USDA': 1, 'USDB': 2}
    line_width = 0.4

    for interaction in interactions:
        int_df = nuc_df[nuc_df['Interaction'] == interaction]
        color = colors.get(interaction, 'black')
        x_base = x_positions[interaction]
        
        for _, row in int_df.iterrows():
            # Add horizontal line for the level
            fig.add_trace(go.Scatter(
                x=[x_base - line_width, x_base + line_width],
                y=[row['Ex'], row['Ex']],
                mode='lines',
                line=dict(color=color, width=3),
                name=interaction,
                legendgroup=interaction,
                showlegend=(row['Ex'] == 0), # Only show in legend once
                hoverinfo='text',
                text=f"Interaction: {interaction}<br>State: {row['State']}<br>Jπ: {row['Jp']}<br>Ex: {row['Ex']} MeV"
            ))
            
            # Add text label for Jpi
            fig.add_annotation(
                x=x_base + line_width + 0.05,
                y=row['Ex'],
                text=row['Jp'],
                showarrow=False,
                xanchor='left',
                font=dict(size=10, color=color)
            )

    fig.update_layout(
        title=f"Energy Level Schemes for {nucleus} (Ex ≤ 4 MeV)",
        xaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 2],
            ticktext=interactions,
            title="Interaction",
            range=[-0.5, 2.8]
        ),
        yaxis=dict(title="Excitation Energy (MeV)"),
        template="plotly_white",
        height=800,
        width=800
    )
    
    return fig

# Generate and save plots
for nucleus in ['25Na', '26Na']:
    fig = create_level_plot(nucleus, df)
    output_path = f'/Users/calemhoffman/Documents/GitHub/cosmo/results/Na/{nucleus}_levels.png'
    fig.write_image(output_path)
    print(f"Saved plot for {nucleus} to {output_path}")
