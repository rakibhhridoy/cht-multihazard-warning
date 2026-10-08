#!/usr/bin/env python3
"""Build the TRIGRS domain and forcing for Rangamati, June 2017.

Domain: the 160 inventory failures dated 13 June 2017 in Rangamati district, buffered by 1.5 km,
on the Copernicus GLO-30 surface model reprojected to UTM 46N at 30 m. Slope is computed from the
reprojected grid. GLO-30 is a surface model built from 2011-2015 radar and records the canopy top
where there is forest, so slopes are those of the vegetated hills rather than of cut faces.

Forcing: the gauge-anchored hourly series already used by the manuscript
(data/results/june2017_hourly_rangamati.csv), ERA5-Land and IMERG each scaled to the 343 mm
Rangamati station peak. The rain is spatially uniform over the domain (one reanalysis cell).

Writes modelling/inputs/rangamati2017/{dem,slope}.asc, a failure mask and forcing CSVs."""
import json, subprocess, sys
from pathlib import Path
import numpy as np, pandas as pd, rasterio
from rasterio.warp import transform as warp_xy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data" / "scripts"))
import rain_analysis as ra                                          # noqa: E402
import skill as sk                                                  # noqa: E402

OUT = ROOT / "modelling" / "inputs" / "rangamati2017"; OUT.mkdir(parents=True, exist_ok=True)
DEM_TILES = [ROOT / "data" / "dem" / f"cop30_N22_E09{i}.tif" for i in (1, 2)]
BUFFER_M, RES_M, CRS = 1500.0, 30.0, "EPSG:32646"


def failures():
    inv = sk.load_inventory()
    f = inv[(inv.District == "Rangamati") & (inv.D == "2017-06-13")].copy()
    x, y = warp_xy("EPSG:4326", CRS, f.lon.tolist(), f.lat.tolist())
    f["x"], f["y"] = x, y
    return f


def build_dem(f):
    x0, x1 = f.x.min() - BUFFER_M, f.x.max() + BUFFER_M
    y0, y1 = f.y.min() - BUFFER_M, f.y.max() + BUFFER_M
    x0, y0 = np.floor(x0 / RES_M) * RES_M, np.floor(y0 / RES_M) * RES_M
    x1, y1 = np.ceil(x1 / RES_M) * RES_M, np.ceil(y1 / RES_M) * RES_M
    vrt, tif = OUT / "dem_src.vrt", OUT / "dem_utm.tif"
    subprocess.run(["gdalbuildvrt", "-q", str(vrt), *map(str, DEM_TILES)], check=True)
    subprocess.run(["gdalwarp", "-q", "-overwrite", "-t_srs", CRS, "-tr", str(RES_M), str(RES_M),
                    "-te", str(x0), str(y0), str(x1), str(y1), "-r", "bilinear", str(vrt), str(tif)], check=True)
    with rasterio.open(tif) as src:
        z = src.read(1).astype(float); tr = src.transform
    return z, tr


def slope_deg(z):
    gy, gx = np.gradient(z, RES_M)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def write_asc(path, a, tr, fmt="%.3f"):
    nrows, ncols = a.shape
    hdr = (f"ncols {ncols}\nnrows {nrows}\nxllcorner {tr.c:.3f}\nyllcorner {tr.f - nrows * RES_M:.3f}\n"
           f"cellsize {RES_M:.1f}\nNODATA_value -9999\n")
    with open(path, "w") as fh:
        fh.write(hdr); np.savetxt(fh, a, fmt=fmt)


def main():
    f = failures()
    z, tr = build_dem(f)
    s = slope_deg(z)
    write_asc(OUT / "dem.asc", z, tr); write_asc(OUT / "slope.asc", s, tr, "%.2f")
    rows = ((tr.f - f.y) // RES_M).astype(int).values; cols = ((f.x - tr.c) // RES_M).astype(int).values
    mask = np.zeros(z.shape, int); mask[rows, cols] = 1
    np.save(OUT / "failure_mask.npy", mask)
    f[["lat", "lon", "x", "y", "Death_", "Fail_Type", "Area"]].assign(row=rows, col=cols).to_csv(OUT / "failures.csv", index=False)

    rain = pd.read_csv(ROOT / "data" / "results" / "june2017_hourly_rangamati.csv", index_col=0, parse_dates=True)
    win = rain.loc["2017-06-10 01:00":"2017-06-14 00:00"]
    forcing = pd.DataFrame({"era5land": win["era5land_raw_corr_high"], "imerg": win["imerg_raw_corr_high"]}).fillna(0.0)
    forcing.to_csv(OUT / "forcing_mm_per_h.csv")
    meta = {"shape": list(z.shape), "cells": int(z.size), "failure_cells": int(mask.sum()),
            "failures": int(len(f)), "slope_deg_all": [round(float(np.percentile(s, p)), 1) for p in (10, 50, 90)],
            "slope_deg_failures": [round(float(np.percentile(s[mask == 1], p)), 1) for p in (10, 50, 90)],
            "forcing_start": str(forcing.index[0]), "forcing_end": str(forcing.index[-1]),
            "forcing_total_mm": forcing.sum().round(1).to_dict(), "fail_window": ra.FAIL}
    (OUT / "domain.json").write_text(json.dumps(meta, indent=1))
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main()
