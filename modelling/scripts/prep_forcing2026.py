#!/usr/bin/env python3
"""Hourly forcing for the Rangamati TRIGRS domain, July 2026, anchored as in 2017.

Each product (ERA5-Land, IMERG Late) is taken at the 2017 Rangamati failure centroid and scaled
uniformly so that its largest 24-hour total in 5-10 July equals the 287 mm that the Meteorological
Department's Rangamati station recorded in the 24 hours to 06:00 on 8 July. The 2017 forcing was
scaled the same way to the same station's 343 mm, so the two years differ only in the shape and
size of the storm as recorded on one district gauge. Other 2026 days at Rangamati were not
reported, so 287 mm is the only anchor. Writes modelling/inputs/rangamati2026/forcing_mm_per_h.csv."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data" / "scripts"))
import rain_analysis as ra                                            # noqa: E402

OUT = ROOT / "modelling" / "inputs" / "rangamati2026"; OUT.mkdir(parents=True, exist_ok=True)
GAUGE_MM = 287.0
f = pd.read_csv(ROOT / "modelling" / "inputs" / "rangamati2017" / "failures.csv")
LAT, LON = float(f.lat.mean()), float(f.lon.mean())


def era5():
    _, hourly = ra.era5land_hourly()
    return ra.point(hourly.sel(valid_time=slice("2026-06-30", "2026-07-15")), LAT, LON, "valid_time")


def imerg():
    da = xr.open_dataset(ROOT / "data" / "imerg" / "imerg_hh_2026-07_cht.nc")["precipitation"]
    s = da.sel(lat=LAT, lon=LON, method="nearest").to_series() * 0.5
    s.index = pd.DatetimeIndex([pd.Timestamp(str(x)) for x in s.index]).floor("h") + ra.LOCAL + pd.Timedelta(hours=1)
    return s.groupby(level=0).sum()                                   # labelled at hour end, as ERA5-Land


def main():
    idx = pd.date_range("2026-07-01 01:00", "2026-07-15 00:00", freq="h")
    out, meta = {}, {"centroid": [round(LAT, 4), round(LON, 4)], "gauge_mm": GAUGE_MM}
    for name, s in (("era5land", era5()), ("imerg", imerg())):
        s = s.reindex(idx).fillna(0.0)
        r24 = s.rolling(24, min_periods=1).sum().loc["2026-07-05":"2026-07-10"]
        k = GAUGE_MM / float(r24.max())
        out[name] = s * k
        meta[name] = {"raw_max24_mm": round(float(r24.max()), 1), "max24_end": str(r24.idxmax()),
                      "K": round(k, 3), "corrected_total_mm": round(float((s * k).sum()), 1)}
    pd.DataFrame(out).to_csv(OUT / "forcing_mm_per_h.csv")
    (OUT / "forcing.json").write_text(json.dumps(meta, indent=1)); print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
