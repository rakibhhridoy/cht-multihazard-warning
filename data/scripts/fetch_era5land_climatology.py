#!/usr/bin/env python3
"""ERA5-Land hourly total precipitation over the Chittagong Hill Tracts, 1950 to present.

Monsoon months only (May to October), which carry essentially all of the region's extreme daily
rainfall. Hourly rather than daily because the CDS daily-statistics product does not support
accumulated variables, and because the 24-hour totals the thresholds are defined on are rolling
windows, not calendar days.

Two things learned the hard way shape this script.

The transfer drops mid-file often enough that a naive fetcher leaves truncated NetCDF behind, and
a truncated file usually still opens, with fewer hours, which would bias that season's maximum
downward without announcing itself. So every download lands on a temporary path, is opened and
counted, and only then moved into place. Coverage is decided by reading the files, never by
trusting a name or a size.

The dominant cost is CDS queue time, not bytes: single-year requests have spent 37 to 71 minutes
queued for 4 to 28 minutes of work. Batching years to pay that wait once would be the obvious
fix, and it is not available. CDS applies a per-request cost cap that sits between one year of
the six monsoon months (4,464 fields, accepted) and two years (8,928 fields, refused with
"cost limits exceeded"). One season is already near the ceiling, so CHUNK stays at 1 and the
queue is simply the price of the archive.
"""
import sys, time, os
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr, cdsapi

OUT = Path(__file__).resolve().parents[1] / "era5land_climatology"; OUT.mkdir(exist_ok=True)
AREA = [23.8, 91.7, 21.2, 92.8]          # N, W, S, E: the three hill districts plus Chattogram
MONTHS = [f"{m:02d}" for m in range(5, 11)]
FULL_SEASON_HOURS = 184 * 24             # May to October inclusive
YEARS = list(range(1950, 2027))
CHUNK = 1


def expected_hours(year):
    """The current year is short: ERA5-Land trails real time by a few days."""
    return 3000 if year >= 2026 else FULL_SEASON_HOURS


def covered_years():
    """Years already held, determined by opening every file and counting hours per year."""
    have = {}
    for f in sorted(OUT.glob("era5land_tp_*.nc")):
        try:
            with xr.open_dataset(f) as ds:
                tname = "valid_time" if "valid_time" in ds.dims else "time"
                yrs = pd.DatetimeIndex(ds[tname].values).year
        except Exception:
            continue
        for y, n in zip(*np.unique(yrs, return_counts=True)):
            have[int(y)] = have.get(int(y), 0) + int(n)
    return {y for y, n in have.items() if n >= expected_hours(y)}


def fetch_chunk(years, client):
    tag = f"{years[0]}-{years[-1]}" if len(years) > 1 else str(years[0])
    final = OUT / f"era5land_tp_{tag}.nc"
    tmp = OUT / f".era5land_tp_{tag}.part"
    req = {"variable": ["total_precipitation"], "year": [str(y) for y in years], "month": MONTHS,
           "day": [f"{d:02d}" for d in range(1, 32)],
           "time": [f"{h:02d}:00" for h in range(24)],
           "area": AREA, "data_format": "netcdf", "download_format": "unarchived"}
    client.retrieve("reanalysis-era5-land", req, str(tmp))
    want = sum(expected_hours(y) for y in years)
    try:
        with xr.open_dataset(tmp) as ds:
            tname = "valid_time" if "valid_time" in ds.dims else "time"
            got = ds.sizes[tname]
    except Exception as e:
        tmp.unlink(missing_ok=True); raise IOError(f"unreadable download: {e}")
    if got < want:
        tmp.unlink(missing_ok=True)
        raise IOError(f"incomplete: {got} h, expected >= {want}")
    os.replace(tmp, final)
    return f"{final.stat().st_size/1e6:.1f} MB, {got} h"


if __name__ == "__main__":
    c = cdsapi.Client()
    have = covered_years()
    todo = [y for y in YEARS if y not in have]
    print(f"held: {len(have)} years. remaining: {len(todo)} -> "
          f"{-(-len(todo)//CHUNK)} requests of up to {CHUNK}", flush=True)
    chunks = [todo[i:i + CHUNK] for i in range(0, len(todo), CHUNK)]
    failed = []
    for ch in chunks:
        for attempt in range(4):
            try:
                t0 = time.time()
                print(f"{ch[0]}-{ch[-1]}: {fetch_chunk(ch, c)} in {(time.time()-t0)/60:.0f} min",
                      flush=True); break
            except Exception as e:
                print(f"{ch[0]}-{ch[-1]}: attempt {attempt+1}/4 {type(e).__name__}: {str(e)[:110]}",
                      flush=True)
                time.sleep(30 * (attempt + 1))
        else:
            failed.append(ch); print(f"{ch[0]}-{ch[-1]}: GIVING UP", flush=True)
    print(f"\ndone. failed chunks: {failed if failed else 'none'}", flush=True)
