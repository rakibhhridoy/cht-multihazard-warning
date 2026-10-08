#!/usr/bin/env python3
"""Where and in what order both hazards hit: LISFLOOD-FP flood footprint against the dated landslides.

For a run from run_lisflood.py, the 'flooded' cells are those whose maximum depth exceeds a
threshold (0.5 m by default) and that lie on the drainage network (flow accumulation >= 1 km2),
so the thin sheet of rain on every hillslope cell is not counted as flood. For each inventory
landslide inside the catchment dated within the run window: the distance to the nearest flooded
cell and that cell's modelled time of peak depth (.maxtm, hours from start). The same is done for
random catchment cells, so the share of landslides near flooded valleys can be read against what
the catchment's own geometry would give by chance.
Usage: lisflood_overlay.py RUN_DIR_NAME [--depth 0.5]. Writes <run>/overlay.json."""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from pyproj import Transformer
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data" / "scripts"))
INP = ROOT / "modelling" / "inputs" / "sangu"
RES = ROOT / "modelling" / "results" / "lisflood"
BST = pd.Timedelta(hours=6)


def grid(path):
    return np.loadtxt(path, skiprows=6)


def main(run_name, depth):
    run = RES / run_name; summ = json.loads((run / "summary.json").read_text())
    import run_lisflood as rl
    ev = rl.EVENTS[summ["event"]]; t0 = pd.Timestamp(ev["t0"])
    dom = json.loads((INP / "domain.json").read_text()); ny, nx = dom["shape"]
    mask = np.load(INP / "mask.npy"); acc = np.load(INP / "acc.npy")
    mx = grid(run / "out" / "run.max")[:ny, :nx]; tm = grid(run / "out" / "run.maxtm")[:ny, :nx]
    flooded = (mx >= depth) & (acc * 8100 / 1e6 >= 1.0)
    dist, (ir, ic) = distance_transform_edt(~flooded, return_indices=True)
    dist = dist * dom["res_m"]
    import skill
    inv = skill.load_inventory()
    x, y = Transformer.from_crs("EPSG:4326", "EPSG:32646", always_xy=True).transform(inv.lon.values, inv.lat.values)
    c = ((x - dom["xllcorner"]) // dom["res_m"]).astype(int)
    r = (ny - 1 - (y - dom["yllcorner"]) // dom["res_m"]).astype(int)
    ok = (r >= 0) & (r < ny) & (c >= 0) & (c < nx)
    inside = np.zeros(len(inv), bool); inside[ok] = mask[r[ok], c[ok]]
    t_lo, t_hi = (t0 + BST).normalize(), (pd.Timestamp(ev["t1"]) + BST).normalize()
    sel = inside & inv.D.between(t_lo, t_hi).values
    rr, cc = r[sel], c[sel]
    d_ls = dist[rr, cc]
    peak_ls = t0 + BST + pd.to_timedelta(tm[ir[rr, cc], ic[rr, cc]], unit="h")
    rng = np.random.default_rng(1)
    mr, mc = np.where(mask)
    k = rng.choice(len(mr), 20000, replace=False)
    d_rand = dist[mr[k], mc[k]]
    out = {"run": run_name, "depth_threshold_m": depth, "flooded_cells": int(flooded.sum()),
           "flooded_km2": round(float(flooded.sum()) * 0.0081, 1),
           "landslides_in_catchment_in_window": int(sel.sum()),
           "landslide_dates": {str(k.date()): int(v) for k, v in inv[sel].D.value_counts().items()}}
    if sel.sum():
        out["landslide_dist_to_flood_m_p25_50_75"] = [round(float(np.percentile(d_ls, q))) for q in (25, 50, 75)]
        out["random_dist_to_flood_m_p25_50_75"] = [round(float(np.percentile(d_rand, q))) for q in (25, 50, 75)]
        for lim in (250, 500, 1000):
            out[f"share_within_{lim}m"] = {"landslides": round(float((d_ls <= lim).mean()), 2),
                                            "random": round(float((d_rand <= lim).mean()), 2)}
        from scipy.stats import mannwhitneyu
        out["mannwhitney_p_landslides_closer"] = float(f"{mannwhitneyu(d_ls, d_rand, alternative='less').pvalue:.2g}")
        # clustering check: landslides are not independent (one storm, a few valleys), so also
        # test on one point per 1 km block
        blk = pd.Series(d_ls).groupby([(rr // 11), (cc // 11)]).median().values
        out["blocks_1km"] = int(len(blk))
        out["mannwhitney_p_blocks"] = float(f"{mannwhitneyu(blk, d_rand, alternative='less').pvalue:.2g}")
        out["nearest_flood_peak_bst_p10_50_90"] = [str(pd.Series(peak_ls).quantile(q).floor("h"))[:16] for q in (0.1, 0.5, 0.9)]
        pd.DataFrame({"lat": inv.lat.values[sel], "lon": inv.lon.values[sel], "date": inv.D.values[sel],
                      "dist_to_flood_m": d_ls, "nearest_flood_peak_bst": peak_ls}).to_csv(run / "overlay_points.csv", index=False)
    (run / "overlay.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("run"); a.add_argument("--depth", type=float, default=0.5)
    p = a.parse_args(); main(p.run, p.depth)
