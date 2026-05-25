"""Group-level statistics on the posterior−frontal contrast."""
from __future__ import annotations

from typing import Iterable

import pandas as pd
from scipy import stats


def paired_ttest_rem_vs_nrem(
    contrast_df: pd.DataFrame,
    nrem_stages: Iterable[str] = ("N2", "N3"),
) -> pd.DataFrame:
    """Paired t-test of REM vs NREM contrast per band, across subjects.

    For each subject we collapse `nrem_stages` to a single per-subject mean,
    then pair with that subject's REM value. Subjects missing REM or any
    `nrem_stages` are dropped.

    Returns columns: band, n_subjects, mean_rem, mean_nrem, t, p.
    """
    nrem_set = set(nrem_stages)
    rem = contrast_df[contrast_df["stage"] == "REM"]
    nrem = contrast_df[contrast_df["stage"].isin(nrem_set)]
    nrem_avg = (
        nrem.groupby(["subject", "band"], as_index=False)["contrast"].mean()
    )

    results = []
    for band in sorted(contrast_df["band"].unique()):
        rem_band = rem[rem["band"] == band].set_index("subject")["contrast"]
        nrem_band = nrem_avg[nrem_avg["band"] == band].set_index("subject")["contrast"]
        common = rem_band.index.intersection(nrem_band.index)
        if len(common) < 2:
            results.append(
                {
                    "band": band,
                    "n_subjects": len(common),
                    "mean_rem": rem_band.loc[common].mean() if len(common) else float("nan"),
                    "mean_nrem": nrem_band.loc[common].mean() if len(common) else float("nan"),
                    "t": float("nan"),
                    "p": float("nan"),
                }
            )
            continue
        r = rem_band.loc[common].to_numpy()
        n = nrem_band.loc[common].to_numpy()
        t, p = stats.ttest_rel(r, n)
        results.append(
            {
                "band": band,
                "n_subjects": int(len(common)),
                "mean_rem": float(r.mean()),
                "mean_nrem": float(n.mean()),
                "t": float(t),
                "p": float(p),
            }
        )
    return pd.DataFrame(results)
