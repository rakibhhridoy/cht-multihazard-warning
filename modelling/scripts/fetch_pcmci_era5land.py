#!/usr/bin/env python3
"""ERA5-Land soil moisture, runoff and rain over the hill districts for the PCMCI lag analysis.

Two products. Daily: one field per day at 00 UTC for May to October 2001-2026. At 00 UTC the
ERA5-Land accumulations (tp, ro, sro) hold the whole previous UTC day, and the soil water layers
are a snapshot, so one time step gives a daily series without de-accumulation. Six variables
times 184 days is 1,104 fields per season, so four seasons fit under the CDS per-request cost
cap of about 4,464 fields. Hourly: the June 2017 and July 2026 storm months, for the event-scale
order of soil and river response.

The point time-series product (reanalysis-era5-land-timeseries) would be faster but carries
neither soil water nor runoff (both requests fail with MultiAdaptorNoDataError, 2026-10-06).

Every download lands on a temporary path, is opened and counted, then moved into place, as in
data/scripts/fetch_era5land_climatology.py. Rerun to resume. Writes data/pcmci/."""
import os, sys, tempfile, zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import xarray as xr, cdsapi

OUT = Path(__file__).resolve().parents[2] / "data" / "pcmci"; OUT.mkdir(exist_ok=True)
AREA = [23.0, 91.9, 21.8, 92.5]          # N, W, S, E: Rangamati and Bandarban districts, Sangu basin
VARS = ["total_precipitation", "runoff", "surface_runoff", "volumetric_soil_water_layer_1",
        "volumetric_soil_water_layer_2", "volumetric_soil_water_layer_3"]
DAYS = [f"{d:02d}" for d in range(1, 32)]
CHUNKS = [list(range(y, y + 4)) for y in range(2001, 2025, 4)] + [[2025]]
# 2026 is requested one month at a time, May to September: a multi-month 2026 request comes back as
# heterogeneous GRIB ("structural differences") and failed the day count twice (2026-10-06), while
# a single-month 2026 request (hourly July) opened cleanly.
MONTHS_2026 = ["05", "06", "07", "08", "09"]
EVENTS = {"2017_06": ("2017", "06"), "2026_07": ("2026", "07")}


def ok(path, want):
    try:
        with xr.open_dataset(path) as ds:
            t = "valid_time" if "valid_time" in ds.dims else "time"
            return ds.sizes[t] >= want
    except Exception:
        return False


def get(name, req, want):
    final, tmp = OUT / f"{name}.nc", OUT / f".{name}.part"
    if final.exists() and ok(final, want):
        return f"{name}: have"
    c = cdsapi.Client(quiet=True, progress=False)
    try:
        c.retrieve("reanalysis-era5-land", {**req, "variable": VARS, "area": AREA, "data_format": "netcdf",
                                            "download_format": "unarchived"}, str(tmp))
    except Exception as e:
        return f"{name}: FAIL {str(e)[:200]}"
    if zipfile.is_zipfile(tmp):                              # soil and accumulated fields split into two files
        d = Path(tempfile.mkdtemp()); zipfile.ZipFile(tmp).extractall(d)
        parts = [xr.open_dataset(f).drop_vars(["number", "expver"], errors="ignore") for f in sorted(d.glob("*.nc"))]
        xr.merge(parts).load().to_netcdf(tmp.with_suffix(".merged")); [x.close() for x in parts]
        os.replace(tmp.with_suffix(".merged"), tmp)
    if not ok(tmp, want):
        tmp.unlink(missing_ok=True); return f"{name}: incomplete"
    os.replace(tmp, final); return f"{name}: ok {final.stat().st_size/1e6:.1f} MB"


def jobs():
    for ys in CHUNKS:
        yield (f"daily_{ys[0]}-{ys[-1]}", {"year": [str(y) for y in ys], "month": [f"{m:02d}" for m in range(5, 11)],
                                          "day": DAYS, "time": ["00:00"]}, 184 * len(ys))
    for m in MONTHS_2026:
        yield (f"daily_2026_{m}", {"year": ["2026"], "month": [m], "day": DAYS, "time": ["00:00"]}, 30)
    for tag, (y, m) in EVENTS.items():
        yield (f"hourly_{tag}", {"year": [y], "month": [m], "day": DAYS, "time": [f"{h:02d}:00" for h in range(24)]},
               28 * 24)


if __name__ == "__main__":
    with ThreadPoolExecutor(int(sys.argv[1]) if len(sys.argv) > 1 else 4) as ex:
        for r in ex.map(lambda j: get(*j), list(jobs())):
            print(r, flush=True)
