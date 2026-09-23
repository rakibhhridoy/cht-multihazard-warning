#!/usr/bin/env python3
"""IMERG V07 Final half-hourly (GPM_3IMERGHH) for the June 2017 deep case. Downloads each global
granule, keeps the SE Bangladesh subset, deletes the global file. Output:
data/imerg/imerg_hh_2017-06_cht.nc (time in UTC, precipitation in mm/h)."""
import earthaccess, xarray as xr
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "imerg_raw"; RAW.mkdir(exist_ok=True)
OUT = ROOT / "imerg"; OUT.mkdir(exist_ok=True)
earthaccess.login(strategy="netrc")
res = earthaccess.search_data(short_name="GPM_3IMERGHH", version="07",
                              temporal=("2017-06-09T18:00:00", "2017-06-14T06:00:00"))
print("granules:", len(res), flush=True)
parts = []
for i in range(0, len(res), 12):
    files = earthaccess.download(res[i:i + 12], str(RAW))
    for f in files:
        ds = xr.open_dataset(f, group="Grid", engine="netcdf4")
        parts.append(ds["precipitation"].sel(lon=slice(91.4, 92.8), lat=slice(20.7, 23.8)).load())
        ds.close(); Path(f).unlink()
    print(f"  {min(i + 12, len(res))}/{len(res)}", flush=True)
da = xr.concat(parts, "time").sortby("time")
da.to_dataset(name="precipitation").to_netcdf(OUT / "imerg_hh_2017-06_cht.nc")
print("DONE", da.shape, str(da.time.values[0])[:16], "->", str(da.time.values[-1])[:16])
