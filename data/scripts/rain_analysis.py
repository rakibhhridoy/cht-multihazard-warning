#!/usr/bin/env python3
"""Rainfall analysis for the three-storm manuscript, on ERA5-Land (CDS) and IMERG V07.
1. De-accumulate ERA5-Land total_precipitation to hourly mm, with a unit test.
2. June 2017: gauge-anchored crossing times for the published thresholds, under ERA5-Land and
   IMERG, raw and gauge-corrected -> the opposite-bias bracket.
3. Rerun the inventory date audit on ERA5-Land.
Writes data/results/*.csv|json. Local time = UTC+6."""
import json, glob, re
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
ROOT = Path(__file__).resolve().parents[1]; RES = ROOT / "results"; RES.mkdir(exist_ok=True)
LOCAL = pd.Timedelta(hours=6)
RANGAMATI = (22.5954, 92.1431); BANDARBAN = (22.1953, 92.2184)
GAUGE_24H = {"low": 332.0, "high": 343.0}          # FFWC 2017 / BMD via Islam et al. 2021 (A1)
# Failure window from contemporaneous reports (D1). Earliest is the first published clock time,
# landslides at Bandarban "around 2:30am" on 13 June (Dhaka Tribune, 13 Jun 2017); dawn from a
# survivor account (Al Jazeera, 14 Jun 2017); latest the Manikchhari slide that killed four
# soldiers "around 11am" (Dhaka Tribune).
FAIL = {"earliest": "2017-06-13 02:30", "dawn": "2017-06-13 05:30", "latest": "2017-06-13 11:00"}
# Inventory date correction. Fourteen records carry the malformed year "13/06/207".
# All fourteen are in Rangamati at Manikchhari, the 2007 cluster is entirely in Chittagong
# district, their centroid falls inside the 13 June 2017 cluster, and ERA5-Land gives
# 116.3 mm/24h at that point on 13 June 2017 against 23.1 mm on 13 June 2007. Read as 2017.
# Three records carry "15/06/217". All three are at Rangunia Eco Park (Chittagong), within
# 15 km of the Rangunia/Gomra records already dated 15/06/2017, and "217" admits no other
# reading within the inventory's 2001-2017 span. Read as 2017.
DATE_FIXES = {"13/06/207": "13/06/2017", "15/06/217": "15/06/2017"}

THRESH = [("empirical_24h_57.4", 24, 57.4), ("empirical_72h_130", 72, 130.0),
          ("operational_3h_100", 3, 100.0), ("operational_24h_200", 24, 200.0), ("operational_72h_350", 72, 350.0)]

# ---------------------------------------------------------------- ERA5-Land
def era5land_hourly():
    ds = xr.open_mfdataset(sorted(glob.glob(str(ROOT / "era5land" / "era5land_tp_*.nc"))),
                           combine="nested", concat_dim="valid_time", data_vars="minimal", coords="minimal", compat="override")
    tp = ds["tp"].sortby("valid_time").load() * 1000.0            # m -> mm, accumulated since 00 UTC
    t = pd.DatetimeIndex(tp["valid_time"].values)
    prev = tp.shift(valid_time=1)
    contiguous = np.r_[False, np.diff(t.values) == np.timedelta64(1, "h")]
    is01 = xr.DataArray(t.hour == 1, dims="valid_time", coords={"valid_time": tp["valid_time"]})
    keep = xr.DataArray(contiguous | (t.hour == 1), dims="valid_time", coords={"valid_time": tp["valid_time"]})
    hourly = xr.where(is01, tp, tp - prev).where(keep)             # drop 00 UTC with no prior 23 UTC
    hourly = hourly.clip(min=0)                                    # tiny negative float residuals
    return tp, hourly

def test_deaccumulation(tp, hourly):
    """Sum of reconstructed hours 01..00 must equal the next 00 UTC accumulated value."""
    t = pd.DatetimeIndex(tp["valid_time"].values); errs = []
    for d0 in sorted({x.normalize() for x in t}):
        hrs = [d0 + pd.Timedelta(hours=h) for h in range(1, 25)]
        if all(h in t for h in hrs):
            s = hourly.sel(valid_time=hrs).sum("valid_time")
            ref = tp.sel(valid_time=hrs[-1])
            errs.append(float(abs(s - ref).max()))
    assert errs, "no complete day to test"
    assert max(errs) < 0.05, f"de-accumulation error up to {max(errs):.4f} mm"
    return len(errs), max(errs)

def point(da, lat, lon, tname):
    """Nearest grid cell with data. ERA5-Land is land-only, so coastal centroids can fall in an
    empty cell; the nearest non-empty cell is used instead and its distance is recorded."""
    valid = da.notnull().any(tname)
    dist = (da["latitude"] - lat) ** 2 + (da["longitude"] - lon) ** 2
    dist = dist.where(valid)
    ij = np.unravel_index(int(np.nanargmin(dist.values)), dist.shape)
    cell = da.isel(latitude=ij[0], longitude=ij[1])
    point.last_km = float(np.sqrt(float(dist.values[ij])) * 111)
    s = cell.to_series()
    s.index = pd.DatetimeIndex(s.index) + LOCAL
    return s.dropna()

# ---------------------------------------------------------------- IMERG
def imerg_hourly_point(lat, lon):
    ds = xr.open_dataset(ROOT / "imerg" / "imerg_hh_2017-06_cht.nc")
    p = ds["precipitation"].sel(lat=lat, lon=lon, method="nearest").to_series()
    idx = p.index
    if not isinstance(idx, pd.DatetimeIndex):                      # cftime -> pandas
        idx = pd.DatetimeIndex([pd.Timestamp(str(x)) for x in idx])
    p.index = idx + LOCAL
    # Each IMERG time is the START of its half hour, whereas each ERA5-Land hour is labelled at its
    # END. Hours are summed on their start and then relabelled at their end, so that a rolling total
    # labelled t covers the same interval, up to t, in both products.
    return (p * 0.5).resample("h").sum().shift(1, freq="h")        # mm/h rate over 30 min -> mm per hour

# ---------------------------------------------------------------- thresholds
def crossings(s):
    out = {}
    for name, win, val in THRESH:
        r = s.rolling(win, min_periods=1).sum()
        hit = r[r >= val].index.min()
        out[name] = None if pd.isna(hit) else {
            "time": str(hit), **{f"lead_h_{k}": round((pd.Timestamp(v) - hit).total_seconds() / 3600, 1) for k, v in FAIL.items()}}
    return out

def june2017():
    tp, hourly = era5land_hourly()
    n, err = test_deaccumulation(tp, hourly)
    print(f"de-accumulation test: {n} complete days, max error {err:.5f} mm  PASS")
    era = point(hourly, *RANGAMATI, "valid_time").loc["2017-06-06":"2017-06-16"]
    series = {"era5land_raw": era}
    try:
        series["imerg_raw"] = imerg_hourly_point(*RANGAMATI).loc["2017-06-10":"2017-06-14 12:00"]
    except FileNotFoundError:
        print("IMERG file not yet available - ERA5-Land only")
    summary = {}
    for name, s in list(series.items()):
        mx24 = s.rolling(24, min_periods=1).sum().max()
        summary[name] = {"max24h_mm": round(float(mx24), 1), "peak_hourly_mm": round(float(s.max()), 1),
                         "ratio_to_gauge_343": round(float(mx24 / GAUGE_24H["high"]), 2),
                         "onset_first_hour_ge_1mm_after_12Jun": str(s.loc["2017-06-11 18:00":][s.loc["2017-06-11 18:00":] >= 1].index.min())}
        for g in ("low", "high"):
            k = GAUGE_24H[g] / mx24
            series[f"{name}_corr_{g}"] = s * k
            summary[name][f"K_{g}"] = round(float(k), 3)
    result = {"summary": summary, "crossings": {n: crossings(s) for n, s in series.items()}}
    (RES / "june2017_crossings.json").write_text(json.dumps(result, indent=1))
    pd.DataFrame({n: s for n, s in series.items()}).to_csv(RES / "june2017_hourly_rangamati.csv")
    return result

# ---------------------------------------------------------------- date audit
def audit():
    _, hourly = era5land_hourly()
    inv = pd.read_csv(ROOT / "rabby_li_inventory" / "inventory_wgs84.csv")
    inv["Date"] = inv["Date"].astype(str).str.strip().replace(DATE_FIXES)
    full = inv[inv["Date"].str.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}")]
    rows = []
    for d, g in full.groupby("Date"):
        if len(g) < 3: continue
        try: day = pd.to_datetime(d, dayfirst=True)
        except Exception: continue
        s = point(hourly, g["lat"].mean(), g["lon"].mean(), "valid_time")
        w = s.loc[day - pd.Timedelta(days=4): day + pd.Timedelta(hours=23)]
        if len(w) < 48:
            rows.append({"date": d, "n": len(g), "max24h": None, "max72h": None, "flag": "NO DATA"}); continue
        m24 = w.rolling(24, min_periods=1).sum().max(); m72 = w.rolling(72, min_periods=1).sum().max()
        flag = "OK" if m24 >= 57.4 else ("WEAK" if m24 >= 30 else "SUSPECT")
        rows.append({"date": d, "n": len(g), "max24h": round(float(m24), 1), "max72h": round(float(m72), 1), "flag": flag,
                     "cell_offset_km": round(point.last_km, 1)})
    df = pd.DataFrame(rows).sort_values("n", ascending=False)
    df.to_csv(RES / "date_audit_era5land.csv", index=False)
    return df

if __name__ == "__main__":
    import sys
    if "audit" in sys.argv: print(audit().to_string(index=False))
    else: print(json.dumps(june2017(), indent=1))
