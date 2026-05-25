"""Figures: spectra, band-power boxplots, and the contrast bar plot."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


STAGE_ORDER = ["W", "N1", "N2", "N3", "REM"]
BAND_ORDER = ["delta", "theta", "alpha", "beta", "gamma"]


def plot_spectra(
    spectra: Dict[str, np.ndarray],
    freqs: np.ndarray,
    channels: Sequence[str],
    stages: Iterable[str] = ("N2", "N3", "REM"),
    fmax: float = 40.0,
    save_path: str | Path | None = None,
):
    """Plot mean PSD per stage for each channel side-by-side.

    `spectra` maps stage -> array of shape (n_channels, n_freqs).
    """
    stages_present = [s for s in stages if s in spectra]
    fig, axes = plt.subplots(1, len(channels), figsize=(5 * len(channels), 4), sharey=True)
    if len(channels) == 1:
        axes = [axes]
    for ax, ch_idx, ch in zip(axes, range(len(channels)), channels):
        for stage in stages_present:
            ax.semilogy(freqs, spectra[stage][ch_idx], label=stage)
        ax.set_xlim(0, fmax)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_title(ch)
        ax.legend()
    axes[0].set_ylabel("PSD (µV²/Hz)")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig


def plot_bandpower_boxes(
    subject_df: pd.DataFrame,
    save_path: str | Path | None = None,
):
    """Boxplot of per-subject mean band power, faceted by channel."""
    stages = [s for s in STAGE_ORDER if s in subject_df["stage"].unique()]
    bands = [b for b in BAND_ORDER if b in subject_df["band"].unique()]
    g = sns.catplot(
        data=subject_df,
        x="band",
        y="power",
        hue="stage",
        col="channel",
        order=bands,
        hue_order=stages,
        kind="box",
        sharey=False,
        height=4,
        aspect=1.2,
    )
    g.set_axis_labels("Frequency band", "Power (µV²)")
    g.set_titles("{col_name}")
    for ax in g.axes.flat:
        ax.set_yscale("log")
    if save_path:
        g.savefig(save_path, dpi=150, bbox_inches="tight")
    return g


def plot_contrast_bars(
    contrast_df: pd.DataFrame,
    bands: Sequence[str] = ("delta", "gamma"),
    save_path: str | Path | None = None,
):
    """Bar plot of log posterior − log frontal contrast per stage, for selected bands."""
    sub = contrast_df[contrast_df["band"].isin(bands)]
    stages = [s for s in STAGE_ORDER if s in sub["stage"].unique()]
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.barplot(
        data=sub,
        x="band",
        y="contrast",
        hue="stage",
        order=list(bands),
        hue_order=stages,
        errorbar="se",
        ax=ax,
    )
    ax.axhline(0, color="k", linewidth=0.7)
    ax.set_ylabel("log10(posterior) − log10(frontal)")
    ax.set_xlabel("Band")
    ax.set_title("Posterior−frontal contrast by stage")
    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150, bbox_inches="tight")
    return fig
