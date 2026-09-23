#!/usr/bin/env python3
"""Fetch ERA5-Land hourly total_precipitation over the SE Bangladesh hills for every window the
manuscript needs: the 2017 deep case, the 2023/2026 comparator windows, and the 15 inventory
date-audit windows. One CDS request per (year, month). Days are padded by one day before each
window because Bangladesh local time is UTC+6. Output: data/era5land/era5land_tp_YYYY_MM.nc"""
import cdsapi, datetime as dt
from pathlib import Path
from collections import defaultdict
OUT = Path(__file__).resolve().parents[1] / "era5land"; OUT.mkdir(exist_ok=True)
AREA = [23.8, 91.4, 20.7, 92.8]            # N, W, S, E

# (end_date, days_before) windows
WINDOWS = [
    ("2017-06-16", 10),   # deep case 6-16 June + audit 11, 13, 15 June
    ("2017-07-20", 15),   # audit 10 and 20 July 2017
    ("2023-08-12", 11),   # comparator
    ("2026-07-14", 12),   # comparator
    ("2010-06-15", 7), ("2007-06-11", 5), ("2013-07-28", 5), ("2008-06-06", 5),
    ("2008-07-03", 5), ("2012-06-26", 5), ("2016-06-01", 5), ("2011-07-01", 5),
]
need = defaultdict(set)
for end, back in WINDOWS:
    e = dt.date.fromisoformat(end)
    for k in range(back + 1):
        d = e - dt.timedelta(days=k); need[(d.year, d.month)].add(d.day)

c = cdsapi.Client()
for (y, m), days in sorted(need.items()):
    f = OUT / f"era5land_tp_{y}_{m:02d}.nc"
    if f.exists() and f.stat().st_size > 10_000:
        print("have", f.name); continue
    print(f"requesting {y}-{m:02d} days {sorted(days)}", flush=True)
    try:
        c.retrieve("reanalysis-era5-land", {
            "variable": ["total_precipitation"],
            "year": str(y), "month": f"{m:02d}", "day": [f"{d:02d}" for d in sorted(days)],
            "time": [f"{h:02d}:00" for h in range(24)],
            "area": AREA, "data_format": "netcdf", "download_format": "unarchived",
        }, str(f))
        print("  saved", f.name, f.stat().st_size, "bytes", flush=True)
    except Exception as ex:
        print(f"  FAILED {y}-{m:02d}: {ex}", flush=True)
print("DONE")
