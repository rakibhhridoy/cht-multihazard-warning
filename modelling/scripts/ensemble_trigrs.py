#!/usr/bin/env python3
"""Latin-hypercube ensemble of TRIGRS runs for Rangamati, June 2017 (lookup mode).

Strength ranges are the laboratory values for Rangamati hill soils of Santo et al. (2024), with
cohesion extended down to zero so that the ensemble shows how much cohesion the 30 m slopes can
carry. Hydraulic properties, depth and initial water table have no local measurement and span
the ranges commonly used for residual soils in TRIGRS studies. Each parameter set is run with both
gauge-anchored forcings. Results go to modelling/results/ensemble_<seed>.csv, one row per run."""
import argparse, json, shutil
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import qmc
import run_trigrs as rt

RANGES = {                      # name: (low, high, log-scale?)
    "c":      (0.0, 11.8, False),     # kPa; lab 3.7-11.8 (Santo et al. 2024), extended to 0
    "phi":    (27.8, 38.2, False),    # deg, lab range
    "uws":    (15.7, 21.2, False),    # kN/m3, lab saturated unit weight range
    "Ks":     (1e-7, 1e-4, True),     # m/s
    "D0_Ks":  (10.0, 500.0, True),    # diffusivity / Ks ratio
    "zmax":   (1.0, 4.0, False),      # m
    "dwt_f":  (0.5, 1.0, False),      # initial water-table depth as a fraction of zmax
    "rizero": (1e-9, 1e-7, True),     # m/s
}


def sample(n, seed):
    u = qmc.LatinHypercube(d=len(RANGES), seed=seed).random(n)
    rows = []
    for x in u:
        p = {}
        for (k, (lo, hi, lg)), v in zip(RANGES.items(), x):
            p[k] = float(10 ** (np.log10(lo) + v * (np.log10(hi) - np.log10(lo)))) if lg else float(lo + v * (hi - lo))
        rows.append(p)
    return rows


def one(args):
    i, q, product = args
    p = {"c": q["c"], "phi": q["phi"], "uws": q["uws"], "Ks": q["Ks"], "D0": q["Ks"] * q["D0_Ks"],
         "zmax": q["zmax"], "dwt": q["zmax"] * q["dwt_f"], "rizero": q["rizero"]}
    tag = f"ens/{product}_{i:04d}"
    try:
        r = rt.run(p, product, tag)
    except Exception as e:                                            # keep going; record the failure
        return {"i": i, "product": product, **q, "error": str(e)[:200]}
    shutil.rmtree(rt.RES / tag / "out", ignore_errors=True)
    for f in ("zones.asc", "zmax.asc", "depthwt.asc", "rizero.asc", "slope_lut.asc", "dem_lut.asc"):
        (rt.RES / tag / f).unlink(missing_ok=True)
    keep = {k: v for k, v in r.items() if k not in ("timeline", "params", "tag", "grid")}
    return {"i": i, **q, **keep}


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("--n", type=int, default=400)
    a.add_argument("--seed", type=int, default=2017); a.add_argument("--workers", type=int, default=4)
    a.add_argument("--workdir", default=None, help="folder for per-run TRIGRS files (default: results/trigrs)")
    v = a.parse_args()
    if v.workdir:                     # workers are spawned afresh on macOS, so pass it by environment
        import os
        os.environ["TRIGRS_WORKDIR"] = v.workdir; rt.RES = Path(v.workdir)
    params = sample(v.n, v.seed)
    jobs = [(i, q, prod) for i, q in enumerate(params) for prod in ("era5land", "imerg")]
    out = rt.ROOT / "modelling" / "results" / f"ensemble_{v.seed}.csv"
    rows = []
    with ProcessPoolExecutor(max_workers=v.workers) as ex:
        for k, r in enumerate(ex.map(one, jobs, chunksize=4)):
            rows.append(r)
            if (k + 1) % 50 == 0 or k + 1 == len(jobs):
                pd.DataFrame(rows).to_csv(out, index=False); print(f"{k+1}/{len(jobs)} runs", flush=True)
    (rt.ROOT / "modelling" / "results" / f"ensemble_{v.seed}_ranges.json").write_text(json.dumps(RANGES, indent=1))
