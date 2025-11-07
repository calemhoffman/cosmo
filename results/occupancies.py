#%%
import xml.etree.ElementTree as ET
import pandas as pd

# --- Paste your XML snippets here ---
ground_xml = """
<wavefunction Jz="0" Tz="0" file="36Ar_usdb_M0T0+.HH.EE" id="0"/>
			<occupation name="0d3" N="2.4998" Z="2.4998"/>
			<occupation name="0d5" N="5.76057" Z="5.76057"/>
			<occupation name="1s1" N="1.73962" Z="1.73962"/>
"""

# excited_xml = """
# <wavefunction Jz="0" Tz="2" file="32Si_fsu9_M0T4+.HH.EE" id="7"/>
# <occupation name="0s1" N="2" Z="2"/>
# <occupation name="0p3" N="4" Z="4"/>
# <occupation name="0p1" N="2" Z="2"/>
# <occupation name="0d5" N="5.56275" Z="4.77189"/>
# <occupation name="0d3" N="2.77844" Z="0.27425"/>
# <occupation name="1s1" N="1.65881" Z="0.953858"/>
# <occupation name="0f7" N="0" Z="0"/>
# <occupation name="0f5" N="0" Z="0"/>
# <occupation name="1p3" N="0" Z="0"/>
# <occupation name="1p1" N="0" Z="0"/>
# """

# excited_xml = """
# <wavefunction Jz="0" Tz="2" file="32Si_fsu9_M0T4+.HH.EE" id="1"/>
# 			<occupation name="0s1" N="2" Z="2"/>
# 			<occupation name="0p3" N="4" Z="4"/>
# 			<occupation name="0p1" N="2" Z="2"/>
# 			<occupation name="0d5" N="5.83927" Z="5.18586"/>
# 			<occupation name="0d3" N="2.61605" Z="0.215391"/>
# 			<occupation name="1s1" N="1.54469" Z="0.598745"/>
# 			<occupation name="0f7" N="0" Z="0"/>
# 			<occupation name="0f5" N="0" Z="0"/>
# 			<occupation name="1p3" N="0" Z="0"/>
# 			<occupation name="1p1" N="0" Z="0"/>
#   """
excited_xml = """
			<wavefunction Jz="0" Tz="0" file="36Ar_usdb_M0T0+.HH.EE" id="3"/>
			<occupation name="0d3" N="2.68367" Z="2.68367"/>
			<occupation name="0d5" N="5.62302" Z="5.62302"/>
			<occupation name="1s1" N="1.69331" Z="1.69331"/>
"""
# --- Parse occupations ---
def parse_occupations(xml_text):
    root = ET.fromstring(f"<root>{xml_text}</root>")
    data = {}
    for occ in root.findall('occupation'):
        name = occ.attrib['name']
        data[name] = {
            'N': float(occ.attrib['N']),
            'Z': float(occ.attrib['Z'])
        }
    return data

g_occ = parse_occupations(ground_xml)
e_occ = parse_occupations(excited_xml)

# --- Build DataFrame ---
rows = []
# iterate over the union of orbitals so we don't KeyError if one set is missing an orbital
all_orbs = sorted(set(g_occ.keys()) | set(e_occ.keys()))
for orb in all_orbs:
    g = g_occ.get(orb, {'N': 0.0, 'Z': 0.0})
    e = e_occ.get(orb, {'N': 0.0, 'Z': 0.0})
    dN = e['N'] - g['N']
    dZ = e['Z'] - g['Z']
    rows.append({'Orbital': orb, 'ΔN': dN, 'ΔZ': dZ})

df = pd.DataFrame(rows).set_index('Orbital')
print(df)

# %%
