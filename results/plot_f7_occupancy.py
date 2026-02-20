"""
Plot ν(0f₇/₂) neutron occupancy vs. spin J for 38Cl.

Correct parity-matched comparison pairs:
  • Negative parity:  FSU9 0ℏω (fsu9-)  vs  FSU9 2ℏω (fsu9_2hw-)
  • Positive parity:  FSU9 1ℏω (fsu9+)  vs  FSU9 3ℏω (fsu9+3hw)

Comparing 0ℏω with 3ℏω is incorrect — they differ by an *odd* number of ℏω
and represent configurations of different intrinsic parity structure.
"""

import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

F7_ORBITAL = "0f7"
BASE = "/Users/calemhoffman/Documents/GitHub/cosmo/results"

# ── XML parser ────────────────────────────────────────────────────────────────

def parse_states(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    records = []
    for state in root.findall(".//state"):
        try:
            J = int(state.get("J"))
        except (TypeError, ValueError):
            continue
        parity = state.get("P", "")
        E      = float(state.get("Ex", "nan"))   # MeV excitation energy
        name   = state.get("name", "")
        occ_n, occ_z = {}, {}
        for occ in state.findall("occupation"):
            oname = occ.get("name")
            occ_n[oname] = float(occ.get("N", 0))
            occ_z[oname] = float(occ.get("Z", 0))
        records.append(dict(J=J, parity=parity, E=E, name=name,
                            occ_n=occ_n, occ_z=occ_z))
    return records


def get_yrast_yrare(records, parity="+"):
    from collections import defaultdict
    by_J = defaultdict(list)
    for r in records:
        if r["parity"] == parity:
            by_J[r["J"]].append(r)
    yrast, yrare = {}, {}
    for J, states in by_J.items():
        states_sorted = sorted(states, key=lambda s: s["E"])
        yrast[J] = states_sorted[0]
        if len(states_sorted) >= 2:
            yrare[J] = states_sorted[1]
    return yrast, yrare


def f7_series(yrast_dict, yrare_dict):
    """Return spin arrays, yrast/yrare f7/2 occupancy, delta, ΔE — for J with both yrast and yrare."""
    spins    = sorted(set(yrast_dict) & set(yrare_dict))
    J        = np.array(spins)
    f7_a     = np.array([yrast_dict[s]["occ_n"].get(F7_ORBITAL, np.nan) for s in spins])
    f7_r     = np.array([yrare_dict[s]["occ_n"].get(F7_ORBITAL, np.nan) for s in spins])
    delta_f7 = f7_r - f7_a
    delta_E  = np.array([yrare_dict[s]["E"] - yrast_dict[s]["E"] for s in spins])
    return J, f7_a, f7_r, delta_f7, delta_E


def f7_yrast_only(yrast_dict):
    spins = sorted(yrast_dict)
    J     = np.array(spins)
    f7_a  = np.array([yrast_dict[s]["occ_n"].get(F7_ORBITAL, np.nan) for s in spins])
    return J, f7_a


# ── load files ────────────────────────────────────────────────────────────────

# Negative parity pair (0ℏω and 2ℏω)
neg0 = parse_states(f"{BASE}/38Cl_fsu9-_merged.xml")
neg2 = parse_states(f"{BASE}/38Cl_fsu9_2hw-_merged.xml")

yr0n, yr0r_n = get_yrast_yrare(neg0, parity="-")
yr2n, yr2r_n = get_yrast_yrare(neg2, parity="-")

J0n,  f7_0n_a,  f7_0n_r,  df7_0n,  dE_0n  = f7_series(yr0n, yr0r_n)
J2n,  f7_2n_a,  f7_2n_r,  df7_2n,  dE_2n  = f7_series(yr2n, yr2r_n)

# Also get yrast-only for 2ℏω if yrare is sparse
J2n_a, f7_2n_ao = f7_yrast_only(yr2n)

# Positive parity pair (1ℏω = fsu9+ and 3ℏω = fsu9+3hw)
pos1 = parse_states(f"{BASE}/38Cl_fsu9+_merged.xml")
pos3 = parse_states(f"{BASE}/38Cl_fsu9+3hw_merged.xml")

yr1p, yr1r_p = get_yrast_yrare(pos1, parity="+")
yr3p, yr3r_p = get_yrast_yrare(pos3, parity="+")

J1p,  f7_1p_a,  f7_1p_r,  df7_1p,  dE_1p  = f7_series(yr1p, yr1r_p)
J3p_a, f7_3p_ao = f7_yrast_only(yr3p)  # 3ℏω yrast
J3p_r, f7_3p_ro = f7_yrast_only(yr3r_p)  # 3ℏω yrare


# ── colour palette ────────────────────────────────────────────────────────────

C_YRA  = "#00CFFF"    # cyan  – 0/1ℏω yrast
C_YRR  = "#FF6EC7"    # pink  – 0/1ℏω yrare
C_2HW  = "#66FF99"    # green – 2ℏω
C_3HW  = "#99CCFF"    # blue  – 3ℏω
GOLD   = "#FFD700"

BKGD = "#111111"


# ── figure layout ─────────────────────────────────────────────────────────────

fig, axes = plt.subplots(2, 3, figsize=(15, 9),
                          gridspec_kw={"height_ratios": [3, 2]})
fig.patch.set_facecolor(BKGD)
fig.suptitle("³⁸Cl  $\\nu(0f_{7/2})$ occupancy vs. spin  —  parity-matched comparisons",
             color="white", fontsize=14, y=0.98)

def style_ax(ax):
    ax.set_facecolor(BKGD)
    for sp in ax.spines.values():
        sp.set_edgecolor("#444444")
    ax.tick_params(colors="white", which="both")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    ax.title.set_color("white")

for row in axes:
    for ax in row:
        style_ax(ax)


# ══════════════════════════════════════════════════════════════════════════════
# LEFT COLUMN  —  Negative parity:  0ℏω  vs  2ℏω
# ══════════════════════════════════════════════════════════════════════════════

ax = axes[0, 0]
ax.plot(J0n,  f7_0n_a,  "o-",  color=C_YRA, lw=2, ms=7, label="0ℏω yrast")
ax.plot(J0n,  f7_0n_r,  "s--", color=C_YRR, lw=2, ms=7, label="0ℏω yrare")
ax.plot(J2n_a, f7_2n_ao, "^-", color=C_2HW, lw=2, ms=7, label="2ℏω yrast")
if len(J2n):   # overlay yrare if yrare data exists
    ax.plot(J2n, f7_2n_r, "D--", color="lime", lw=1.5, ms=6, label="2ℏω yrare")
ax.axhline(1.0, color="white", lw=0.8, ls=":", alpha=0.35, label="single-n limit")
ax.set_ylabel("$\\nu(0f_{7/2})$ occupancy", fontsize=11)
ax.set_title("Negative parity  (0ℏω vs 2ℏω)", fontsize=11)
ax.legend(fontsize=8, loc="upper left")
ax.set_ylim(0, 3.2)
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.25))
ax.grid(True, which="both", alpha=0.12)

# delta panel
ax = axes[1, 0]
ax.bar(J0n - 0.2, df7_0n, 0.4, color=C_YRR, alpha=0.85, label="0ℏω: yrare−yrast")
if len(J2n):
    ax.bar(J2n + 0.2, df7_2n, 0.4, color=C_2HW, alpha=0.85, label="2ℏω: yrare−yrast")
ax.axhline(0, color="white", lw=0.8)
ax.set_ylabel("$\\Delta\\nu(0f_{7/2})$", fontsize=11)
ax.set_xlabel("Spin J", fontsize=11)
ax.set_title("Yrare − Yrast  $\\nu(0f_{7/2})$  difference", fontsize=10)
ax.legend(fontsize=8)
ax.grid(True, axis="y", alpha=0.15)


# ══════════════════════════════════════════════════════════════════════════════
# MIDDLE COLUMN  —  Positive parity:  1ℏω  vs  3ℏω
# ══════════════════════════════════════════════════════════════════════════════

ax = axes[0, 1]
ax.plot(J1p,  f7_1p_a,  "o-",  color=C_YRA, lw=2, ms=7, label="1ℏω yrast")
ax.plot(J1p,  f7_1p_r,  "s--", color=C_YRR, lw=2, ms=7, label="1ℏω yrare")
if len(J3p_a):
    ax.plot(J3p_a, f7_3p_ao, "^-",  color=C_3HW, lw=2, ms=7, label="3ℏω yrast")
if len(J3p_r):
    ax.plot(J3p_r, f7_3p_ro, "D--", color="#AAFFCC", lw=1.5, ms=6, label="3ℏω yrare")
ax.axhline(1.0, color="white", lw=0.8, ls=":", alpha=0.35)
ax.set_title("Positive parity  (1ℏω vs 3ℏω)", fontsize=11)
ax.set_ylim(0, 3.2)
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.25))
ax.legend(fontsize=8, loc="upper left")
ax.grid(True, which="both", alpha=0.12)

# delta panel (1hw only; 3hw yrare may be sparse)
ax = axes[1, 1]
ax.bar(J1p - 0.2, df7_1p, 0.4, color=C_YRR, alpha=0.85, label="1ℏω: yrare−yrast")
ax.axhline(0, color="white", lw=0.8)
ax.set_ylabel("$\\Delta\\nu(0f_{7/2})$", fontsize=11)
ax.set_xlabel("Spin J", fontsize=11)
ax.set_title("Yrare − Yrast  $\\nu(0f_{7/2})$  difference", fontsize=10)
ax.legend(fontsize=8)
ax.grid(True, axis="y", alpha=0.15)


# ══════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN  —  Yrare−Yrast energy gap  (both parities)
# ══════════════════════════════════════════════════════════════════════════════

ax = axes[0, 2]
ax.plot(J0n, dE_0n, "o-",  color="#FF8C00", lw=2, ms=7, label="π=− 0ℏω gap")
if len(J2n):
    ax.plot(J2n, dE_2n, "^-", color=C_2HW,  lw=2, ms=7, label="π=− 2ℏω gap")
ax.plot(J1p, dE_1p, "s--", color="#00BFFF", lw=2, ms=7, label="π=+ 1ℏω gap")
ax.set_ylabel("$E_{yrare} - E_{yrast}$ (MeV)", fontsize=11)
ax.set_title("Yrare − Yrast energy splitting", fontsize=11)
ax.legend(fontsize=8)
ax.yaxis.set_minor_locator(ticker.MultipleLocator(0.25))
ax.grid(True, which="both", alpha=0.12)

# highlight the J region where Δν sign flip occurs (band crossing diagnostic)
for J_flip, label in [(9, "J=9 flip\n(neg)"), (9, "")]:
    ax.axvline(J_flip, color="#FF4040", lw=0.8, ls="--", alpha=0.5)

ax = axes[1, 2]
# direct comparison of yrast 0f7/2 between yrast negative (0ℏω) and positive (1ℏω)
J_neg_a = sorted(yr0n)
f7_neg_a = [yr0n[J]["occ_n"].get(F7_ORBITAL, np.nan) for J in J_neg_a]
J_pos_a  = sorted(yr1p)
f7_pos_a = [yr1p[J]["occ_n"].get(F7_ORBITAL, np.nan) for J in J_pos_a]

ax.plot(J_neg_a, f7_neg_a, "o-",  color="#FF8C00", lw=2, ms=7, label="π=− 0ℏω yrast")
ax.plot(J_pos_a, f7_pos_a, "s--", color="#00BFFF", lw=2, ms=7, label="π=+ 1ℏω yrast")
ax.axhline(1.0, color="white", lw=0.7, ls=":", alpha=0.35)
ax.set_ylabel("$\\nu(0f_{7/2})$", fontsize=11)
ax.set_xlabel("Spin J", fontsize=11)
ax.set_title("Yrast $\\nu(0f_{7/2})$: both parities compared", fontsize=10)
ax.legend(fontsize=8)
ax.grid(True, which="both", alpha=0.12)

# ── shared formatting ─────────────────────────────────────────────────────────
for row in axes:
    for ax in row:
        ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        ax.xaxis.set_minor_locator(ticker.MultipleLocator(1))

plt.tight_layout(rect=[0, 0, 1, 0.97])
out = f"{BASE}/38Cl_f7_occupancy_vs_spin.png"
plt.savefig(out, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
print(f"Saved: {out}")
plt.show()
