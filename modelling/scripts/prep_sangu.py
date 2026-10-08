#!/usr/bin/env python3
"""Sangu catchment above Bandarban town for LISFLOOD-FP: DEM, catchment mask, river network.

GLO-30 tiles mosaicked and resampled to 90 m in UTM 46N (rain-on-grid over a ~1,500 km2 basin
is affordable on 8 cores at 90 m, not at 30 m). Flow directions from WhiteboxTools D8 after least-cost breaching
(pysheds fails under numpy 2); the outlet is snapped to the highest-accumulation cell within 1 km of the
FFWC Bandarban station (22.195 N, 92.218 E). Writes modelling/inputs/sangu/."""
import json, subprocess
from pathlib import Path
import numpy as np, rasterio
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "modelling" / "inputs" / "sangu"; OUT.mkdir(parents=True, exist_ok=True)
TILES = [ROOT / "data" / "dem" / f"cop30_{t}.tif" for t in ("N20_E092", "N21_E092", "N22_E092")]
STATION = (92.218, 22.195)
RES = 90


# WhiteboxTools D8 pointer codes -> (drow, dcol)
D8 = {1: (-1, 1), 2: (0, 1), 4: (1, 1), 8: (1, 0), 16: (1, -1), 32: (0, -1), 64: (-1, -1), 128: (-1, 0)}


def d4_condition(z, d8):
    """LISFLOOD-FP exchanges water across cell faces only, so a breached D8 path that steps
    diagonally is dammed at every diagonal step (first run: valleys ponded 38-40 m, outflow ~0).
    For each diagonal step, lower the lower of the two face-sharing cells to midway between the
    cell and its receiver, which gives a descending four-connected path. A lowered cell stays
    above the receiver, so it still drains and no pit is created."""
    z = z.copy(); n = 0
    for code, (dr, dc) in D8.items():
        if dr == 0 or dc == 0:
            continue
        rr, cc = np.where(d8 == code)
        ok = (rr + dr >= 0) & (rr + dr < z.shape[0]) & (cc + dc >= 0) & (cc + dc < z.shape[1])
        for r, c in zip(rr[ok], cc[ok]):
            z0, z1 = z[r, c], z[r + dr, c + dc]
            mid = (z0 + z1) / 2
            a, b = (r + dr, c), (r, c + dc)
            k = a if z[a] <= z[b] else b
            if z[k] > mid:
                z[k] = mid; n += 1
    return z, n


def d4_epsilon_fill(z, eps=0.001):
    """Priority-flood + epsilon (Barnes et al. 2014) on four neighbours, seeded from the domain edge
    (the free boundary): afterwards every cell has a strictly descending face-connected path out.
    Run after d4_condition, so it only lifts the few cells that lowering could not free."""
    import heapq
    ny, nx = z.shape; z = z.copy(); done = np.zeros(z.shape, bool); pq = []
    for r in range(ny):
        for c in (0, nx - 1):
            heapq.heappush(pq, (z[r, c], r, c)); done[r, c] = True
    for c in range(1, nx - 1):
        for r in (0, ny - 1):
            heapq.heappush(pq, (z[r, c], r, c)); done[r, c] = True
    raised = 0
    while pq:
        h, r, c = heapq.heappop(pq)
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            rr, cc = r + dr, c + dc
            if 0 <= rr < ny and 0 <= cc < nx and not done[rr, cc]:
                done[rr, cc] = True
                if z[rr, cc] <= h:
                    z[rr, cc] = h + eps; raised += 1
                heapq.heappush(pq, (z[rr, cc], rr, cc))
    return z, raised


def d4_accumulation(z):
    """Cells draining through each cell along steepest four-neighbour descent. After
    d4_epsilon_fill every cell has a lower face neighbour, so the network this defines is
    face-connected, as LISFLOOD-FP's sub-grid channel requires."""
    ny, nx = z.shape
    p = np.pad(z, 1, constant_values=np.inf)
    nbz = np.stack([p[1 + dr:1 + dr + ny, 1 + dc:1 + dc + nx] for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))])
    k = np.argmin(nbz, axis=0)
    edge = np.zeros(z.shape, bool); edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = True
    drop = z - nbz.min(axis=0)
    rr, cc = np.indices(z.shape)
    tr = rr + np.array([-1, 1, 0, 0])[k]; tc = cc + np.array([0, 0, -1, 1])[k]
    out = edge & (drop <= 0)                                       # edge cells with no lower neighbour leave
    acc = np.ones(z.shape)
    order = np.argsort(-z, axis=None)
    tflat = np.where(out.ravel(), -1, (tr * nx + tc).ravel())
    a = acc.ravel()
    for i in order:
        j = tflat[i]
        if j >= 0:
            a[j] += a[i]
    return a.reshape(z.shape)


def main():
    vrt = OUT / "src.vrt"; dem90 = OUT / "dem90_full.tif"
    subprocess.run(["gdalbuildvrt", "-q", str(vrt)] + [str(t) for t in TILES], check=True)
    subprocess.run(["gdalwarp", "-q", "-overwrite", "-t_srs", "EPSG:32646", "-tr", str(RES), str(RES), "-r", "average",
                    "-te", "390000", "2300000", "500000", "2470000", str(vrt), str(dem90)], check=True)
    import whitebox
    wbt = whitebox.WhiteboxTools(); wbt.set_verbose_mode(False); wbt.set_working_dir(str(OUT))
    wbt.breach_depressions_least_cost("dem90_full.tif", "breached.tif", dist=100, fill=True, flat_increment=0.01)  # no flats: equal neighbours let the routing scheme loop water
    wbt.d8_pointer("breached.tif", "d8.tif"); wbt.d8_flow_accumulation("breached.tif", "acc.tif", out_type="cells")
    with rasterio.open(OUT / "acc.tif") as src:
        acc = src.read(1); tr = src.transform; prof = src.profile
    x, y = Transformer.from_crs("EPSG:4326", "EPSG:32646", always_xy=True).transform(*STATION)
    r, c = int((tr.f - y) / RES), int((x - tr.c) / RES)
    k = int(1000 / RES)                                   # snap within 1 km to the main stem
    win = acc[r - k:r + k + 1, c - k:c + k + 1]
    dr, dc = np.unravel_index(int(np.argmax(win)), win.shape); r, c = r - k + dr, c - k + dc
    xs, ys = tr.c + (c + 0.5) * RES, tr.f - (r + 0.5) * RES
    with rasterio.open(OUT / "pour.tif", "w", **{**prof, "dtype": "int16", "nodata": 0}) as dst:
        a = np.zeros(acc.shape, "int16"); a[r, c] = 1; dst.write(a, 1)
    wbt.watershed("d8.tif", "pour.tif", "catch.tif")
    with rasterio.open(OUT / "catch.tif") as src:
        cfull = src.read(1) == 1
    with rasterio.open(OUT / "breached.tif") as src:
        zfull = src.read(1).astype(float)
    with rasterio.open(OUT / "d8.tif") as src:
        d8 = src.read(1)
    zfull, n_fixed = d4_condition(zfull, d8)
    area_km2 = float(cfull.sum()) * RES * RES / 1e6
    pad = 10
    rr, cc = np.where(cfull)
    # 60 extra cells (5.4 km) on the west keep the Sangu running downstream of the town before it
    # leaves through the free boundary, so the outlet stage is not set by the boundary itself
    r0, r1, c0, c1 = max(rr.min() - pad, 0), rr.max() + pad + 1, max(cc.min() - pad - 60, 0), cc.max() + pad + 1
    z = zfull[r0:r1, c0:c1].copy(); m = cfull[r0:r1, c0:c1]; ac = acc[r0:r1, c0:c1]
    z, n_raised = d4_epsilon_fill(z)
    xll = tr.c + c0 * RES; yll = tr.f - r1 * RES
    hdr = f"ncols {z.shape[1]}\nnrows {z.shape[0]}\nxllcorner {xll}\nyllcorner {yll}\ncellsize {RES}\nNODATA_value -9999"
    # Full terrain everywhere (nodata would become a wall at 1e7 m and dam the outlet); rain is
    # confined to the catchment by the rain mask written per event in run_lisflood.py
    np.savetxt(OUT / "dem.asc", z, fmt="%.4f", header=hdr, comments="")
    np.save(OUT / "acc.npy", ac); np.save(OUT / "mask.npy", m)
    acc4 = d4_accumulation(z)
    np.save(OUT / "acc4.npy", acc4)
    orow, ocol = r - r0, c - c0
    info = {"res_m": RES, "shape": list(z.shape), "catchment_km2": round(area_km2, 1), "cells": int(m.sum()),
            "outlet_utm": [float(xs), float(ys)], "outlet_rc": [int(orow), int(ocol)],
            "outlet_acc_cells": int(ac[orow, ocol]), "z_range": [float(z[m].min()), float(z[m].max())],
            "xllcorner": xll, "yllcorner": yll, "d4_cells_lowered": int(n_fixed),
            "d4_fill_cells_raised": int(n_raised)}
    (OUT / "domain.json").write_text(json.dumps(info, indent=1)); print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main()
