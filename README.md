# COGS 138 Final Project — Posterior Hot Zone EEG Signatures of Dreaming

**Team:** Jayminn Anand, Yann Bellac, Srikar Mannam

## Research question

Do brainwave patterns at the back of the brain look different during REM sleep compared to NREM sleep, in a way that matches the EEG signature of dreaming described by Siclari et al. (2017)?

## Summary

We use the Sleep-EDF Expanded dataset from PhysioNet (~20 subjects, Sleep Cassette portion) to test whether the "posterior hot zone" signature of dreaming — a relative shift away from low-frequency and toward high-frequency activity at posterior cortical regions — can be detected using only two EEG channels: `Fpz-Cz` (frontal) and `Pz-Oz` (posterior). The analysis compares posterior-minus-frontal band-power contrasts between REM and NREM (N2, N3) sleep using paired t-tests across subjects.

See [PROPOSAL.md](PROPOSAL.md) for the full proposal and citations.

## Repo layout

```
.
├── data/raw/             # Sleep-EDF recordings (gitignored, populated by download script)
├── figures/              # Generated figures
├── notebooks/
│   └── exploration.ipynb # Starter notebook walking through the pipeline on one subject
├── results/              # Per-subject band powers, contrasts, t-test outputs (CSV)
├── scripts/
│   ├── download_data.py  # Download Sleep-EDF for selected subjects via MNE
│   └── run_analysis.py   # End-to-end pipeline producing CSVs + figures
└── src/
    ├── data_loader.py    # Load PSG + hypnogram, apply annotations
    ├── preprocessing.py  # Bandpass filter, epoch, stage selection
    ├── features.py       # Welch PSD, band-power, posterior−frontal contrast
    ├── stats.py          # Paired t-tests across subjects
    └── plots.py          # Spectra, boxplots, contrast bar plots
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Download data (defaults to subjects 0–19, night 1):

```bash
python scripts/download_data.py
```

Run the full pipeline:

```bash
python scripts/run_analysis.py
```

To pick specific subjects:

```bash
python scripts/run_analysis.py --subjects 0 1 2 3 4
```

Outputs land in `results/` (CSVs) and `figures/` (PNGs).

## Pipeline

1. Load Sleep-EDF PSG and hypnogram for each subject (MNE-Python).
2. Bandpass filter 0.3–40 Hz.
3. Epoch into 30-second chunks aligned to sleep stage labels (AASM: stages 3+4 → N3).
4. Keep only N2, N3, REM epochs; drop Wake and N1.
5. Compute band power per epoch and channel using Welch's method:
   - delta 1–4 Hz, theta 4–8 Hz, alpha 8–12 Hz, beta 15–25 Hz, gamma 25–40 Hz
6. Average per subject × stage × channel × band.
7. Compute log posterior − log frontal contrast (the "hot zone" signature).
8. Paired t-tests across subjects: REM vs NREM (N2+N3 average) per band.
9. Plot mean spectra, band-power boxplots, and contrast bars.
