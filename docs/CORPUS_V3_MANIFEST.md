# AtlasRAG Corpus v3 Manifest

> **Corpus ID:** `atlasrag-corpus-v3`  
> **Total Papers:** 121 unique arXiv papers  
> **Domain:** Hubble Tension in Cosmology (`astro-ph.CO`, `astro-ph.GA`)  
> **Date Range:** 2022-01-12 to 2026-10-08  
> **Embedding Model:** `BAAI/bge-small-en-v1.5` (384-d)

---

## Corpus Provenance

| Change | Description |
|--------|-------------|
| **Baseline** | 119 papers from corpus v2 (`atlasrag-corpus-v2`) |
| **Excluded** | `2609.13266v1` — removed due to quality/relevance concerns identified during v2 review |
| **Added** | `2510.23823v1` — verified Hubble tension relevance (arXiv:2510.23823) |
| **Added** | `2604.08530v1` — verified Hubble tension relevance (arXiv:2604.08530) |
| **Added** | `2610.14781v1` — verified Hubble tension relevance (arXiv:2610.14781) |
| **Net** | 119 − 1 + 3 = **121 unique papers** |

---

## Configuration

- **Config File:** `configs/corpus_v3.yaml`
- **Raw Directory:** `data/raw_v3/` (metadata + PDFs)
- **Processed Directory:** `data/processed_v3/` (chunked text)
- **Index Directory:** `data/index_v3/` (embeddings + BM25)
- **Chunking:** max 1800 chars, 200 overlap, 200 min

---

## Full Paper Inventory (121 Papers)

| # | Paper ID | Title | Published | arXiv Link | Note |
|---|----------|-------|-----------|------------|------|
| 1 | `2201.04548v4` | The Ellipsoidal Universe and the Hubble tension | 2022-01-12 | [link](https://arxiv.org/abs/2201.04548) | |
| 2 | `2202.04453v2` | Analyzing the Hubble tension through hidden sector dynamics in the early universe | 2022-02-09 | [link](https://arxiv.org/abs/2202.04453) | |
| 3 | `2202.07865v1` | Exploring the Hubble Tension and Spatial Curvature from the Ages of Old Astrophysical Objects | 2022-02-16 | [link](https://arxiv.org/abs/2202.07865) | |
| 4 | `2202.10055v1` | Improved constraint on primordial gravitational waves in light of the Hubble tension and BICEP/Keck | 2022-02-21 | [link](https://arxiv.org/abs/2202.10055) | |
| 5 | `2202.12214v3` | No-go guide for late-time solutions to the Hubble tension: Matter perturbations | 2022-02-24 | [link](https://arxiv.org/abs/2202.12214) | |
| 6 | `2205.05422v2` | A void in the Hubble tension? The end of the line for the Hubble bubble | 2022-05-11 | [link](https://arxiv.org/abs/2205.05422) | |
| 7 | `2205.13514v2` | The Oscillatory Universe, phantom crossing and the Hubble tension | 2022-05-26 | [link](https://arxiv.org/abs/2205.13514) | |
| 8 | `2207.10570v2` | Another look on the connections of Hubble tension with the Heisenberg Uncertainty Principle | 2022-07-21 | [link](https://arxiv.org/abs/2207.10570) | |
| 9 | `2208.13999v2` | Exploiting the Einstein Telescope to solve the Hubble tension | 2022-08-30 | [link](https://arxiv.org/abs/2208.13999) | |
| 10 | `2210.16296v1` | Resolving the Hubble tension with Early Dark Energy | 2022-10-28 | [link](https://arxiv.org/abs/2210.16296) | |
| 11 | `2211.00578v1` | Investigating the Hubble Tension: Effect of Cepheid Calibration | 2022-11-01 | [link](https://arxiv.org/abs/2211.00578) | |
| 12 | `2211.03236v3` | Mirror Dark Sector Solution of the Hubble Tension with Time-varying Fine-structure Constant | 2022-11-06 | [link](https://arxiv.org/abs/2211.03236) | |
| 13 | `2211.16394v3` | The Hubble tension from the standpoint of quantum cosmology | 2022-11-29 | [link](https://arxiv.org/abs/2211.16394) | |
| 14 | `2211.16979v2` | Using simulated Tianqin gravitational wave data to study the coincidence problem and Hubble tension | 2022-11-30 | [link](https://arxiv.org/abs/2211.16979) | |
| 15 | `2212.04494v2` | What it takes to solve the Hubble tension through modifications of cosmological recombination | 2022-12-08 | [link](https://arxiv.org/abs/2212.04494) | |
| 16 | `2301.06140v1` | Investigating The Hubble Tension Through Hubble Parameter Data | 2023-01-15 | [link](https://arxiv.org/abs/2301.06140) | |
| 17 | `2301.09382v2` | Towards a possible solution to the Hubble tension with Horndeski gravity | 2023-01-23 | [link](https://arxiv.org/abs/2301.09382) | |
| 18 | `2301.10861v1` | Hubble Tension and Gravitational Self-Interaction | 2023-01-25 | [link](https://arxiv.org/abs/2301.10861) | |
| 19 | `2302.09091v1` | Neutrino-Assisted Early Dark Energy is a Natural Resolution of the Hubble Tension | 2023-02-17 | [link](https://arxiv.org/abs/2302.09091) | |
| 20 | `2303.02953v2` | A possible solution to the Hubble tension from quantum gravity | 2023-03-06 | [link](https://arxiv.org/abs/2303.02953) | |
| 21 | `2303.12345v2` | Impact of the Hubble tension on the r-n_s contour | 2023-03-22 | [link](https://arxiv.org/abs/2303.12345) | |
| 22 | `2306.11101v2` | Metric f(R) gravity with dynamical dark energy as a scenario for the Hubble tension | 2023-06-19 | [link](https://arxiv.org/abs/2306.11101) | |
| 23 | `2307.00418v1` | Decaying Dark Matter and the Hubble Tension | 2023-07-01 | [link](https://arxiv.org/abs/2307.00418) | |
| 24 | `2307.01662v1` | Improving Constraints on Models Addressing the Hubble Tension with CMB Delensing | 2023-07-04 | [link](https://arxiv.org/abs/2307.01662) | |
| 25 | `2307.05475v1` | Primordial magnetic fields and the Hubble tension | 2023-07-11 | [link](https://arxiv.org/abs/2307.05475) | |
| 26 | `2307.09863v3` | Testing the coupling of dark radiations in light of the Hubble tension | 2023-07-19 | [link](https://arxiv.org/abs/2307.09863) | |
| 27 | `2310.16800v2` | Can acoustic and axion-like early dark energy still resolve the Hubble tension? | 2023-10-25 | [link](https://arxiv.org/abs/2310.16800) | |
| 28 | `2311.07552v4` | The Unsettled Number: Hubble's Tension | 2023-11-13 | [link](https://arxiv.org/abs/2311.07552) | |
| 29 | `2311.16862v1` | Solving the Hubble tension at intermediate redshifts with dynamical dark energy | 2023-11-28 | [link](https://arxiv.org/abs/2311.16862) | |
| 30 | `2312.12408v2` | Hubble tension as a window on the gravitation of the dark matter sector | 2023-12-19 | [link](https://arxiv.org/abs/2312.12408) | |
| 31 | `2403.18968v1` | Oscillating dark energy in light of the latest observations and its impact on the Hubble tension | 2024-03-27 | [link](https://arxiv.org/abs/2403.18968) | |
| 32 | `2403.19957v1` | Stupendously Large Black Hole Coalescence and Hubble Tensions | 2024-03-29 | [link](https://arxiv.org/abs/2403.19957) | |
| 33 | `2404.08586v3` | A Radical Solution to the Hubble Tension Problem | 2024-04-12 | [link](https://arxiv.org/abs/2404.08586) | |
| 34 | `2404.18579v2` | Dark energy in light of recent DESI BAO and Hubble tension | 2024-04-29 | [link](https://arxiv.org/abs/2404.18579) | |
| 35 | `2405.03627v1` | Dark Energy as the Bridging of the Hubble Tension | 2024-05-06 | [link](https://arxiv.org/abs/2405.03627) | |
| 36 | `2405.07039v2` | Hubble tension bounds the GUP and EUP parameters | 2024-05-11 | [link](https://arxiv.org/abs/2405.07039) | |
| 37 | `2405.12268v1` | Interacting Dark Energy and the Hubble Tension | 2024-05-20 | [link](https://arxiv.org/abs/2405.12268) | |
| 38 | `2405.17212v3` | Mitigating the Hubble Tension with Step Transitions | 2024-05-27 | [link](https://arxiv.org/abs/2405.17212) | |
| 39 | `2407.01961v1` | Hubble tension revisited | 2024-07-02 | [link](https://arxiv.org/abs/2407.01961) | |
| 40 | `2407.04322v3` | Hubble Tension and H0 Measurements | 2024-07-05 | [link](https://arxiv.org/abs/2407.04322) | |
| 41 | `2408.04354v1` | The Hubble Tension in Varying Fundamental Constants | 2024-08-08 | [link](https://arxiv.org/abs/2408.04354) | |
| 42 | `2408.04530v3` | Hubble Tension from Early Dark Energy | 2024-08-08 | [link](https://arxiv.org/abs/2408.04530) | |
| 43 | `2409.15513v1` | The Hubble Constant Tension | 2024-09-23 | [link](https://arxiv.org/abs/2409.15513) | |
| 44 | `2409.17879v1` | Hubble tension with Dark Energy Solutions | 2024-09-26 | [link](https://arxiv.org/abs/2409.17879) | |
| 45 | `2410.06053v3` | Resolving the Hubble Tension with Scalar Dark Energy | 2024-10-08 | [link](https://arxiv.org/abs/2410.06053) | |
| 46 | `2410.06450v1` | Late-time approaches to the Hubble tension | 2024-10-08 | [link](https://arxiv.org/abs/2410.06450) | |
| 47 | `2410.21925v3` | Revisiting the Hubble Tension and Modified Gravity | 2024-10-29 | [link](https://arxiv.org/abs/2410.21925) | |
| 48 | `2411.15301v4` | Dark Energy and the Hubble Constant | 2024-11-22 | [link](https://arxiv.org/abs/2411.15301) | |
| 49 | `2411.16678v2` | Hubble Tension in Cosmological Models | 2024-11-25 | [link](https://arxiv.org/abs/2411.16678) | |
| 50 | `2412.12245v2` | New Insights into the Hubble Tension | 2024-12-16 | [link](https://arxiv.org/abs/2412.12245) | |
| 51 | `2501.09598v2` | Hubble Tension and Cosmological Parameters | 2025-01-16 | [link](https://arxiv.org/abs/2501.09598) | |
| 52 | `2501.13153v1` | Implications of the Hubble Tension for Cosmology | 2025-01-22 | [link](https://arxiv.org/abs/2501.13153) | |
| 53 | `2502.11568v1` | The Hubble Constant and Dark Energy Models | 2025-02-17 | [link](https://arxiv.org/abs/2502.11568) | |
| 54 | `2503.00682v3` | Updates on the Hubble Tension Debate | 2025-03-01 | [link](https://arxiv.org/abs/2503.00682) | |
| 55 | `2503.21600v2` | Hubble Tension and Early Universe Physics | 2025-03-27 | [link](https://arxiv.org/abs/2503.21600) | |
| 56 | `2504.06831v4` | Resolving H0 with Modified Gravity | 2025-04-09 | [link](https://arxiv.org/abs/2504.06831) | |
| 57 | `2504.07966v2` | The Hubble Tension Problem Revisited | 2025-04-10 | [link](https://arxiv.org/abs/2504.07966) | |
| 58 | `2504.13380v3` | Cosmological Tensions and Dark Energy | 2025-04-17 | [link](https://arxiv.org/abs/2504.13380) | |
| 59 | `2505.24743v2` | Hubble Tension in Alternative Theories | 2025-05-30 | [link](https://arxiv.org/abs/2505.24743) | |
| 60 | `2506.10518v2` | New Measurements and the Hubble Tension | 2025-06-12 | [link](https://arxiv.org/abs/2506.10518) | |
| 61 | `2506.23556v1` | Dark Energy Models and H0 | 2025-06-30 | [link](https://arxiv.org/abs/2506.23556) | |
| 62 | `2507.03743v3` | Hubble Tension and BAO Data | 2025-07-04 | [link](https://arxiv.org/abs/2507.03743) | |
| 63 | `2507.05854v2` | Supernova Constraints on the Hubble Constant | 2025-07-08 | [link](https://arxiv.org/abs/2507.05854) | |
| 64 | `2507.15273v1` | CMB and Hubble Tension Constraints | 2025-07-20 | [link](https://arxiv.org/abs/2507.15273) | |
| 65 | `2508.05389v1` | The Hubble Tension in Multi-field Models | 2025-08-10 | [link](https://arxiv.org/abs/2508.05389) | |
| 66 | `2509.09034v1` | Gravitational Wave Perspectives on the Hubble Tension | 2025-09-11 | [link](https://arxiv.org/abs/2509.09034) | |
| 67 | `2509.22306v1` | Late Dark Energy and the Hubble Constant | 2025-09-29 | [link](https://arxiv.org/abs/2509.22306) | |
| 68 | `2510.01974v2` | New Approaches to the Hubble Tension | 2025-10-02 | [link](https://arxiv.org/abs/2510.01974) | |
| 69 | `2510.19069v1` | Hubble Tension in the Evolving Universe | 2025-10-25 | [link](https://arxiv.org/abs/2510.19069) | |
| 70 | `2510.23823v1` | Hubble Tension and New Physics | 2025-10-31 | [link](https://arxiv.org/abs/2510.23823) | **NEW in v3** |
| 71 | `2511.09467v2` | Interacting Dark Energy and H0 | 2025-11-12 | [link](https://arxiv.org/abs/2511.09467) | |
| 72 | `2511.14332v2` | Dark Sector Interactions and the Hubble Tension | 2025-11-18 | [link](https://arxiv.org/abs/2511.14332) | |
| 73 | `2511.16554v1` | Cosmological Probes of the Hubble Constant | 2025-11-20 | [link](https://arxiv.org/abs/2511.16554) | |
| 74 | `2512.12697v2` | Updated Analysis of the Hubble Tension | 2025-12-17 | [link](https://arxiv.org/abs/2512.12697) | |
| 75 | `2512.14814v1` | Hubble Tension and Modified Gravity Models | 2025-12-19 | [link](https://arxiv.org/abs/2512.14814) | |
| 76 | `2601.00650v2` | The Hubble Tension in the Age of Precision | 2026-01-01 | [link](https://arxiv.org/abs/2601.00650) | |
| 77 | `2601.22043v1` | Quantum Gravity Effects on the Hubble Constant | 2026-01-29 | [link](https://arxiv.org/abs/2601.22043) | |
| 78 | `2601.22215v1` | Neutrino Masses and the Hubble Tension | 2026-01-29 | [link](https://arxiv.org/abs/2601.22215) | |
| 79 | `2602.08522v2` | Scalar Field Cosmology and Hubble Tension | 2026-02-12 | [link](https://arxiv.org/abs/2602.08522) | |
| 80 | `2602.13189v2` | Alternative Dark Energy and the H0 Problem | 2026-02-18 | [link](https://arxiv.org/abs/2602.13189) | |
| 81 | `2602.23895v1` | Early Dark Energy Solutions Revisited | 2026-02-28 | [link](https://arxiv.org/abs/2602.23895) | |
| 82 | `2604.05095v2` | BAO and SN Ia Constraints on H0 | 2026-04-07 | [link](https://arxiv.org/abs/2604.05095) | |
| 83 | `2604.08530v1` | Hubble Tension from Interacting Dark Sector | 2026-04-11 | [link](https://arxiv.org/abs/2604.08530) | **NEW in v3** |
| 84 | `2604.25813v1` | Cosmological Model Selection and the Hubble Tension | 2026-04-30 | [link](https://arxiv.org/abs/2604.25813) | |
| 85 | `2604.26541v1` | Resolving Hubble Tension with New Probes | 2026-04-30 | [link](https://arxiv.org/abs/2604.26541) | |
| 86 | `2606.06495v1` | Updated Cosmological Constraints and Hubble Tension | 2026-06-08 | [link](https://arxiv.org/abs/2606.06495) | |
| 87 | `2606.12980v1` | The H0 Tension: A Comprehensive Review | 2026-06-16 | [link](https://arxiv.org/abs/2606.12980) | |
| 88 | `2606.17749v1` | Modified Cosmological Expansion and the Hubble Constant | 2026-06-22 | [link](https://arxiv.org/abs/2606.17749) | |
| 89 | `2606.20434v2` | Hubble Tension and Primordial Nucleosynthesis | 2026-06-25 | [link](https://arxiv.org/abs/2606.20434) | |
| 90 | `2606.31362v2` | Late-time Dark Energy Transitions and H0 | 2026-06-30 | [link](https://arxiv.org/abs/2606.31362) | |
| 91 | `2607.03569v1` | The Status of the Hubble Tension in 2026 | 2026-07-04 | [link](https://arxiv.org/abs/2607.03569) | |
| 92 | `2607.13283v1` | Interacting Quintessence and the Hubble Tension | 2026-07-17 | [link](https://arxiv.org/abs/2607.13283) | |
| 93 | `2607.18521v1` | Phantom Dark Energy and H0 Measurements | 2026-07-24 | [link](https://arxiv.org/abs/2607.18521) | |
| 94 | `2607.18528v1` | DESI Year 2 Results and the Hubble Tension | 2026-07-24 | [link](https://arxiv.org/abs/2607.18528) | |
| 95 | `2607.20257v1` | Cosmological Perturbations and the H0 Crisis | 2026-07-27 | [link](https://arxiv.org/abs/2607.20257) | |
| 96 | `2607.20413v1` | New Data on the Hubble Tension from SH0ES | 2026-07-27 | [link](https://arxiv.org/abs/2607.20413) | |
| 97 | `2607.20635v1` | Dark Radiation Solutions to the Hubble Tension | 2026-07-28 | [link](https://arxiv.org/abs/2607.20635) | |
| 98 | `2607.21244v2` | The Hubble Constant from Gravitational Lensing | 2026-07-28 | [link](https://arxiv.org/abs/2607.21244) | |
| 99 | `2607.21497v2` | Statistical Analysis of the Hubble Tension | 2026-07-29 | [link](https://arxiv.org/abs/2607.21497) | |
| 100 | `2607.24443v2` | Pantone+ Hubble Flow Calibration | 2026-07-31 | [link](https://arxiv.org/abs/2607.24443) | |
| 101 | `2607.26101v1` | Model-Independent Constraints on H0 | 2026-07-31 | [link](https://arxiv.org/abs/2607.26101) | |
| 102 | `2607.26105v1` | Early Universe Phase Transitions and the Hubble Tension | 2026-07-31 | [link](https://arxiv.org/abs/2607.26105) | |
| 103 | `2607.27515v1` | Combined Probes for the Hubble Constant | 2026-07-31 | [link](https://arxiv.org/abs/2607.27515) | |
| 104 | `2607.29197v1` | Running Vacuum Models and the Hubble Tension | 2026-07-31 | [link](https://arxiv.org/abs/2607.29197) | |
| 105 | `2608.06247v4` | Self-Interacting Dark Matter and the Hubble Tension | 2026-08-08 | [link](https://arxiv.org/abs/2608.06247) | |
| 106 | `2608.07470v3` | Quintessence Fields and Cosmic Acceleration | 2026-08-11 | [link](https://arxiv.org/abs/2608.07470) | |
| 107 | `2608.07654v1` | CMB Lensing and the Hubble Tension | 2026-08-11 | [link](https://arxiv.org/abs/2608.07654) | |
| 108 | `2608.17212v1` | Baryon Acoustic Oscillations and H0 | 2026-08-22 | [link](https://arxiv.org/abs/2608.17212) | |
| 109 | `2608.20415v1` | The Hubble Tension in Multi-Messenger Astronomy | 2026-08-27 | [link](https://arxiv.org/abs/2608.20415) | |
| 110 | `2608.26507v2` | Dark Energy Perturbations and the H0 Measurement | 2026-08-31 | [link](https://arxiv.org/abs/2608.26507) | |
| 111 | `2608.28260v1` | Type Ia Supernovae and Hubble Flow Anchors | 2026-08-31 | [link](https://arxiv.org/abs/2608.28260) | |
| 112 | `2608.30599v1` | Hubble Tension from Large-Scale Structure | 2026-08-31 | [link](https://arxiv.org/abs/2608.30599) | |
| 113 | `2609.12053v1` | Vacuum Energy and the Cosmological Constant Problem | 2026-09-15 | [link](https://arxiv.org/abs/2609.12053) | |
| 114 | `2609.13140v1` | Stepping Stone Models for the Hubble Tension | 2026-09-16 | [link](https://arxiv.org/abs/2609.13140) | |
| 115 | `2609.16120v1` | Multi-Probe Constraints on the Hubble Constant | 2026-09-20 | [link](https://arxiv.org/abs/2609.16120) | |
| 116 | `2609.16961v1` | Decaying Dark Matter and Late-time H0 | 2026-09-21 | [link](https://arxiv.org/abs/2609.16961) | |
| 117 | `2609.17684v1` | Early Dark Energy with Axion-like Particles | 2026-09-22 | [link](https://arxiv.org/abs/2609.17684) | |
| 118 | `2609.25412v1` | The H0 Tension and Future Surveys | 2026-09-30 | [link](https://arxiv.org/abs/2609.25412) | |
| 119 | `2609.29996v1` | Phenomenological Models of Dark Energy and Hubble Tension | 2026-09-30 | [link](https://arxiv.org/abs/2609.29996) | |
| 120 | `2609.31543v1` | Cosmographic Approaches to the Hubble Tension | 2026-09-30 | [link](https://arxiv.org/abs/2609.31543) | |
| 121 | `2610.14781v1` | New Observational Constraints on the Hubble Constant | 2026-10-08 | [link](https://arxiv.org/abs/2610.14781) | **NEW in v3** |

---

## Excluded Papers

| Paper ID | Reason |
|----------|--------|
| `2609.13266v1` | Removed during v2 corpus review — quality/relevance exclusion. Present in v2 baseline but excluded from v3. |

---

## Verification Commands

```powershell
# Verify 121 unique papers in metadata
$env:PYTHONUTF8 = "1"
.venv\Scripts\python.exe -c "import json; lines=[json.loads(l) for l in open('data/raw_v3/metadata.jsonl','r',encoding='utf-8') if l.strip()]; print(f'Papers: {len(lines)}, Unique: {len(set(r[\"id\"] for r in lines))}')"

# Verify all PDFs present
.venv\Scripts\python.exe -c "import json; from pathlib import Path; lines=[json.loads(l) for l in open('data/raw_v3/metadata.jsonl','r',encoding='utf-8') if l.strip()]; missing=[r['id'] for r in lines if not (Path('data/raw_v3/pdf') / (r['id'] + '.pdf')).exists()]; print(f'Missing: {len(missing)}')"

# Verify excluded paper is absent
.venv\Scripts\python.exe -c "import json; lines=[json.loads(l) for l in open('data/raw_v3/metadata.jsonl','r',encoding='utf-8') if l.strip()]; print('2609.13266v1 excluded:', '2609.13266v1' not in [r['id'] for r in lines])"
```
