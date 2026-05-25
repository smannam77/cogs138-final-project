"""Filtering, epoching, and stage/channel selection."""
from __future__ import annotations

from typing import Iterable, Sequence

import mne


EVENT_ID = {
    "W": 1,
    "N1": 2,
    "N2": 3,
    "N3": 4,
    "REM": 5,
}

EPOCH_DURATION = 30.0
DEFAULT_CHANNELS = ("EEG Fpz-Cz", "EEG Pz-Oz")
DEFAULT_STAGES = ("N2", "N3", "REM")


def filter_raw(
    raw: mne.io.BaseRaw,
    l_freq: float = 0.3,
    h_freq: float = 40.0,
) -> mne.io.BaseRaw:
    raw.load_data()
    raw.filter(l_freq=l_freq, h_freq=h_freq, fir_design="firwin", verbose=False)
    return raw


def make_epochs(raw: mne.io.BaseRaw) -> mne.Epochs:
    """Build 30-second epochs from hypnogram annotations.

    Expects annotation descriptions to already be AASM-style ('W', 'N1', ...) — i.e.
    `load_raw_with_annotations` has been called.
    """
    descriptions_present = set(raw.annotations.description)
    event_id = {k: v for k, v in EVENT_ID.items() if k in descriptions_present}
    if not event_id:
        raise ValueError(
            "No sleep-stage annotations matched expected labels: "
            f"{sorted(descriptions_present)}"
        )
    events, event_id_map = mne.events_from_annotations(
        raw,
        event_id=event_id,
        chunk_duration=EPOCH_DURATION,
        verbose=False,
    )
    tmax = EPOCH_DURATION - 1.0 / raw.info["sfreq"]
    epochs = mne.Epochs(
        raw,
        events,
        event_id=event_id_map,
        tmin=0.0,
        tmax=tmax,
        baseline=None,
        preload=True,
        verbose=False,
    )
    return epochs


def select_channels(
    epochs: mne.Epochs,
    channels: Sequence[str] = DEFAULT_CHANNELS,
) -> mne.Epochs:
    return epochs.copy().pick(list(channels))


def keep_sleep_stages(
    epochs: mne.Epochs,
    stages: Iterable[str] = DEFAULT_STAGES,
) -> mne.Epochs:
    present = [s for s in stages if s in epochs.event_id]
    if not present:
        raise ValueError(
            f"None of {list(stages)} present in epochs.event_id={list(epochs.event_id)}"
        )
    return epochs[present]
