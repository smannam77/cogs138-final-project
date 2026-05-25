"""Download Sleep-EDF Expanded recordings for the chosen subjects.

Usage:
    python scripts/download_data.py
    python scripts/download_data.py --subjects 0 1 2 3 --path data/raw
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import download_sleep_edf  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--subjects",
        type=int,
        nargs="+",
        default=list(range(20)),
        help="Subject indices (0–82 for Sleep Cassette). Default: 0–19.",
    )
    parser.add_argument(
        "--recording",
        type=int,
        nargs="+",
        default=[1],
        help="Recording nights to fetch (1 and/or 2). Default: [1].",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("data/raw"),
        help="Where to cache the downloaded files.",
    )
    args = parser.parse_args()

    args.path.mkdir(parents=True, exist_ok=True)
    pairs = download_sleep_edf(
        subjects=args.subjects,
        recording=args.recording,
        path=args.path,
    )
    print(f"Downloaded {len(pairs)} recording(s) to {args.path}")
    for psg, hyp in pairs:
        print(f"  PSG: {psg}\n  HYP: {hyp}")


if __name__ == "__main__":
    main()
