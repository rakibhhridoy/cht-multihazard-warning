#!/usr/bin/env python3
"""Empirical quantile mapping of ERA5-Land daily rainfall onto gauge rainfall, as an alternative to
the single-event factor. Calibrated on the two GHCN-Daily gauges near the hills (Chattogram
airport, BGM00041978; Cox's Bazar, BGM00041992), May-October, using only seasons with at least
170 reported days (GHCN omits days for which no report reached it, and near-complete seasons keep
that omission from biasing the distribution). Validated out of sample on the ten BMD 24-hour
totals of July 2026 (event2026.GAUGE_2026), which postdate the GHCN record used here.
Writes data/results/bias_qm.json and data/results/qm_transfer.csv."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import climatology as cl
import event2026 as ev

ROOT = cl.ROOT; RES = cl.RES
GHCN = {"BGM00041978": ("Chattogram airport", 22.250, 91.813), "BGM00041992": ("Cox's Bazar", 21.452, 91.964)}
MIN_DAYS = 170
QS = np.r_[np.linspace(0, 0.95, 96), np.linspace(0.951, 0.999, 49)]


def ghcn(sid):
    d = pd.read_csv(ROOT / "ghcnd" / f"{sid}.csv.gz", header=None,
                    names=["id", "date", "el", "v", "m", "q", "src", "t"])
    p = d[(d.el == "PRCP") & d.q.isna()].copy()
    p.index = pd.to_datetime(p.date.astype(str)); p = p.v / 10.0
    p = p[p.index.month.isin(range(5, 11))]
    n = p.groupby(p.index.year).size()
    return p[p.index.year.isin(n[n >= MIN_DAYS].index)]


def transfer(era_daily, gauge_daily):
    """Quantile pairs (ERA5-Land -> gauge) on wet days, with a linear tail beyond the top pair."""
    x = np.quantile(era_daily, QS); y = np.quantile(gauge_daily, QS)
    x = np.maximum.accumulate(x); y = np.maximum.accumulate(y)
    return x, y


def apply(v, x, y):
    v = np.asarray(v, float)
    out = np.interp(v, x, y)
    top = v > x[-1]
    out[top] = y[-1] * v[top] / x[-1]          # constant ratio above the calibrated range
    return out


def main():
    hourly = cl.load_hourly()
    pairs_era, pairs_g, meta = [], [], {}
    for sid, (name, la, lo) in GHCN.items():
        g = ghcn(sid)
        e = cl.point_series(hourly, la, lo)                     # BST
        # GHCN SYNOP day is taken as the UTC day (06:00-06:00 BST); only the distribution is used
        ed = e.shift(-6, freq="h").resample("D").sum()
        common = ed.index.intersection(g.index)
        pairs_era.append(ed.loc[common].values); pairs_g.append(g.loc[common].values)
        meta[name] = {"seasons": sorted(set(int(y) for y in common.year)), "days": int(len(common)),
                      "gauge_mean_mm": round(float(g.loc[common].mean()), 2),
                      "era5land_mean_mm": round(float(ed.loc[common].mean()), 2),
                      "gauge_p99_mm": round(float(np.quantile(g.loc[common], 0.99)), 1),
                      "era5land_p99_mm": round(float(np.quantile(ed.loc[common], 0.99)), 1)}
    xe = np.concatenate(pairs_era); yg = np.concatenate(pairs_g)
    x, y = transfer(xe, yg)
    pd.DataFrame({"q": QS, "era5land_mm": x, "gauge_mm": y}).to_csv(RES / "qm_transfer.csv", index=False)

    # ---- out-of-sample check on July 2026 --------------------------------------------------
    import rain_analysis as ra
    _, h = ra.era5land_hourly()
    h = h.sel(valid_time=slice("2026-07-01", "2026-07-15"))
    val = []
    for st, end, gv in ev.GAUGE_2026:
        la, lo = ev.STATIONS[st]
        s = ra.point(h, la, lo, "valid_time")
        e = pd.Timestamp(end); raw = float(s.loc[e - pd.Timedelta(hours=23):e].sum())
        val.append({"station": st, "end_bst": end, "gauge": gv, "raw": round(raw, 1),
                    "x2.95": round(raw * 2.95, 1), "qm": round(float(apply([raw], x, y)[0]), 1)})
    df = pd.DataFrame(val)
    def score(col):
        err = df[col] - df.gauge
        return {"bias_mm": round(float(err.mean()), 1), "mae_mm": round(float(err.abs().mean()), 1),
                "median_ratio_to_gauge": round(float((df[col] / df.gauge).median()), 2)}
    res = {"calibration": meta, "calibration_days": int(len(xe)),
           "transfer_points_mm": {f"{v:.0f}": round(float(apply([v], x, y)[0]), 1) for v in [5, 20, 40, 60, 80, 100, 120]},
           "validation_2026": val, "score_raw": score("raw"), "score_x2.95": score("x2.95"), "score_qm": score("qm")}
    (RES / "bias_qm.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
