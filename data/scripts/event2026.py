#!/usr/bin/env python3
"""July 2026 replay. Two parts:
1. ERA5-Land against the BMD 24-hour gauge totals quoted in the BDRCS situation reports (the only
   gauge values published for the event), giving a second, independent estimate of the reanalysis
   bias after the single 2017 anchor.
2. The published thresholds replayed on the gauge-corrected series at Rangamati, the Ukhiya camps
   and Chattogram, set against the dated warnings and deaths.
Writes data/results/event2026.json. Local time = UTC+6 (BST)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rain_analysis as ra

RES = ra.RES
# BMD stations. Chattogram (Ambagan) and Cox's Bazar agree with GHCN/BMD positions to ~1 km;
# Rangamati, Bandarban and Kutubdia are town coordinates, so each ratio is also computed against
# the wettest and driest cell of the 3x3 neighbourhood to bound the position error.
STATIONS = {"Rangamati": (22.64, 92.20), "Bandarban": (22.20, 92.22), "Chattogram": (22.35, 91.82),
            "Cox's Bazar": (21.43, 91.93), "Kutubdia": (21.82, 91.85)}
# BMD 24-hour totals as reported (BDRCS SitReps 2-3; Daily Star for the 09:00 Bandarban value).
# End times are BST; BMD's 24-hour day ends at 06:00.
GAUGE_2026 = [("Chattogram", "2026-07-07 06:00", 283), ("Kutubdia", "2026-07-07 06:00", 195),
              ("Cox's Bazar", "2026-07-07 06:00", 129), ("Bandarban", "2026-07-07 06:00", 128),
              ("Rangamati", "2026-07-08 06:00", 287), ("Bandarban", "2026-07-08 09:00", 309),
              ("Chattogram", "2026-07-09 06:00", 329), ("Bandarban", "2026-07-09 06:00", 235),
              ("Rangamati", "2026-07-09 06:00", 130), ("Cox's Bazar", "2026-07-09 06:00", 125)]
# Replay points: the 2017 Rangamati cluster centroid, the fatal camps of Ukhiya (Camps 5, 7, 11
# and 15 lie within one 0.1-degree cell of this point) and Chattogram city.
POINTS = {"Rangamati": ra.RANGAMATI, "Ukhiya camps": (21.20, 92.155), "Chattogram": (22.35, 91.82)}
# Dated record (BST). Times given only as a day are placed at the start of that day, so that
# 'before' comparisons are conservative.
TIMELINE = {"forecast_and_activation": "2026-07-05 00:00",          # I4, day only
            "camp_deaths_6jul": "2026-07-06 00:00",                # I8, 'early hours'
            "bulletin_05": "2026-07-07 13:00",                     # I2
            "rangamati_287mm_window_end": "2026-07-08 06:00",      # I6
            "camp5_deaths": "2026-07-08 12:00",                    # L6, 'afternoon'
            "rangamati_upgrade_reported": "2026-07-09 00:00"}      # I6, SitRep 2 (9 Jul)
THRESH = [("empirical_24h_57.4", 24, 57.4), ("empirical_72h_130", 72, 130.0),
          ("installed_24h_200", 24, 200.0), ("installed_72h_350", 72, 350.0)]


def local(s):
    s = s.copy(); s.index = pd.DatetimeIndex(s.index) + ra.LOCAL
    return s


def neighbourhood(h, lat, lon):
    """Series of the nearest cell and its 3x3 neighbours with data (BST)."""
    iy = int(np.abs(h.latitude.values - lat).argmin()); ix = int(np.abs(h.longitude.values - lon).argmin())
    out = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            y, x = iy + dy, ix + dx
            if 0 <= y < h.sizes["latitude"] and 0 <= x < h.sizes["longitude"]:
                s = h.isel(latitude=y, longitude=x).to_series()
                if s.notna().sum() > 0:
                    out.append(local(s))
    return out


def first_cross(s, hours, thr, after):
    r = s.rolling(hours, min_periods=hours).sum()
    hit = r[(r.index >= after) & (r >= thr)]
    return None if hit.empty else hit.index[0]


def main():
    _, hourly = ra.era5land_hourly()
    h = hourly.sel(valid_time=slice("2026-07-01", "2026-07-15"))

    # ---- 1. gauge check -------------------------------------------------------------------
    rows = []
    for st, end, g in GAUGE_2026:
        la, lo = STATIONS[st]
        s = ra.point(h, la, lo, "valid_time"); off = ra.point.last_km
        e = pd.Timestamp(end); w = slice(e - pd.Timedelta(hours=23), e)
        v = float(s.loc[w].sum())
        nb = [float(x.loc[w].sum()) for x in neighbourhood(h, la, lo)]
        rows.append({"station": st, "end_bst": end, "gauge_mm": g, "era5land_mm": round(v, 1),
                     "ratio": round(g / v, 2), "ratio_range_3x3": [round(g / max(nb), 2), round(g / min(nb), 2)],
                     "cell_offset_km": round(off, 1)})
    ratios = np.array([r["ratio"] for r in rows])
    k26 = float(np.median(ratios))
    gauge = {"pairs": rows, "median_ratio": round(k26, 2),
             "iqr": [round(float(np.percentile(ratios, 25)), 2), round(float(np.percentile(ratios, 75)), 2)],
             "min_max": [round(float(ratios.min()), 2), round(float(ratios.max()), 2)],
             "ratio_2017_anchor": 2.95}

    # ---- 2. replay ------------------------------------------------------------------------
    after = pd.Timestamp("2026-07-03 00:00")
    replay = {}
    for name, (la, lo) in POINTS.items():
        s = ra.point(h, la, lo, "valid_time"); off = ra.point.last_km
        out = {"cell_offset_km": round(off, 1), "raw_max24h_mm": round(float(s.rolling(24).sum().max()), 1)}
        for label, k in [("raw", 1.0), ("k_min", gauge["min_max"][0]), ("k_median", k26), ("k_max", gauge["min_max"][1])]:
            cx = {}
            for tn, hrs, thr in THRESH:
                t = first_cross(s * k, hrs, thr, after)
                cx[tn] = None if t is None else str(t)[:16]
            out[label] = cx
        replay[name] = out

    # ---- 3. IMERG Late as a second product, where downloaded --------------------------------
    imerg = None
    f = ra.ROOT / "imerg" / "imerg_hh_2026-07_cht.nc"
    if f.exists():
        da = xr.open_dataset(f)["precipitation"]                      # mm/h per half hour, UTC start
        def ipoint(la, lo):
            s = da.sel(lat=la, lon=lo, method="nearest").to_series() * 0.5
            idx = pd.DatetimeIndex([pd.Timestamp(str(x)) for x in s.index])     # cftime -> pandas
            s.index = idx.floor("h") + ra.LOCAL + pd.Timedelta(hours=1)         # labelled at hour end, as ERA5-Land
            return s.groupby(level=0).sum()                          # hourly total, labelled at hour end
        irows = []
        for st, end, g in GAUGE_2026:
            s = ipoint(*STATIONS[st]); e = pd.Timestamp(end)
            v = float(s.loc[e - pd.Timedelta(hours=23):e].sum())
            irows.append({"station": st, "end_bst": end, "gauge_mm": g, "imerg_mm": round(v, 1), "ratio": round(g / v, 2)})
        ir = np.array([r["ratio"] for r in irows]); ki = float(np.median(ir))
        irep = {}
        for name, (la, lo) in POINTS.items():
            s = ipoint(la, lo)
            out = {"raw_max24h_mm": round(float(s.rolling(24).sum().max()), 1)}
            for label, k in [("raw", 1.0), ("k_min", float(ir.min())), ("k_median", ki), ("k_max", float(ir.max()))]:
                out[label] = {tn: (lambda t: None if t is None else str(t)[:16])(first_cross(s * k, hrs, thr, after))
                              for tn, hrs, thr in THRESH}
            irep[name] = out
        imerg = {"product": "IMERG V07 Late (GPM_3IMERGHHL)", "gauge_pairs": irows,
                 "median_ratio": round(ki, 2), "min_max": [round(float(ir.min()), 2), round(float(ir.max()), 2)],
                 "replay": irep}

    res = {"gauge_check": gauge, "replay": replay, "imerg": imerg, "timeline_bst": TIMELINE,
           "note": "ERA5-Land event file ends 14 Jul 2026 23:00 UTC. Corrected = raw x ratio."}
    (RES / "event2026.json").write_text(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
