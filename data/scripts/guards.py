#!/usr/bin/env python3
"""Checks that answer the most likely reviewer objections (register Z10-Z13).
A. Was 2026 simply wetter or drier at Rangamati? Same point, same products, uncorrected.
B. Does the 2017 lead time need hourly data? Trailing 24-h totals as a gauge read every 3, 6 or
   24 hours (at 06:00) would have reported them, on the gauge-anchored series.
C. Is the empirical threshold's alarm burden a reanalysis artefact? Days per season on which the
   two GHCN gauges' own daily totals exceed each threshold, beside the reanalysis at those points.
D. Do the thresholds fail only outside their home district? Detection and alarm days in Cox's
   Bazar alone, where the empirical threshold was derived.
Writes data/results/guards.json."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rain_analysis as ra, climatology as cl, bias_qm as qm, skill as sk


def stats(s):
    return {"max24h": round(float(s.rolling(24).sum().max()), 1),
            "max72h": round(float(s.rolling(72).sum().max()), 1), "event_total": round(float(s.sum()), 1)}


def imerg2026(lat, lon):
    da = xr.open_dataset(ra.ROOT / "imerg" / "imerg_hh_2026-07_cht.nc")["precipitation"]
    s = da.sel(lat=lat, lon=lon, method="nearest").to_series() * 0.5
    s.index = pd.DatetimeIndex([pd.Timestamp(str(x)) for x in s.index]).floor("h") + ra.LOCAL + pd.Timedelta(hours=1)
    return s.groupby(level=0).sum()


def main():
    hourly = cl.load_hourly()
    out = {}
    # ---- A
    e = cl.point_series(hourly, *ra.RANGAMATI)
    e17, e26 = e.loc["2017-06-10":"2017-06-15 23:00"], e.loc["2026-07-03":"2026-07-12 23:00"]
    i17 = ra.imerg_hourly_point(*ra.RANGAMATI).loc["2017-06-10":"2017-06-14 12:00"]
    i26 = imerg2026(*ra.RANGAMATI).loc["2026-07-03":"2026-07-10 23:00"]
    out["A_rangamati_forcing_raw"] = {"era5land": {"2017": stats(e17), "2026": stats(e26)},
                                      "imerg": {"2017": stats(i17), "2026 (to 10 Jul)": stats(i26)}}
    # ---- B
    B = {}
    for name, raw in [("era5land", e17), ("imerg", i17)]:
        k = 343.0 / raw.rolling(24).sum().max(); c = raw * k; r24 = c.rolling(24).sum()
        row = {"factor": round(float(k), 2),
               "24h_to_12Jun_0600": round(float(r24.loc["2017-06-12 06:00"]), 0),
               "24h_to_13Jun_0600": round(float(r24.loc["2017-06-13 06:00"]), 0)}
        for h in (3, 6):
            rep = r24[r24.index.hour % h == 0]
            row[f"{h}h_reports_first_57.4"] = str(rep[rep >= 57.4].index.min())[:16]
            row[f"{h}h_reports_first_200"] = str(rep[rep >= 200].index.min())[:16]
        B[name] = row
    out["B_reading_interval_2017"] = B
    # ---- C
    tq = pd.read_csv(sk.RES / "qm_transfer.csv"); x, y = tq.era5land_mm.values, tq.gauge_mm.values
    C = {}
    for sid, (name, la, lo) in qm.GHCN.items():
        g = qm.ghcn(sid); yrs = sorted(set(int(v) for v in g.index.year)); per = g.groupby(g.index.year)
        row = {"seasons": yrs, "gauge_daily_days_ge_57.4": round(float(per.apply(lambda v: (v >= 57.4).sum()).mean()), 1),
               "gauge_daily_days_ge_200": round(float(per.apply(lambda v: (v >= 200).sum()).mean()), 2)}
        s = cl.point_series(hourly, la, lo)
        for mode in ("qm", "flat"):
            cs = sk.corrected(s, x, y, mode)
            dd = cs.shift(-6, freq="h").resample("D").sum(); dd = dd[dd.index.year.isin(yrs)]
            r = cs.rolling(24, min_periods=24).sum(); r = r[r.index.year.isin(yrs)]
            for thr in (57.4, 200):
                row[f"{mode}_daily_days_ge_{thr}"] = round(float((dd >= thr).groupby(dd.index.year).sum().mean()), 1)
                d = (r >= thr).groupby(r.index.normalize()).any()
                row[f"{mode}_rolling24_days_ge_{thr}"] = round(float(d.groupby(d.index.year).sum().mean()), 1)
        C[name] = row
    out["C_gauge_alarm_days"] = C
    # ---- D
    inv = sk.load_inventory(); cent = inv.groupby("District")[["lat", "lon"]].mean()
    dated = inv.dropna(subset=["D"])
    ev = dated[dated.D.dt.month.between(5, 10)].groupby(["District", "D"]).size().reset_index(name="n")
    extra = pd.DataFrame([{"District": a, "D": pd.Timestamp(b)} for a, b in sk.SITREP])
    cx = pd.concat([ev[["District", "D"]], extra]); cx = cx[cx.District == "Cox's Bazar"]
    s = cl.point_series(hourly, *cent.loc["Cox's Bazar"]); D = {"n_events": int(len(cx))}
    for mode in ("qm", "flat"):
        r = sk.corrected(s, x, y, mode).rolling(24, min_periods=24).sum()
        r2 = r[(r.index.year >= 1979) & (r.index.year <= 2025)]
        for thr in (57.4, 200):
            hits = [bool((r.loc[e.D - pd.Timedelta(days=1): e.D + pd.Timedelta(hours=23)] >= thr).any()) for _, e in cx.iterrows()]
            d = (r2 >= thr).groupby(r2.index.normalize()).any()
            D[f"{mode}_{thr}"] = {"pod": round(float(np.mean(hits)), 2),
                                  "alarm_days": round(float(d.groupby(d.index.year).sum().mean()), 1)}
    out["D_coxs_bazar_only"] = D
    (sk.RES / "guards.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
