"""Spectral features: Welch PSD, band power, and the posterior−frontal contrast."""
from __future__ import annotations

from typing import Dict, Mapping, Tuple

import mne
import numpy as np
import pandas as pd
from scipy import signal


BANDS: Dict[str, Tuple[float, float]] = {
    "delta": (1.0, 4.0),
    "theta": (4.0, 8.0),
    "alpha": (8.0, 12.0),
    "beta": (15.0, 25.0),
    "gamma": (25.0, 40.0),
}


def welch_psd(
    data: np.ndarray,
    sfreq: float,
    n_per_seg: int | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Welch PSD along the last axis.

    `data` shape can be (..., n_times). Returns (freqs, psd) with psd shape
    matching data minus the time axis plus a frequency axis.
    """
    if n_per_seg is None:
        n_per_seg = int(4 * sfreq)
        n_per_seg = min(n_per_seg, data.shape[-1])
    freqs, psd = signal.welch(data, fs=sfreq, nperseg=n_per_seg, axis=-1)
    return freqs, psd


def band_power(
    freqs: np.ndarray,
    psd: np.ndarray,
    fmin: float,
    fmax: float,
) -> np.ndarray:
    """Integrate PSD between fmin and fmax (inclusive) along the frequency axis."""
    mask = (freqs >= fmin) & (freqs <= fmax)
    return np.trapz(psd[..., mask], freqs[mask], axis=-1)


def compute_band_powers(
    epochs: mne.Epochs,
    bands: Mapping[str, Tuple[float, float]] = BANDS,
) -> pd.DataFrame:
    """Long-form DataFrame of band power per (epoch, channel, band).

    Columns: epoch, stage, channel, band, power.
    """
    sfreq = epochs.info["sfreq"]
    data = epochs.get_data(copy=False)  # (n_epochs, n_channels, n_times)
    freqs, psd = welch_psd(data, sfreq)

    ch_names = epochs.ch_names
    inv_event_id = {v: k for k, v in epochs.event_id.items()}
    stages = [inv_event_id[ev] for ev in epochs.events[:, 2]]

    rows = []
    for band_name, (fmin, fmax) in bands.items():
        bp = band_power(freqs, psd, fmin, fmax)  # (n_epochs, n_channels)
        for i, stage in enumerate(stages):
            for j, ch in enumerate(ch_names):
                rows.append(
                    {
                        "epoch": i,
                        "stage": stage,
                        "channel": ch,
                        "band": band_name,
                        "power": float(bp[i, j]),
                    }
                )
    return pd.DataFrame(rows)


def aggregate_subject(df: pd.DataFrame, subject_id: int) -> pd.DataFrame:
    """Average band powers within each (stage, channel, band) for one subject."""
    agg = (
        df.groupby(["stage", "channel", "band"], as_index=False)["power"].mean()
    )
    agg["subject"] = subject_id
    return agg[["subject", "stage", "channel", "band", "power"]]


def posterior_frontal_contrast(
    subject_df: pd.DataFrame,
    posterior_ch: str = "EEG Pz-Oz",
    frontal_ch: str = "EEG Fpz-Cz",
) -> pd.DataFrame:
    """log10(posterior power) − log10(frontal power) per (subject, stage, band).

    The log transform stabilizes variance and makes the contrast interpretable
    as a ratio in dB-like units.
    """
    posterior = subject_df[subject_df["channel"] == posterior_ch]
    frontal = subject_df[subject_df["channel"] == frontal_ch]
    merged = posterior.merge(
        frontal,
        on=["subject", "stage", "band"],
        suffixes=("_post", "_front"),
    )
    merged["contrast"] = np.log10(merged["power_post"]) - np.log10(
        merged["power_front"]
    )
    return merged[["subject", "stage", "band", "contrast"]]


def mean_spectra_by_stage(
    epochs: mne.Epochs,
) -> Tuple[Dict[str, np.ndarray], np.ndarray, list[str]]:
    """Mean PSD per stage for one subject.

    Returns ({stage: psd shape (n_channels, n_freqs)}, freqs, channel_names).
    """
    sfreq = epochs.info["sfreq"]
    data = epochs.get_data(copy=False)
    freqs, psd = welch_psd(data, sfreq)  # (n_epochs, n_channels, n_freqs)
    inv_event_id = {v: k for k, v in epochs.event_id.items()}
    stages = np.array([inv_event_id[ev] for ev in epochs.events[:, 2]])
    out = {stage: psd[stages == stage].mean(axis=0) for stage in np.unique(stages)}
    return out, freqs, epochs.ch_names
