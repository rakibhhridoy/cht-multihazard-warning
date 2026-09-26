#!/usr/bin/env python3
"""IMERG V07 half-hourly for a comparator event, SE Bangladesh subset, same method as
fetch_imerg.py. Final (GPM_3IMERGHH) is used where released; July 2026 is not yet released as
Final, so the Late run (GPM_3IMERGHHL) is used for it.
Usage: fetch_imerg_event.py SHORT_NAME START END TAG
  e.g. fetch_imerg_event.py GPM_3IMERGHHL 2026-07-02T18:00 2026-07-14T18:00 2026-07
Output: data/imerg/imerg_hh_<TAG>_cht.nc (time in UTC, precipitation in mm/h)."""
import sys, earthaccess, xarray as xr
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "imerg_raw"; RAW.mkdir(exist_ok=True)
OUT = ROOT / "imerg"; OUT.mkdir(exist_ok=True)
short, t0, t1, tag = sys.argv[1:5]
earthaccess.login(strategy="netrc")
res = earthaccess.search_data(short_name=short, version="07", temporal=(t0, t1))
print("granules:", len(res), flush=True)
# Each granule's subset is cached, so an interrupted download resumes where it stopped.
CACHE = RAW / f"subset_{tag}"; CACHE.mkdir(exist_ok=True)
todo = [g for g in res if not (CACHE / (g.data_links()[0].split("/")[-1] + ".nc")).exists()]
print("to fetch:", len(todo), flush=True)
for i in range(0, len(todo), 6):
    files = earthaccess.download(todo[i:i + 6], str(RAW))
    for f in files:
        ds = xr.open_dataset(f, group="Grid", engine="netcdf4")
        ds["precipitation"].sel(lon=slice(91.4, 92.8), lat=slice(20.7, 23.8)).load() \
            .to_dataset(name="precipitation").to_netcdf(CACHE / (Path(f).name + ".nc"))
        ds.close(); Path(f).unlink()
    print(f"  {min(i + 6, len(todo))}/{len(todo)}", flush=True)
parts = [xr.open_dataset(f)["precipitation"].load() for f in sorted(CACHE.glob("*.nc")) if not f.name.startswith("._")]
da = xr.concat(parts, "time").sortby("time")
da.to_dataset(name="precipitation").to_netcdf(OUT / f"imerg_hh_{tag}_cht.nc")
print("DONE", short, da.shape, str(da.time.values[0])[:16], "->", str(da.time.values[-1])[:16])
