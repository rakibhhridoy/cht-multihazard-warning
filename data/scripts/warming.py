#!/usr/bin/env python3
"""Warming sensitivity of the published thresholds. The corrected 1979-2025 series of skill.py are
scaled by the Clausius-Clapeyron rate of about 7 % per degree of warming (Trenberth et al. 2003;
Westra et al. 2014), and the number of days per season on which each fixed threshold fires, and its
detection of the dated events, are recomputed for 1, 2 and 3 degrees.

This is a sensitivity test, not a projection. Uniform scaling raises every hour by the same
fraction, whereas observed extremes can scale faster than the rate for short durations and slower
for long ones, and the 1950-2025 record shows no trend so far (climatology.py).
Writes data/results/warming.json."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import climatology as cl
import skill as sk

CC = 0.07
DT = [0, 1, 2, 3]
THRESH = [("empirical_24h_57.4", 24, 57.4), ("installed_24h_200", 24, 200.0)]


def main():
    hourly = cl.load_hourly()
    tq = pd.read_csv(sk.RES / "qm_transfer.csv"); x, y = tq.era5land_mm.values, tq.gauge_mm.values
    inv = sk.load_inventory()
    cent = inv.groupby("District")[["lat", "lon"]].mean()
    dated = inv.dropna(subset=["D"])
    ev = dated[dated.D.dt.month.between(5, 10)].groupby(["District", "D"]).size().reset_index(name="n")
    extra = pd.DataFrame([{"District": d, "D": pd.Timestamp(t)} for d, t in sk.SITREP])
    events = pd.concat([ev[["District", "D"]], extra], ignore_index=True)
    series = {d: cl.point_series(hourly, r.lat, r.lon) for d, r in cent.iterrows()}
    out = {"cc_rate_per_degree": CC, "results": {}}
    for mode in ("qm", "flat"):
        base = {d: sk.corrected(s, x, y, mode) for d, s in series.items()}
        res = {}
        for dt in DT:
            f = 1 + CC * dt
            roll = {d: (s * f).rolling(24, min_periods=24).sum() for d, s in base.items()}
            row = {}
            for tn, _, thr in THRESH:
                ad = []
                for d, r in roll.items():
                    r2 = r[(r.index.year >= 1979) & (r.index.year <= 2025)]
                    days = (r2 >= thr).groupby(r2.index.normalize()).any()
                    ad.append(float(days.groupby(days.index.year).sum().mean()))
                hits = []
                for _, e in events.iterrows():
                    w = roll[e.District].loc[e.D - pd.Timedelta(days=1): e.D + pd.Timedelta(hours=23)]
                    if len(w): hits.append(bool((w >= thr).any()))
                row[tn] = {"alarm_days_mean": round(float(np.mean(ad)), 1), "pod": round(float(np.mean(hits)), 2)}
            res[f"+{dt}C"] = row
        for tn, _, _ in THRESH:
            b = res["+0C"][tn]["alarm_days_mean"]
            for dt in DT[1:]:
                res[f"+{dt}C"][tn]["alarm_days_change_pct"] = round(100 * (res[f"+{dt}C"][tn]["alarm_days_mean"] / b - 1), 0)
        out["results"][mode] = res
    (sk.RES / "warming.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
