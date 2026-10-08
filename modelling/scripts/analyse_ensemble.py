#!/usr/bin/env python3
"""Summarise the TRIGRS ensemble for Rangamati, June 2017.

A run is admissible when the landscape starts stable (under 5 % of hill cells below FS 1 one
hour into the run). Among admissible runs the summary asks four things: how many trigger any
failure cell inside the 02:30-11:00 window of 13 June; when failure cells first fall below FS 1
relative to that window; which parameters set that timing (Spearman rank correlation); and how
much hillslope fails alongside the failure cells (the false-alarm burden). Spatial skill is
reported against the slope-only ceiling, since with uniform parameters FS ranks cells by slope.
Writes modelling/results/ensemble_<seed>_summary.json."""
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[2]; RES = ROOT / "modelling" / "results"
FAIL0 = pd.Timestamp("2017-06-13 02:30")
PARAMS = ["c", "phi", "uws", "Ks", "D0_Ks", "zmax", "dwt_f", "rizero"]


def main(seed):
    d = pd.read_csv(RES / f"ensemble_{seed}.csv")
    err = int(d["error"].notna().sum()) if "error" in d else 0
    d = d[d.get("error").isna()] if "error" in d else d
    d = d.assign(med_first=pd.to_datetime(d.median_first_fs_lt1))
    d["lead_h"] = (FAIL0 - d.med_first).dt.total_seconds() / 3600
    adm = d[d.share_hill_fs_lt1_prestorm < 0.05]
    out = {"runs": int(len(d)) + err, "errors": err, "admissible": int(len(adm)),
           "admissible_by_product": adm["product"].value_counts().to_dict()}
    trig = adm[adm.share_fail_cells_fs_lt1_final > adm.share_fail_fs_lt1_prestorm]
    out["runs_triggering_any_failure_cell"] = int(len(trig))
    out["runs_any_in_window"] = int((adm.share_fail_triggered_in_window > 0).sum())
    out["runs_majority_of_triggered_in_window"] = int(
        (adm.share_fail_triggered_in_window > adm.share_fail_triggered_before_window).sum())
    if len(trig):
        out["lead_h_of_median_first_failure_pct10_50_90"] = [round(float(np.nanpercentile(trig.lead_h, q)), 1) for q in (10, 50, 90)]
        out["share_fail_cells_failing_pct10_50_90"] = [round(float(np.percentile(trig.share_fail_cells_fs_lt1_final, q)), 3) for q in (10, 50, 90)]
        out["share_hill_cells_failing_pct10_50_90"] = [round(float(np.percentile(trig.share_hill_cells_fs_lt1_final, q)), 3) for q in (10, 50, 90)]
        out["auc_pct10_50_90"] = [round(float(np.percentile(trig.auc_final_fs, q)), 3) for q in (10, 50, 90)]
        out["spearman_lead_h"] = {p: round(float(spearmanr(trig[p], trig.lead_h, nan_policy="omit")[0]), 2) for p in PARAMS}
        out["spearman_share_fail"] = {p: round(float(spearmanr(trig[p], trig.share_fail_cells_fs_lt1_final)[0]), 2) for p in PARAMS}
        lab = trig[trig.c >= 3.7]
        out["lab_cohesion_runs_triggering"] = int(len(lab))
        out["lab_cohesion_share_fail_cells_failing_max"] = round(float(lab.share_fail_cells_fs_lt1_final.max()), 3) if len(lab) else None
    win = adm[adm.share_fail_triggered_in_window > 0]
    out["param_medians_admissible"] = {k: float(f"{adm[k].median():.3g}") for k in PARAMS}
    out["param_medians_any_in_window"] = {k: float(f"{win[k].median():.3g}") for k in PARAMS} if len(win) else None
    out["in_window_share_of_fail_cells_pct50_90"] = ([round(float(np.percentile(win.share_fail_triggered_in_window, q)), 3)
                                                      for q in (50, 90)] if len(win) else None)
    (RES / f"ensemble_{seed}_summary.json").write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--seed", type=int, default=2017)
    main(a.parse_args().seed)
