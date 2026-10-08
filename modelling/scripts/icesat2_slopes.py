#!/usr/bin/env python3
"""How much steeper are the Rangamati hills than the 30 m Copernicus model shows? ICESat-2 check.

ICESat-2 ATL08 (v007) gives terrain height every 20 m along each beam (h_te_best_fit_20m), from
photons classed as ground, so it sees the ground under the canopy where the radar surface model
sees the canopy top. Along-track slopes from ATL08 are set against slopes from the reprojected
GLO-30 grid (the TRIGRS domain) sampled at the same points with the same baseline, so both are
measured the same way and only the source differs.

Baselines of 20 m and 60 m are both reported. At 20 m the ground estimate's noise (about a metre
under canopy) adds spurious slope; the 60 m baseline damps that, and its noise floor is checked on
cells that the DEM calls near-flat. Along-track slope is a lower bound on the full gradient for
both sources alike, so the ratio between them, not either value, is the quantity of interest.
Writes modelling/results/icesat2_slopes.json and a point table."""
import json, glob
from pathlib import Path
import numpy as np, pandas as pd, netCDF4
import pyproj
from pyproj import Transformer
from scipy.ndimage import map_coordinates

ROOT = Path(__file__).resolve().parents[2]
INP = ROOT / "modelling" / "inputs" / "rangamati2017"
RES = ROOT / "modelling" / "results"
FILL = 1e30
TO_UTM = Transformer.from_crs("EPSG:4326", "EPSG:32646", always_xy=True)
# ATL08 heights are above the WGS84 ellipsoid; GLO-30 is above the EGM2008 geoid (about 53 m higher
# here). The EGM2008 grid is fetched by PROJ from cdn.proj.org on first use.
pyproj.network.set_network_enabled(True)
TO_EGM08 = Transformer.from_crs("EPSG:4979", "EPSG:4326+3855", always_xy=True)


def dem():
    hdr = {}
    with open(INP / "dem.asc") as fh:
        for _ in range(6):
            k, v = fh.readline().split(); hdr[k.lower()] = float(v)
    z = np.loadtxt(INP / "dem.asc", skiprows=6)
    return z, hdr


def sample(z, hdr, x, y):
    col = (x - hdr["xllcorner"]) / hdr["cellsize"] - 0.5
    row = (hdr["yllcorner"] + hdr["nrows"] * hdr["cellsize"] - y) / hdr["cellsize"] - 0.5
    ok = (col >= 0) & (row >= 0) & (col <= hdr["ncols"] - 1) & (row <= hdr["nrows"] - 1)
    v = np.full(len(x), np.nan); v[ok] = map_coordinates(z, [row[ok], col[ok]], order=1)
    return v


def beams(path):
    d = netCDF4.Dataset(path)
    for b in [g for g in d.groups if g.startswith("gt")]:
        ls = d.groups[b].groups.get("land_segments")
        if ls is None or ls.variables["latitude_20m"].shape[0] == 0:
            continue
        def arr(v):
            a = v[:]
            a = a.filled(np.nan) if np.ma.isMaskedArray(a) else np.asarray(a)
            return a.astype(float).ravel()
        lat, lon = arr(ls.variables["latitude_20m"]), arr(ls.variables["longitude_20m"])
        h = arr(ls.groups["terrain"].variables["h_te_best_fit_20m"])
        night = np.repeat(np.asarray(ls.variables["night_flag"][:]), 5).astype(float)
        lat[np.abs(lat) > 90] = np.nan; lon[np.abs(lon) > 180] = np.nan
        h[(h > FILL) | (np.abs(h) > 1e4)] = np.nan
        yield Path(path).name, b, lat, lon, h, night


def slopes(df, base):
    """Along-track slope over a baseline of `base` consecutive 20 m points, per beam track."""
    out = []
    for _, g in df.groupby(["granule", "beam"]):
        g = g.sort_values("s")
        x, y, hi, hd = g.x.values, g.y.values, g.h_is2.values, g.h_dem.values
        ds = np.hypot(x[base:] - x[:-base], y[base:] - y[:-base])
        good = (ds > 15 * base) & (ds < 25 * base)                      # consecutive points only
        si = np.degrees(np.arctan(np.abs(hi[base:] - hi[:-base]) / ds))
        sd = np.degrees(np.arctan(np.abs(hd[base:] - hd[:-base]) / ds))
        out.append(pd.DataFrame({"is2": si[good], "dem": sd[good]}))
    return pd.concat(out).dropna()


def main():
    z, hdr = dem()
    files = sorted(f for f in glob.glob(str(ROOT / "data" / "icesat2" / "atl08" / "ATL08_*.h5")))
    rows = []
    skipped = []
    for f in files:
        try:
            bl = list(beams(f))
        except (OSError, KeyError) as e:                             # incomplete or empty granule
            skipped.append(Path(f).name); continue
        for gran, b, lat, lon, h, night in bl:
            _, _, h = TO_EGM08.transform(lon, lat, h)
            h = np.asarray(h, float)
            x, y = TO_UTM.transform(lon, lat)
            x, y = np.asarray(x), np.asarray(y)
            hd = sample(z, hdr, x, y)
            k = np.isfinite(h) & np.isfinite(hd)
            if k.sum() < 10:
                continue
            s = np.concatenate([[0], np.cumsum(np.hypot(np.diff(x), np.diff(y)))])
            rows.append(pd.DataFrame({"granule": gran, "beam": b, "x": x[k], "y": y[k], "s": s[k],
                                      "h_is2": h[k], "h_dem": hd[k], "night": night[k]}))
    df = pd.concat(rows, ignore_index=True)
    dz = df.h_dem - df.h_is2                                         # canopy plus error
    df = df[(dz > -20) & (dz < 60)]                                  # canopy height plus error; reject gross outliers
    df.to_csv(RES / "icesat2_points.csv", index=False)
    out = {"geoid": "EGM2008 via PROJ (EPSG:4979 -> 4326+3855)", "granules_found": len(files), "granules_unreadable": skipped, "granules_used": int(df.granule.nunique()), "tracks": int(df.groupby(["granule", "beam"]).ngroups),
           "points": int(len(df)), "dem_minus_is2_m_pct10_50_90": [round(float(np.percentile(dz[(dz > -20) & (dz < 60)], q)), 1) for q in (10, 50, 90)]}
    for base in (1, 3):
        sl = slopes(df, base)
        flat = sl[sl.dem < 2]
        hill = sl[sl.dem >= 5]
        q = [50, 75, 90, 95]
        out[f"baseline_{20*base}m"] = {
            "pairs": int(len(sl)), "noise_floor_is2_deg_where_dem_lt2_pct50_90": [round(float(np.percentile(flat.is2, p)), 1) for p in (50, 90)] if len(flat) else None,
            "hill_dem_deg_pct": {p: round(float(np.percentile(hill.dem, p)), 1) for p in q},
            "hill_is2_deg_pct": {p: round(float(np.percentile(hill.is2, p)), 1) for p in q},
            "tan_ratio_is2_over_dem_median_on_hill": round(float(np.median(np.tan(np.radians(hill.is2)) / np.tan(np.radians(hill.dem)))), 2),
            "share_is2_ge_26deg_on_hill": round(float((hill.is2 >= 26).mean()), 3),
            "share_dem_ge_26deg_on_hill": round(float((hill.dem >= 26).mean()), 3)}
    (RES / "icesat2_slopes.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
