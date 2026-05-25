"""End-to-end analysis pipeline.

Loads each subject, filters, epochs, computes band power, aggregates,
computes the posterior−frontal contrast, runs paired t-tests, and writes
CSVs + figures.

Usage:
    python scripts/run_analysis.py
    python scripts/run_analysis.py --subjects 0 1 2 3 4
"""
from __future__ import annotations

import argparse
import sys
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd  # noqa: E402

from src.data_loader import download_sleep_edf, load_raw_with_annotations  # noqa: E402
from src.preprocessing import (  # noqa: E402
    filter_raw,
    keep_sleep_stages,
    make_epochs,
    select_channels,
)
from src.features import (  # noqa: E402
    aggregate_subject,
    compute_band_powers,
    posterior_frontal_contrast,
)
from src.stats import paired_ttest_rem_vs_nrem  # noqa: E402
from src.plots import plot_bandpower_boxes, plot_contrast_bars  # noqa: E402


def process_subject(subject_id: int, data_dir: Path) -> pd.DataFrame:
    pairs = download_sleep_edf([subject_id], recording=1, path=data_dir)
    psg, hyp = pairs[0]
    raw = load_raw_with_annotations(psg, hyp)
    filter_raw(raw)
    epochs = make_epochs(raw)
    epochs = select_channels(epochs)
    epochs = keep_sleep_stages(epochs)
    band_df = compute_band_powers(epochs)
    return aggregate_subject(band_df, subject_id)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subjects", type=int, nargs="+", default=list(range(20)))
    parser.add_argument("--data-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--results-dir", type=Path, default=Path("results"))
    parser.add_argument("--figures-dir", type=Path, default=Path("figures"))
    args = parser.parse_args()

    args.data_dir.mkdir(parents=True, exist_ok=True)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    args.figures_dir.mkdir(parents=True, exist_ok=True)

    per_subject = []
    for sid in args.subjects:
        print(f"[subject {sid}] processing...")
        try:
            per_subject.append(process_subject(sid, args.data_dir))
        except Exception:
            print(f"[subject {sid}] FAILED:")
            traceback.print_exc()
    if not per_subject:
        print("No subjects processed successfully; aborting.")
        return

    all_df = pd.concat(per_subject, ignore_index=True)
    all_df.to_csv(args.results_dir / "band_powers.csv", index=False)
    print(f"Wrote {args.results_dir / 'band_powers.csv'}")

    contrast = posterior_frontal_contrast(all_df)
    contrast.to_csv(args.results_dir / "contrast.csv", index=False)
    print(f"Wrote {args.results_dir / 'contrast.csv'}")

    test_results = paired_ttest_rem_vs_nrem(contrast)
    test_results.to_csv(args.results_dir / "rem_vs_nrem_ttests.csv", index=False)
    print(f"Wrote {args.results_dir / 'rem_vs_nrem_ttests.csv'}")
    print("\nPaired t-tests (REM vs NREM contrast):")
    print(test_results.to_string(index=False))

    plot_bandpower_boxes(all_df, save_path=args.figures_dir / "bandpower_boxes.png")
    plot_contrast_bars(contrast, save_path=args.figures_dir / "contrast_bars.png")
    print(f"\nWrote figures to {args.figures_dir}/")


if __name__ == "__main__":
    main()
