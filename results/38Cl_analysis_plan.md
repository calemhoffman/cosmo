# ³⁸Cl Nuclear Structure: Deep Analysis Plan

## 1. Overview

This document outlines a systematic analysis and interpretation strategy for experimental ³⁸Cl γ-ray data and FSU9 shell model calculations in the sd-pf model space.

---

## 2. Data Summary

### Experimental (GLS file)
| Band | States | J^π range | E_max (keV) | Notes |
|------|--------|-----------|-------------|-------|
| 1 (yrast-like) | 14 | 2⁻ – 11⁺ | 8422 | Definite spin-parity most states |
| 2 (yrare) | 11 | ()–(11⁺) | 12063 | Many tentative; several with unknown parity |

**Ground state:** 2⁻ at 0 keV; **Known isomer:** 5⁻ at 671 keV (T₁/₂ = 715 ms).  
Level scheme shows two interwoven positive- and negative-parity cascades connected by E1 cross-talk transitions.

### Theoretical (all FSU9, Lubna et al. 2019–2020)
| File | HWMAX | Parity | J range | Comment |
|------|-------|--------|---------|---------|
| `fsu9+_merged` | 0 (0ℏω) | + | 0–13⁺ | Normal positive-parity configurations |
| `fsu9+3hw_merged` | 3 (3ℏω) | + | 10–13⁺ | Intruder states, high-spin only |
| `fsu9-_merged` | 0 (0ℏω) | – | 0–9⁻ | Normal negative-parity; 1 νf₇/₂ |
| `fsu9_2hw-_merged` | 2 (2ℏω) | – | 6–13⁻ | 2-particle-2-hole across N=20 |

---

## 3. Key Observational Results

### 3a. Positive-Parity Yrast Line
- **FSU9 0ℏω** reproduces the yrast positive-parity energies remarkably well from **J=5⁺ through J=9⁺**, with deviations typically ≤ 500 keV.
- At **J=10⁺ and above**, the 0ℏω curve rises steeply (~10 MeV at J=12⁺) while experiment plateaus near ~8.4–9.6 MeV — a clear signal that normal configurations are **exhausting their spin capacity**.
- **FSU9 3ℏω** brings the theoretical yrast line down to ~11–12 MeV at J=11–12⁺, much closer to observation. The systematic ~1–2 MeV over-prediction at these spins is a residual of the 3ℏω basis truncation.
- The observed 10(+) state at 7780 keV and 11⁺ at 8422 keV lie *between* the 0ℏω and 3ℏω predictions — consistent with a **mixing of normal and cross-shell configurations**.

### 3b. Negative-Parity Yrast Line
- **FSU9 0ℏω** reproduces the low-spin negative-parity states (2⁻ ground state, 5⁻ isomer, 3⁻, 4⁻) well within ~500 keV through J=5⁻.
- At J=6⁻ the 0ℏω prediction collapses — it rises abruptly to **~8–9 MeV** for the 6⁻ yrast, while the only experimental data point (6⁻ at 4220 keV in Band 2, tentative) sits ~4.2 MeV. **The 0ℏω space is fundamentally exhausted at J=6⁻.**
- **FSU9 2ℏω** predicts the 6⁻ yrast at Ex ≈ 0 MeV (renormalized), rising smoothly to ~10–12 MeV at J=12⁻. This matches the experimental tentative (8⁻) at 5795 keV and (9⁺) at 7294 quite well in trend.
- The 2ℏω band represents **genuinely intruder (cross-shell) structure**, with 2 protons or neutrons promoted across the N=20 gap.

### 3c. Orbital Occupancies
- **Yrast positive-parity states**: At low spin (J=2⁺–5⁺), the valence neutron primarily fills the 0f₇/₂ orbital (~1.2–1.5 occupancy with ~1.4 N=0f₇/₂). As spin increases to J=7⁺–9⁺, the neutron 0f₇/₂ occupancy saturates near 1.6–1.9. At J=10⁺–12⁺, the proton sector also shows marked 0d₃/₂ depletion and 0f₇/₂ promotion, indicating **both proton and neutron cross-shell excitations** at the highest spins.
- **Yrare positive-parity states**: Show systematically *lower* 0f₇/₂ neutron occupancy (~1.2–1.5) compared to yrast at the same spin — consistent with the yrare being a lower-f₇/₂-coupling partner state. The **delta plot (yrare – yrast)** shows:
  - *Negative* Δ(0f₇/₂-N) for J=2⁺–9⁺: yrare has less f₇/₂ neutron content.
  - *Positive* Δ(0d₃/₂-N) for low spins: yrare states are more sd-like.
  - At J=10⁺, the delta flips: the yrast now has a *lower* f₇/₂ contribution than the first yrare at J=10⁺, indicating a **band crossing** in the theoretical structure at high spin.
- **Phenomenological interpretation**: The yrast band at high spin arises from proton-neutron alignment with paired f₇/₂ nucleons, while the yrare band retains more sd character — a classic signature of sd-pf valence space mixing.

---

## 4. Quantifying Theory Quality

### 4a. Recommended Metrics to Compute

| Metric | Formula | What it tells you |
|--------|---------|-------------------|
| **RMS deviation** | σ = √[Σ(E_th − E_exp)²/N] | Overall scale of error |
| **Mean signed error** | μ = Σ(E_th − E_exp)/N | Systematic shift (compression/expansion) |
| **Yrast level ordering score** | Fraction of J-states correctly ordered | Structural fidelity |
| **Normalized χ²** | Σ[(E_th − E_exp)/ΔE_exp]² / N | Weight by experimental uncertainty |

**Recommended groupings:**
- Low-spin negative parity: J=2⁻–5⁻ vs. 0ℏω prediction
- High-spin negative parity: J=6⁻–9⁻ vs. 2ℏω prediction
- Low-spin positive parity: J=5⁺–9⁺ vs. 0ℏω prediction
- High-spin positive parity: J=10⁺–12⁺ vs. 3ℏω prediction

**Expected findings (estimated from comparisons):**
- 0ℏω negative parity at J≤5: RMS ≲ 400 keV → **Good** agreement (confidence: high)
- 2ℏω negative parity at J=6–8: RMS ≲ 700 keV → **Reasonable** (confidence: medium; sparse data)
- 0ℏω positive parity at J=5–9: RMS ≲ 400 keV → **Excellent** (confidence: high)
- 3ℏω positive parity at J=10–12: RMS ~1–2 MeV → **Qualitative** (confidence: medium; basis truncation)

### 4b. Transition Strengths (not yet computed)
Calculate B(M1) and B(E2) for experimentally measured transitions (intensities and multipolarities in GLS file) and compare to shell model via:
- Effective g-factors: g_s(eff) = 0.75 g_s(free)
- Effective charges: e_p = 1.35e, e_n = 0.35e (standard)
These provide **independent tests** of the wavefunctions beyond energies alone.

---

## 5. Nuclear Physics Conclusions

### 5a. Strong Conclusions (High Confidence)

**C1: 38Cl is not a pure sd-shell nucleus above J=5ℏ.**  
The FSU9 0ℏω model fails to predict the negative-parity states above J=5⁻ and positive-parity states above J=9⁺. The 21st neutron in the 0f₇/₂ orbital — responsible for the 5⁻ isomer at 671 keV — must be supplemented by additional cross-shell excitations to generate the observed level densities and γ-ray cascade structure at high spin. *Confidence: very high (the 0ℏω failure is structural, not numerical).*

**C2: The 5⁻ isomeric state is well-understood as a one-neutron f₇/₂ configuration.**  
The 0ℏω FSU9 calculation places the 5⁻ at Ex ≈ 584 MeV above the negative-parity ground state (in the 0ℏω renormalization), consistent with the experimental 671 keV. The low E_x and near-unity νf₇/₂ occupancy (~1.0 in the 0ℏω calculation) confirm this state as a nearly pure ν(0f₇/₂)¹ configuration coupled to the sd-shell proton core. The small isomeric lifetime (715 ms) arises from the M2 transition character coupling the 5⁻ and 2⁻ states across the parity change. *Confidence: high.*

**C3: High-spin positive-parity states require proton excitations into the fp shell.**  
The occupancy plots show that at J=10⁺ and above, both neutron 0f₇/₂ and proton 0d₃/₂→0f₇/₂ excitations are needed. This is consistent with a picture where the ground-state neutron is already in 0f₇/₂, and achieving J=10⁺ requires an additional fp proton. This predicts non-trivial spectroscopic factors in proton pickup/stripping reactions — measurable via (p,d) or (³He,d) experiments.

**C4: The yrast and yrare positive-parity bands exhibit distinct f₇/₂ character.**  
The yrast band has systematically higher neutron 0f₇/₂ occupancy than the yrare band at the same spin (confirmed by the delta plot). This "bifurcation" is analogous to the behavior seen in fp-shell nuclei where competing f₇/₂ alignments generate doublet structures. The yrast/yrare separation (~0.5–2 MeV) represents the residual n-p interaction energy for the f₇/₂-coupled pair.

### 5b. Moderate Conclusions (Medium Confidence)

**C5: A band crossing likely occurs near J=10⁺, ~8–9 MeV.**  
The experimental 10(+) at 7780 keV appears between the 0ℏω and 3ℏω theoretical predictions. This is consistent with a crossing between the normal (0ℏω) configuration becoming yrare and an intruder (3ℏω or multi-quasiparticle) state becoming yrast. The two 11⁺ states observed at 8422 and 9608 keV (and the (11⁺) at 12063 keV) are quantitatively consistent with such a crossing. *Limitation: only tentative spin assignments exist above 8422 keV.*

**C6: Negative-parity band above J=6⁻ is dominated by 2ℏω (2p-2h) cross-shell excitations.**  
The 2ℏω calculation tracks the experimental tentative negative-parity levels from J=6⁻ to J=8⁻ in trend. The 6⁻ at 4220 keV and tentative (8⁻) at 5795 keV are consistent with the bottom of the 2p-2h band after renormalization to the 2ℏω ground state. The occupancy data show ~2.4–2.6 neutrons in 0f₇/₂ for these states (vs. ~1.0 in the 0ℏω ground state). *Limitation: 2ℏω energies depend on poorly known sd-fp cross-shell matrix elements; experimental assignments are tentative.*

**C7: The N=20 shell gap in 38Cl is weaker than the pure sd limit.**  
The relatively low excitation energies of the intruder-dominated states (e.g., 6⁻ excitation only 4.2 MeV) compared to the 0ℏω prediction (~8 MeV) implies significant softening of the N=20 gap for Z=17 (Cl). This places ³⁸Cl in the same systematic trend as the approaching island of inversion near Z=8–12, N=20, albeit not as dramatic. *Confidence: medium — alternative structural interpretations exist for the 6⁻ assignment.*

### 5c. Speculative Observations (Lower Confidence, for Future Investigation)

**C8: The yrare band at high spin (~J=10⁺, E_x > 7 MeV) may contain shape-coexisting structures.**  
The high excitation energies of the yrare states (9608, 10503, 12063 keV) with poorly determined spins could signal the onset of deformed configurations (e.g., prolate collective rotation). The FSU9 3ℏω calculation shows multiple close-lying 10⁺–12⁺ states which could mix. *This is highly speculative given the current data quality.*

**C9: Comparison with 38Ar, 37Cl, and 39Cl may quantify the Z=17 single-particle energies.**  
The FSU9 interaction was fit broadly; ³⁸Cl (Z=17, N=21) lies one particle away from ³⁷Cl (Z=17, N=20) and the 0d₃/₂ closure. A systematic comparison of the 0f₇/₂ occupancies across this chain would directly probe the πd₃/₂-νf₇/₂ monopole interaction central to the FSU9 fit.

---

## 6. Key Limitations

| Limitation | Impact | Severity |
|------------|--------|----------|
| Tentative spin-parity above 8.4 MeV | Cannot confirm band crossing | **High** |
| Missing parity assignments for several yrare states | Cannot test negative-parity theory at J>8 | **High** |
| 3ℏω truncated to high-J only | No 3ℏω low-spin comparison | **Medium** |
| 2ℏω restricted to negative parity only | 2ℏω positive-parity intruders unevaluated | **Medium** |
| No transition strength (B(M1)/B(E2)) calculations | Can't test wavefunctions independently | **Medium** |
| Experimental intensities lack absolute normalization | Cannot convert to B(M1/E2)/Weisskopf units | **Medium** |
| Only one cross-talk E1 cluster measured in yrare band | Limited inter-band connectivity | **Low-Medium** |
| No Doppler-shift lifetime measurements | Cannot derive absolute B(ML) values | **Medium** |

---

## 7. Proposed Deeper Analysis Steps

### Step 1: Quantitative Energy Comparison Table
Create a state-by-state comparison table:
```
| J^π | E_exp (keV) | E_th 0ℏω (keV) | E_th 2/3ℏω (keV) | ΔE_0 | ΔE_2/3 |
```
for all experimentally known states. Compute RMS deviations per parity/model-space grouping.

### Step 2: Transition Strength Analysis

For each gamma in the GLS file with a measured intensity and multipolarity:
1. Convert relative intensities to a common normalization (e.g., strongest transition = 100).
2. Use Weisskopf estimates to assess the plausibility of spin-parity assignments (are M1/E2 rates physically reasonable?).
3. Compare measured DCO/polarization ratios (if available) against predicted mixing ratios δ(E2/M1) from the shell model.

### Step 3: Occupancy Spin-Systematics Plot
Plot ν(0f₇/₂) occupancy vs. J for both yrast and yrare bands on the same axis (like a "spin alignment curve"). This is the expectation value ⟨n_f7/2⟩(J). A linear rise followed by a plateau is the signature of sequential particle alignment ("backbending" precursor).

### Step 4: Neighboring Nuclei Comparison
- **³⁸Ar (Z=18, N=20):** Magic N=20 core; its ground state and low-lying levels anchor the sd-shell reference. Compare FSU9 predictions for ³⁸Ar.
- **³⁷Cl (Z=17, N=20):** One neutron removed from the 0f₇/₂ orbital. Spectroscopic factors from ³⁸Cl(p,d)³⁷Cl would directly measure the ν0f₇/₂ single-particle strength.
- **³⁹Cl (Z=17, N=22):** Two neutrons in 0f₇/₂; expected to show larger 0f₇/₂ occupancy and potentially a stronger band mixing scenario.
- **³⁷S (Z=16, N=21):** Mirror partner analogue of ³⁷Cl; isospin symmetry test.

### Step 5: Theory–Experiment χ² Map vs. Effective Interaction Parameters
Vary the πd₃/₂–νf₇/₂ monopole matrix element (key FSU9 parameter) by ±20% and examine how the yrast energies respond. This gives a sensitivity estimate and a measure of how well ³⁸Cl constrains the interaction.

### Step 6: Band Crossing Analysis
Project the two theoretical yrast lines (0ℏω and 3ℏω) onto the same excitation energy axis. Find the crossing spin J_x at which 3ℏω becomes lower in energy. Compare J_x to the experimental observation of where the level scheme changes character (E_γ compression, intensity redistribution). This gives a model-independent way to identify where the dominant configuration changes.

---

## 8. Future Experimental Directions (Cautious)

| Measurement | Technique | Expected Insight | Feasibility |
|-------------|-----------|-----------------|-------------|
| RDCO/polarization for 6⁻, (8⁻) states | Coincidence γ-ray array | Confirm negative-parity parity assignments | **Medium** (requires sufficient statistics) |
| Lifetime of 6⁺, 7⁺, 8⁺ states | DSAM or RDM | B(E2)/B(M1) → quadrupole deformation | **Feasible** with existing data? |
| ³⁸Cl(p, d) or ³⁹Cl(d,t) transfer | Magnetic spectrometer | Spectroscopic factors for νf₇/₂ | **Challenging** (radioactive target) |
| ³⁶S(⁵He,³H)³⁸Cl charge exchange | In-beam | Establish T=1 analog states | **Technically demanding** |
| γ-ray angular distributions | Re-analysis if raw data exists | Confirm/upgrade tentative assignments | **High value if data exists** |
| Isomer tagging of 5⁻ at 671 keV | Coincidence gating | Cleanly separate yrare decay paths | **Recommended** |

---

## 9. Connection to Regional Nuclear Physics

³⁸Cl fills a critical position in the A≈38 isobaric chain:

```
      Z
18 │ ³⁸Ar (N=20 magic): closed sd shell, 0⁺ g.s.
17 │ ³⁸Cl (N=21): one νf₇/₂, 2⁻ g.s., 5⁻ isomer   ← this work
   │ ³⁷Cl (N=20): doubly (sub-)magic, 3/2⁺ g.s.
16 │ ³⁸S  (N=22): 0⁺ g.s., well-studied
   │ ³⁶S  (N=20): 0⁺ g.s.
      N  20  21  22
```

The evolution from the N=20 closed shell in ³⁸Ar → ³⁸Cl (adding one neutron to 0f₇/₂) demonstrates:
1. **Shell-gap robustness**: the 0f₇/₂ single-particle energy is ~2-3 MeV above the sd shell at Z=17.
2. **sd-pf mixing onset**: the relatively low energy of cross-shell states (6⁻ at ~4 MeV) compared to the N=20 gap (~6 MeV in ⁴¹Ca) shows Z=17 is softer than the proton-magic N=20 systems.
3. **Isomeric structure**: the 5⁻ isomer is qualitatively the same as the 5⁻ isomers in ³⁸mCl (T₁/₂=715 ms), ³⁴mCl, etc. — all arising from maximum νf₇/₂ alignment.

---

## 10. Publishing Strategy (if applicable)

A complete paper on this data set should include:

1. **Introduction:** Motivation; ³⁸Cl in context of N≈20 sd-pf shell evolution.
2. **Experimental:** Reaction details, detector setup, GLS construction method.
3. **Results:** Full level scheme with uncertainties; spin-parity evidence (DCO, polarization if available).
4. **Shell Model:** FSU9 comparison for all four model spaces; quantitative metrics.
5. **Discussion:** Occupancy analysis; band crossing; comparison to ³⁷Cl, ³⁸Ar, ³⁹Cl.
6. **Conclusions:** What is learned about N=20 gap, πd₃/₂-νf₇/₂ monopole, high-spin intruder structure.

**Key figures needed beyond what exists:**
- [ ] Quantitative bar chart of |E_th − E_exp| per model space
- [ ] Spin vs. ν(0f₇/₂) occupancy curve (yrast and yrare)
- [ ] B(M1)/B(E2) comparison table (requires calculation)
- [ ] Comparison of yrast line with neighboring nuclei (³⁷Cl, ³⁹Cl)

---

*Document prepared: February 2026. All theoretical results from FSU9 interaction (Lubna et al., PRC 100, 034308, 2019; PRR 2, 043342, 2020). Experimental data from GLS file (D.C. Radford format, Jan 2026).*
