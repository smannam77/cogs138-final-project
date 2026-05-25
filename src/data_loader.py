"""Sleep-EDF Expanded data loading.

Wraps `mne.datasets.sleep_physionet.age.fetch_data` and applies hypnogram
annotations to the PSG recording so that downstream code can epoch on
sleep-stage labels.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import mne
from mne.datasets.sleep_physionet.age import fetch_data


SLEEP_STAGE_MAP = {
    "Sleep stage W": "W",
    "Sleep stage 1": "N1",
    "Sleep stage 2": "N2",
    "Sleep stage 3": "N3",
    "Sleep stage 4": "N3",
    "Sleep stage R": "REM",
    "Sleep stage ?": "UNK",
    "Movement time": "MVT",
}


def download_sleep_edf(
    subjects: List[int],
    recording: int | List[int] = 1,
    path: Optional[str | Path] = None,
) -> List[Tuple[str, str]]:
    """Fetch Sleep-EDF Expanded recordings.

    Returns a list of (psg_path, hypnogram_path) tuples — one per (subject, night).
    """
    recording_list = [recording] if isinstance(recording, int) else list(recording)
    path_str = str(path) if path is not None else None
    pairs = fetch_data(
        subjects=subjects,
        recording=recording_list,
        path=path_str,
        on_missing="warn",
    )
    return [tuple(p) for p in pairs]


def load_raw_with_annotations(psg_path: str | Path, hyp_path: str | Path) -> mne.io.BaseRaw:
    """Load a PSG EDF and attach hypnogram annotations renamed to AASM-style labels."""
    raw = mne.io.read_raw_edf(str(psg_path), preload=False, verbose=False)
    annotations = mne.read_annotations(str(hyp_path))
    descriptions = [SLEEP_STAGE_MAP.get(d, d) for d in annotations.description]
    raw.set_annotations(
        mne.Annotations(
            onset=annotations.onset,
            duration=annotations.duration,
            description=descriptions,
            orig_time=annotations.orig_time,
        ),
        emit_warning=False,
    )
    return raw
