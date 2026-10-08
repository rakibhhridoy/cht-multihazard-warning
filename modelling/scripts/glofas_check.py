#!/usr/bin/env python3
"""Independent check on the flood model: GloFAS v5.0 daily discharge of the Sangu at Bandarban.

GloFAS shares none of the LISFLOOD-FP inputs (ERA5 runoff instead of IMERG, 0.05 deg river network
instead of the 90 m DEM, no station anchor). Two tests against the FFWC record (peaks on 13 Jun
2017, 7 Aug 2023, 8 Jul 2026; +135, +283, +96 cm over danger level):
1. timing: the GloFAS peak day in each storm window against the observed peak day;
2. rank: whether peak discharge orders the storms 2023 > 2017 > 2026, and where each storm sits
   among the June-September maxima of 2001-2025.
The Sangu cell is the river-network cell nearest the FFWC Bandarban station (92.218 E, 22.195 N) on
the chain of high-discharge cells that crosses the extraction box. Daily values are 00-24 UTC means
(06:00 BST to 06:00 BST next day). Writes modelling/results/glofas_check.json and glofas_sangu.csv."""
import glob, json
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr

ROOT = Path(__file__).resolve().parents[2]
CELL = (22.175, 92.225)                       # lat, lon of the Sangu cell beside the station
EVENTS = {"2017": ("2017-06-08", "2017-06-20", "2017-06-13", 135),
          "2023": ("2023-08-01", "2023-08-14", "2023-08-07", 283),
          "2026": ("2026-07-02", "2026-07-14", "2026-07-08", 96)}


def series():
    out = []
    for f in sorted(glob.glob(str(ROOT / "data" / "glofas" / "glofas_*.nc"))):
        ds = xr.open_dataset(f)
        s = ds.avg_dis.sel(latitude=CELL[0], longitude=CELL[1], method="nearest").to_series()
        out.append(s)
    s = pd.concat(out).sort_index(); s.index = pd.DatetimeIndex(s.index).normalize()
    return s[~s.index.duplicated()]


def main():
    s = series(); s.rename("q_m3s").to_csv(ROOT / "modelling" / "results" / "glofas_sangu.csv")
    ann = s[s.index.year <= 2025].groupby(s.index.year[s.index.year <= 2025]).max()
    res = {"cell": CELL, "years": [int(s.index.year.min()), int(s.index.year.max())],
           "jjas_mean_m3s": round(float(s.mean()), 1), "annual_max_median_m3s": round(float(ann.median()), 1)}
    for ev, (a, b, obs, cm) in EVENTS.items():
        w = s.loc[a:b]
        if w.empty:
            res[ev] = None; continue
        pk = w.idxmax()
        res[ev] = {"obs_peak_day": obs, "obs_cm_over_dl": cm, "glofas_peak_day": str(pk.date()),
                   "offset_d": int((pk - pd.Timestamp(obs)).days), "peak_m3s": round(float(w.max())),
                   "rank_among_2001_2025_maxima": int((ann > w.max()).sum()) + 1, "of": int(len(ann)),
                   "window": {str(k.date()): round(float(v)) for k, v in w.items()}}
    ok = [e for e in EVENTS if res.get(e)]
    res["rank_by_peak"] = sorted(ok, key=lambda e: -res[e]["peak_m3s"])
    res["rank_matches_obs"] = res["rank_by_peak"] == ["2023", "2017", "2026"]
    (ROOT / "modelling" / "results" / "glofas_check.json").write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
