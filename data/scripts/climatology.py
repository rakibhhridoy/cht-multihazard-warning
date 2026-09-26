#!/usr/bin/env python3
"""Is the rainfall that drives the warning layer changing?

Reads the 1950-present ERA5-Land monsoon archive fetched by fetch_era5land_climatology.py and
asks three questions at the two points the manuscript already uses:

  1. Is the annual maximum rolling 24-hour and 72-hour rainfall trending?
  2. Where do June 2017, August 2023 and July 2026 sit in that distribution?
  3. Is the number of days per season that cross the warning thresholds changing?

A caution that governs the whole script: ERA5-Land underestimates this region's extreme
rainfall badly, capturing 34 % of the June 2017 gauge total. Three consequences are handled
explicitly rather than hidden.

  - The Mann-Kendall test is rank based, so it is invariant under any monotonic transformation.
    A constant multiplicative bias therefore cannot change the trend result. This is the most
    defensible number here.
  - The Sen slope is not invariant, so it is reported as a percentage of the series median per
    decade as well as in mm, and only the percentage should be quoted.
  - Absolute thresholds cannot be applied to uncorrected reanalysis. They are converted to
    ERA5-Land equivalents with the event gauge factor, and that factor's provenance and its
    single-event origin are stated wherever the result is used.

Writes data/results/climatology_*.csv|json.
"""
import json, glob
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"; RES.mkdir(exist_ok=True)
ARCHIVE = ROOT / "era5land_climatology"
LOCAL = pd.Timedelta(hours=6)
RANGAMATI = (22.5954, 92.1431); BANDARBAN = (22.1953, 92.2184)
GAUGE_FACTOR = 2.95        # ERA5-Land -> gauge, from the June 2017 anchor (343 mm); single event
THRESH_24H = {"empirical 57.4 mm (Roy et al. 2022)": 57.4,
              "installed 200 mm (Ali et al. 2018)": 200.0}
EVENTS = {"June 2017": 2017, "August 2023": 2023, "July 2026": 2026}
LAST_COMPLETE = 2025       # 2026 ends 21 Sep in the archive; excluded from trend and GEV


def load_hourly():
    """De-accumulate ERA5-Land tp to hourly mm, per year, on the same convention as
    rain_analysis.py: accumulation runs from 00 UTC and resets at 01 UTC."""
    out = []
    for f in sorted(glob.glob(str(ARCHIVE / "era5land_tp_*.nc"))):
        ds = xr.open_dataset(f)
        tname = "valid_time" if "valid_time" in ds.dims else "time"
        tp = ds["tp"].sortby(tname).load() * 1000.0
        t = pd.DatetimeIndex(tp[tname].values)
        prev = tp.shift({tname: 1})
        contiguous = np.r_[False, np.diff(t.values) == np.timedelta64(1, "h")]
        is01 = xr.DataArray(t.hour == 1, dims=tname, coords={tname: tp[tname]})
        keep = xr.DataArray(contiguous | (t.hour == 1), dims=tname, coords={tname: tp[tname]})
        hourly = xr.where(is01, tp, tp - prev).where(keep).clip(min=0)
        out.append(hourly.rename({tname: "time"}) if tname != "time" else hourly)
        ds.close()
    return xr.concat(out, dim="time").sortby("time")


def point_series(hourly, lat, lon):
    valid = hourly.notnull().any("time")
    dist = (hourly["latitude"] - lat) ** 2 + (hourly["longitude"] - lon) ** 2
    dist = dist.where(valid)
    ij = np.unravel_index(int(np.nanargmin(dist.values)), dist.shape)
    s = hourly.isel(latitude=ij[0], longitude=ij[1]).to_series()
    s.index = pd.DatetimeIndex(s.index) + LOCAL          # Bangladesh Standard Time
    return s.dropna()


def mann_kendall(x):
    """Two-sided Mann-Kendall with the standard tie correction, plus the Sen slope."""
    x = np.asarray(x, float); n = len(x)
    s = sum(np.sign(x[j] - x[i]).sum() for i, j in [(i, slice(i + 1, n)) for i in range(n - 1)])
    _, counts = np.unique(x, return_counts=True)
    var = (n * (n - 1) * (2 * n + 5) - sum(c * (c - 1) * (2 * c + 5) for c in counts)) / 18.0
    z = 0.0 if s == 0 else (s - np.sign(s)) / np.sqrt(var)
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    slopes = [(x[j] - x[i]) / (j - i) for i in range(n - 1) for j in range(i + 1, n)]
    return dict(S=float(s), Z=float(z), p=float(p), sen_slope_per_year=float(np.median(slopes)))


def gev_return(annmax, values):
    """GEV fitted to the annual maxima; return period of each value, and vice versa."""
    c, loc, scale = stats.genextreme.fit(annmax)
    out = {"gev_shape_c": float(c), "gev_loc": float(loc), "gev_scale": float(scale)}
    rp = {}
    for v in values:
        cdf = float(stats.genextreme.cdf(v, c, loc=loc, scale=scale))
        rp[f"{v:g}"] = float("inf") if cdf >= 1 else round(1.0 / (1.0 - cdf), 1)
    out["return_period_years"] = rp
    out["level_at_rp"] = {str(t): float(stats.genextreme.ppf(1 - 1.0 / t, c, loc=loc, scale=scale))
                          for t in (2, 5, 10, 25, 50, 100)}
    return out


def analyse(name, s):
    # Windows are defined on clock time, not row count: the archive is May-October only, so a
    # row-count window at the start of May would reach back into the previous October.
    r24 = s.rolling("24h", min_periods=24).sum()
    r72 = s.rolling("72h", min_periods=72).sum()
    yr = r24.index.year
    # The current season is incomplete (ERA5-Land trails real time), so it would enter a trend
    # test or GEV fit as an artificially low final point. Statistics use complete seasons only;
    # the partial season is still reported, as an event value.
    complete = sorted(y for y in set(yr) if y <= LAST_COMPLETE)
    res = {"point": name, "n_years": len(complete),
           "years": [complete[0], complete[-1]]}
    tables = {}
    for lab, r in [("24h", r24), ("72h", r72)]:
        am_all = r.groupby(r.index.year).max().dropna()
        am = am_all.loc[am_all.index <= LAST_COMPLETE]
        tables[lab] = am_all
        res[lab] = {"annual_max_mm": {"median": float(am.median()), "max": float(am.max()),
                                      "max_year": int(am.idxmax())},
                    "mann_kendall": mann_kendall(am.values),
                    "gev": gev_return(am.values, [am.median(), am.max()] +
                                      [float(am_all[v]) for v in EVENTS.values() if v in am_all.index])}
        res[lab]["mann_kendall"]["sen_slope_pct_of_median_per_decade"] = round(
            100 * 10 * res[lab]["mann_kendall"]["sen_slope_per_year"] / float(am.median()), 2)
        # The season maximum of an event year need not come from the event itself (Rangamati's
        # 2023 24-h maximum fell on 27 August, after the 8-9 August event), so it is an upper
        # bound on the event value and its return period is an upper bound on the event's.
        res[lab]["event_year_season_max"] = {k: (float(am_all[v]) if v in am_all.index else None)
                                             for k, v in EVENTS.items()}
        res[lab]["partial_season"] = {int(y): float(v) for y, v in am_all.items()
                                      if y > LAST_COMPLETE}
    # threshold exceedance: distinct days per season crossing each 24-hour threshold
    exc = {}
    for lab, mm in THRESH_24H.items():
        equiv = mm / GAUGE_FACTOR
        hits = r24[r24 >= equiv]
        per_year = hits.groupby(hits.index.year).apply(lambda h: h.index.normalize().nunique())
        per_year = per_year.reindex(sorted(set(yr)), fill_value=0)
        full = per_year.loc[per_year.index <= LAST_COMPLETE]
        exc[lab] = {"threshold_mm_gauge": mm, "era5land_equivalent_mm": round(equiv, 1),
                    "mean_days_per_season": round(float(full.mean()), 2),
                    "mann_kendall": mann_kendall(full.values.astype(float)),
                    "series": {int(k): int(v) for k, v in per_year.items()}}
    res["threshold_exceedance"] = exc
    return res, tables


if __name__ == "__main__":
    hourly = load_hourly()
    print(f"loaded {hourly.sizes['time']} hours, "
          f"{pd.Timestamp(hourly.time.values[0]):%Y-%m} to {pd.Timestamp(hourly.time.values[-1]):%Y-%m}")
    allres, frames = {}, {}
    for nm, (la, lo) in [("Rangamati", RANGAMATI), ("Bandarban", BANDARBAN)]:
        r, t = analyse(nm, point_series(hourly, la, lo))
        allres[nm] = r; frames[nm] = t
        mk = r["24h"]["mann_kendall"]
        print(f"{nm}: annual max 24h median {r['24h']['annual_max_mm']['median']:.1f} mm, "
              f"MK p={mk['p']:.3f}, Sen {mk['sen_slope_pct_of_median_per_decade']:+.1f}%/decade")
    (RES / "climatology.json").write_text(json.dumps(allres, indent=2))
    rows = []
    for nm, t in frames.items():
        for lab, am in t.items():
            for y, v in am.items():
                rows.append({"point": nm, "window": lab, "year": int(y), "annual_max_mm": float(v)})
    pd.DataFrame(rows).to_csv(RES / "climatology_annual_maxima.csv", index=False)
    print("wrote climatology.json and climatology_annual_maxima.csv")
