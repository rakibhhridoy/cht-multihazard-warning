#!/usr/bin/env python3
"""Re-run every admissible 2017 ensemble member with the July 2026 forcing (same product, same
parameters, same Rangamati domain) and compare the two storms. Admissible = under 5 % of hill cells
below FS 1 before the 2017 storm. Writes modelling/results/replay2026_<seed>.csv and _summary.json."""
import argparse, json, os, shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path(__file__).resolve().parents[2]; RES = ROOT / "modelling" / "results"


def one(row):
    import run_trigrs as rt
    p = {"c": row["c"], "phi": row["phi"], "uws": row["uws"], "Ks": row["Ks"], "D0": row["Ks"] * row["D0_Ks"],
         "zmax": row["zmax"], "dwt": row["zmax"] * row["dwt_f"], "rizero": row["rizero"]}
    tag = f"r26/{row['product']}_{int(row['i']):04d}"
    try:
        r = rt.run(p, row["product"], tag, event="2026")
    except Exception as e:                                            # record and continue
        return {"i": int(row["i"]), "product": row["product"], "r26_error": str(e)[:200]}
    shutil.rmtree(rt.RES / tag, ignore_errors=True)
    tl = r.pop("timeline"); [r.pop(k) for k in ("params", "tag", "grid")]
    r["hill_share_by"] = {t: v[1] for t, v in tl.items() if t.endswith(("00:00:00",))}
    return {"i": int(row["i"]), **{f"r26_{k}": v for k, v in r.items() if k != "product"}, "product": row["product"]}


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--seed", type=int, default=2017)
    a.add_argument("--workers", type=int, default=6); a.add_argument("--workdir", required=True)
    v = a.parse_args(); os.environ["TRIGRS_WORKDIR"] = v.workdir
    e = pd.read_csv(RES / f"ensemble_{v.seed}.csv"); adm = e[e.share_hill_fs_lt1_prestorm < 0.05]
    with ProcessPoolExecutor(max_workers=v.workers) as ex:
        rows = list(ex.map(one, [r for _, r in adm.iterrows()], chunksize=4))
    r = pd.DataFrame(rows)
    m = adm.merge(r.drop(columns=["r26_hill_share_by"], errors="ignore"), on=["i", "product"])
    if "r26_error" in m:
        print("errors:", int(m.r26_error.notna().sum())); m = m[m.r26_error.isna()]
    m.to_csv(RES / f"replay2026_{v.seed}.csv", index=False)
    pre26 = m.r26_share_hill_fs_lt1_prestorm < 0.05
    d = m[pre26]
    ratio = (d.r26_share_hill_cells_fs_lt1_final + 1e-4) / (d.share_hill_cells_fs_lt1_final + 1e-4)
    win = d[d.share_fail_triggered_in_window > 0]
    s = {"runs": int(len(m)), "admissible_both_years": int(len(d)),
         "hill_share_2017_pct10_50_90": [round(float(np.percentile(d.share_hill_cells_fs_lt1_final, q)), 3) for q in (10, 50, 90)],
         "hill_share_2026_pct10_50_90": [round(float(np.percentile(d.r26_share_hill_cells_fs_lt1_final, q)), 3) for q in (10, 50, 90)],
         "ratio_2026_to_2017_pct10_50_90": [round(float(np.percentile(ratio, q)), 2) for q in (10, 50, 90)],
         "runs_2026_more_unstable": int((d.r26_share_hill_cells_fs_lt1_final > d.share_hill_cells_fs_lt1_final + 0.005).sum()),
         "runs_2026_less_unstable": int((d.r26_share_hill_cells_fs_lt1_final < d.share_hill_cells_fs_lt1_final - 0.005).sum()),
         "runs_equal_within_0.5pp": int(((d.r26_share_hill_cells_fs_lt1_final - d.share_hill_cells_fs_lt1_final).abs() <= 0.005).sum()),
         "timing_fit_2017_runs": int(len(win)),
         "timing_fit_2017_hill_2017_vs_2026_median": [round(float(win.share_hill_cells_fs_lt1_final.median()), 3),
                                                      round(float(win.r26_share_hill_cells_fs_lt1_final.median()), 3)] if len(win) else None,
         "timing_fit_2017_median_first_2026": str(pd.to_datetime(win.r26_median_first_fs_lt1).median()) if len(win) else None}
    (RES / f"replay2026_{v.seed}_summary.json").write_text(json.dumps(s, indent=1)); print(json.dumps(s, indent=1))
