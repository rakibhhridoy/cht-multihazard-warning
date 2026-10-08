#!/usr/bin/env python3
"""GloFAS v5.0 reanalysis river discharge around the Sangu at Bandarban, an independent check on the
LISFLOOD-FP timing and ranking (register M10).

GloFAS routes ERA5 runoff through its own LISFLOOD hydrological model at 0.05 deg, so it shares
neither the IMERG forcing, the 90 m DEM nor the station anchor of the flood model. Daily mean
discharge (00-24 UTC), June-September 2001-2025 and June-July 2026 (v5.0 consolidated reaches July
2026; August 2026 not yet out). Served by the CEMS Early Warning Data Store (EWDS), which uses the
same personal access token as the CDS; the key is read from ~/.cdsapirc and never printed.

Each year lands on a temporary path, is opened and its days counted, then moved into place. Rerun
to resume. Writes data/glofas/glofas_<year>.nc."""
import os, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import cdsapi, xarray as xr

OUT = Path(__file__).resolve().parents[2] / "data" / "glofas"; OUT.mkdir(parents=True, exist_ok=True)
AREA = [22.45, 92.05, 21.95, 92.45]          # N, W, S, E: Bandarban town and the Sangu reach above it
URL = "https://ewds.climate.copernicus.eu/api"


def key():
    return re.search(r"key:\s*(\S+)", Path("~/.cdsapirc").expanduser().read_text()).group(1)


def ndays(path):
    try:
        with xr.open_dataset(path) as ds:
            t = "valid_time" if "valid_time" in ds.dims else "time"
            return ds.sizes[t]
    except Exception:
        return 0


def get(year):
    months = ["06", "07"] if year == 2026 else ["06", "07", "08", "09"]
    want = 61 if year == 2026 else 122
    final, tmp = OUT / f"glofas_{year}.nc", OUT / f".glofas_{year}.part"
    if final.exists() and ndays(final) >= want:
        return f"{year}: have"
    c = cdsapi.Client(url=URL, key=key(), quiet=True, progress=False)
    try:
        c.retrieve("cems-glofas-historical", {
            "system_version": ["version_5_0"], "hydrological_model": ["lisflood"],
            "product_type": ["consolidated"], "variable": ["average_river_discharge_in_the_last_24_hours"],
            "timespan": ["time_mean"], "year": [str(year)], "month": months,
            "day": [f"{d:02d}" for d in range(1, 32)], "data_format": "netcdf",
            "download_format": "unarchived", "area": AREA}, str(tmp))
    except Exception as e:
        return f"{year}: FAIL {str(e)[:300]}"
    n = ndays(tmp)
    if n < want:
        tmp.unlink(missing_ok=True); return f"{year}: incomplete ({n} days)"
    os.replace(tmp, final); return f"{year}: ok {n} days"


if __name__ == "__main__":
    years = [int(sys.argv[1])] if len(sys.argv) > 1 else list(range(2001, 2027))
    with ThreadPoolExecutor(4) as ex:
        for r in ex.map(get, years):
            print(r, flush=True)
