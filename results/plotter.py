#%%
import pandas as pd
import plotly.graph_objects as go

#%%
# Open the text file for reading
# filein = '35S_34S_neg.txt'
filein = '32Si_31Si_neg.txt'
oddeven = 0# - if parent is event
with open(filein, 'r') as file:
    lines = file.readlines()
data = []
current_parent = None
current_daughter = None

# Parse the lines and extract the data
for line in lines:
    line = line.strip()
    if line.startswith('Parent:'):
        parent_parts = line.split('Parent: ')[1].split(' ')
        if (oddeven == 0):
            jf = float(parent_parts[0][0:1])
        else:
            jf = float(parent_parts[0].split('/')[0])/2.
        current_parent = {
            'Jf': jf,
            'Exp': float(parent_parts[1][3:]),  # Remove parentheses
            # 'Parity': parent_parts[2][1:-1]  # Remove parentheses
        }
    elif line.startswith('Daughter:'):
        daughter_parts = line.split('Daughter: ')[1].split(' ')
        if (oddeven == 0):
            ji = float(daughter_parts[0].split('/')[0])/2.
        else:
            ji = float(daughter_parts[0][0:1])
        current_daughter = {
            'Ji': ji,
            'Exd': float(daughter_parts[1].split('=')[1])
        }
    elif line:
        parts = line.split(' ')
        data.append({
            **current_parent,
            **current_daughter,
            'L': float(parts[0][:1]),
            'orbital': parts[0],
            'C2S': float(parts[1].split('=')[1]),
            'A': float(parts[2].split('=')[1])
        })

# Create a DataFrame from the extracted data
df = pd.DataFrame(data)
print(df)
df.dtypes

# %%
#calculate other things for dataframe
df['G'] = (2.*df['Jf']+1.)/(2.*df['Ji']+1)*df['C2S']
df = df[(df['Exd']==0) & (df['C2S']>0.05)]
df[:20]
# %%
print(df[df['orbital']=='1p3/2'].G.sum())
print(df[df['orbital']=='1p1/2'].G.sum())
print(df[df['orbital']=='0f7/2'].G.sum())
print(df[df['orbital']=='0f5/2'].G.sum())

# %%
orb=['0f7/2','1p3/2','1p1/2','0f5/2']
# Assuming df is your DataFrame

fig = go.Figure()

for i in range(len(orb)):
    df
    fig.add_trace(go.Scatter(x=df[df['orbital']==orb[i]].Exp, y=df[df['orbital']==orb[i]].G,
                            mode='markers',#marker_color=df['Jf'],
                             #marker_symbol=df['L'],
                             name=orb[i]))

fig.show()
# %%
# #%%
# # Assuming the file name is "filename.txt"
# filename = "32Si_31Si_neg.out"

# # Assuming the file is tab-separated
# df = pd.read_csv(filename, sep='\t', skiprows=3,header=None)

# # Assuming you want to name the columns as per your comment
# df.columns = ["parent","Ex(p)", "daughter","Ex(d)", "L", "SF"]
# df = df[df['Ex(d)'] == 0]
# # Display the DataFrame
# print(df)
#check for parent / daughter even-odd and parity
# df['Jf'] = df['parent'].str.replace(r'-\(.*\)', '', regex=True).astype('float64')
# df['Ji'] = df['daughter'].str.replace(r'/2\+\(.*\)', '', regex=True).astype('float64')
# df['Ji'] = df['Ji']/2.
# 
# df