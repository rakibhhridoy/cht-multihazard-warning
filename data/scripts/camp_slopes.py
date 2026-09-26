#!/usr/bin/env python3
"""Hillslope setting of the Rohingya camps, from the Copernicus GLO-30 DEM and the ISCG camp
outlines (HDX, 2023-04-12, CC0).

The DEM is built from TanDEM-X acquisitions of 2011-2015, before the camps were cleared in late
2017, so it describes the natural hillslopes into which shelters were later cut, not the cut
faces themselves, which are a few metres high and below its resolution. It can therefore test
whether the fatal camps and the camps on the highest-risk list sit on steeper ground, but not
the stability of any individual cut.

Groups: fatal = camps with landslide deaths in July 2026 (5, 7, 11, 15; register I8, L6);
listed = camps on the BDRCS 'highest landslide risk' list of SitRep 2 (register L4).
Writes data/results/camp_slopes.csv and camp_slopes.json."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd, geopandas as gpd, rasterio
from rasterio.merge import merge
from rasterio.warp import reproject, Resampling, calculate_default_transform
from rasterio.features import geometry_mask
from scipy.stats import mannwhitneyu

ROOT = Path(__file__).resolve().parents[1]; RES = ROOT / "results"
CAMPS = ROOT / "camps" / "20230412_A1_Camp_Outlines.shp"
DEMS = sorted((ROOT / "dem").glob("cop30_*.tif"))
FATAL = {"C05", "C07", "C11", "C15"}
LISTED = {"C03", "C07", "C08E", "C08W", "C09", "C10", "C11", "C12", "C13", "C14",
          "C16", "C18", "C19", "C20", "C20X"}
BANDS = (10, 15, 20)          # degrees; at 30 m nothing in the camps exceeds 26


def dem_utm():
    srcs = [rasterio.open(p) for p in DEMS]
    mosaic, tr = merge(srcs, bounds=(92.05, 20.85, 92.35, 21.30))
    src_crs = srcs[0].crs
    dst_crs = "EPSG:32646"
    h, w = mosaic.shape[1:]
    left, bottom, right, top = rasterio.transform.array_bounds(h, w, tr)
    dtr, dw, dh = calculate_default_transform(src_crs, dst_crs, w, h, left, bottom, right, top, resolution=30)
    out = np.full((dh, dw), np.nan, "float32")
    reproject(mosaic[0].astype("float32"), out, src_transform=tr, src_crs=src_crs,
              dst_transform=dtr, dst_crs=dst_crs, resampling=Resampling.bilinear, dst_nodata=np.nan)
    for s in srcs: s.close()
    return out, dtr


def slope_deg(z, res=30.0):
    gy, gx = np.gradient(z, res)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def main():
    z, tr = dem_utm()
    sl = slope_deg(z)
    camps = gpd.read_file(CAMPS).to_crs("EPSG:32646")
    rows = []
    for _, c in camps.iterrows():
        m = ~geometry_mask([c.geometry], out_shape=z.shape, transform=tr, invert=False)
        s = sl[m & np.isfinite(sl)]; e = z[m & np.isfinite(z)]
        row = {"camp": c.CampLabel, "name": c.CampName, "upazila": c.Upazila, "area_km2": round(float(c.AreaSqKM), 3),
               "cells": int(s.size), "slope_mean": round(float(s.mean()), 1), "slope_p90": round(float(np.percentile(s, 90)), 1),
               "relief_p95_p5_m": round(float(np.percentile(e, 95) - np.percentile(e, 5)), 1),
               "fatal_2026": c.CampLabel in FATAL, "highest_risk_list": c.CampLabel in LISTED}
        for b in BANDS:
            row[f"frac_gt{b}"] = round(float((s > b).mean()), 3)
        rows.append(row)
    df = pd.DataFrame(rows).sort_values("slope_p90", ascending=False).reset_index(drop=True)
    df["rank_slope_p90"] = np.arange(1, len(df) + 1)
    df.to_csv(RES / "camp_slopes.csv", index=False)

    ukhia = df[df.upazila == "Ukhia"]
    def compare(a, b, col):
        u = mannwhitneyu(a[col], b[col], alternative="greater")
        return {"median_in": round(float(a[col].median()), 3), "median_out": round(float(b[col].median()), 3),
                "n_in": int(len(a)), "n_out": int(len(b)), "mannwhitney_p_greater": round(float(u.pvalue), 3)}
    res = {"dem": [p.name for p in DEMS], "n_camps": int(len(df)), "n_ukhia": int(len(ukhia)),
           "fatal": df[df.fatal_2026][["camp", "slope_mean", "slope_p90", "rank_slope_p90", "highest_risk_list"]].to_dict("records"),
           "listed_vs_not_ukhia": {col: compare(ukhia[ukhia.highest_risk_list], ukhia[~ukhia.highest_risk_list], col)
                                   for col in ["slope_mean", "slope_p90", "frac_gt10", "relief_p95_p5_m"]},
           "fatal_vs_not_ukhia": {col: compare(ukhia[ukhia.fatal_2026], ukhia[~ukhia.fatal_2026], col)
                                  for col in ["slope_mean", "slope_p90", "frac_gt10", "relief_p95_p5_m"]}}
    (RES / "camp_slopes.json").write_text(json.dumps(res, indent=1))
    return df, res


if __name__ == "__main__":
    df, res = main()
    print(df[["camp", "upazila", "slope_mean", "slope_p90", "frac_gt10", "relief_p95_p5_m",
              "fatal_2026", "highest_risk_list", "rank_slope_p90"]].to_string(index=False))
    print(json.dumps({k: v for k, v in res.items() if k != "dem"}, indent=1))
