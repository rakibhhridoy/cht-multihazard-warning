#!/usr/bin/env python3
"""Run TRIGRS (USGS, v2.1.00c) for Rangamati, June 2017, and score it against the inventory.

One run = one parameter set and one forcing product. TRIGRS reads tr_in.txt from its working
directory, so each run gets its own folder under modelling/results/trigrs/<tag>/. Rain is
spatially uniform and given as hourly rates (cri); runoff routing is off (TRIGRS skips it when the
TopoIndex files are absent), so infiltration is min(rain, Ks) at every cell.

Scores: (1) timing, the share of failure cells whose factor of safety (FS) first falls below 1 at
each output hour, set against the 02:30-11:00 failure window of 13 June; (2) place, the AUC of the
final minimum FS at failure cells against all other hill cells (slope >= 5 deg), where lower FS
should mean more failures; (3) extent, the share of hill cells below FS 1, which is the model's
false-alarm burden.

Lookup mode (default). With one property zone, uniform depth, uniform initial water table and
spatially uniform rain, TRIGRS computes each cell independently and its result depends on the
cell's slope alone. TRIGRS is therefore run on a one-row grid holding every slope from 0 to 50
degrees in 0.25-degree steps, and each landscape cell takes the factor of safety of its slope by
linear interpolation (the 0.02 % of cells steeper than 50 degrees take the 50-degree value). This is the same code and the same equations at a fraction of the cost;
--grid full runs the whole landscape instead and is used to confirm the equivalence."""
import argparse, json, subprocess
from pathlib import Path
import numpy as np, pandas as pd

import os
ROOT = Path(__file__).resolve().parents[2]
TRG = ROOT / "modelling" / "trigrs" / "src" / "TRIGRS" / "trg"
INP = ROOT / "modelling" / "inputs" / "rangamati2017"
RES = Path(os.environ.get("TRIGRS_WORKDIR", ROOT / "modelling" / "results" / "trigrs"))
# Events share the 2017 domain (Rangamati failure area); only forcing and clocks differ. The 2026
# "window" is an assumption: SitRep 3 (12 Jul) reports 126 incidents "over four days" without dates.
EVENTS = {
    "2017": {"T0": "2017-06-10 00:00", "forcing": "rangamati2017",
             "out": ("2017-06-12 00:00", "2017-06-13 12:00", "h"), "window": ("2017-06-13 02:30", "2017-06-13 11:00")},
    "2026": {"T0": "2026-07-01 00:00", "forcing": "rangamati2026",
             "out": ("2026-07-03 00:00", "2026-07-14 18:00", "6h"), "window": ("2026-07-08 00:00", "2026-07-11 23:59")},
}


def clock(event):
    e = EVENTS[event]; t0 = pd.Timestamp(e["T0"])
    out = pd.DatetimeIndex([t0 + pd.Timedelta(hours=1)]).append(pd.date_range(*e["out"][:2], freq=e["out"][2]))
    return t0, out, pd.Timestamp(e["window"][0]), pd.Timestamp(e["window"][1]), ROOT / "modelling" / "inputs" / e["forcing"]


T0 = pd.Timestamp("2017-06-10 00:00")            # model time zero (BST); forcing starts 01:00
# First output one hour into the run, before any storm rain, to test that the landscape starts stable.
OUT_TIMES = pd.DatetimeIndex([pd.Timestamp("2017-06-10 01:00")]).append(
    pd.date_range("2017-06-12 00:00", "2017-06-13 12:00", freq="h"))
FAIL0, FAIL1 = pd.Timestamp("2017-06-13 02:30"), pd.Timestamp("2017-06-13 11:00")


def asc_header(path):
    h = {}
    with open(path) as fh:
        for _ in range(6):
            k, v = fh.readline().split(); h[k.lower()] = float(v)
    return h


def write_const(path, hdr_src, value):
    h = asc_header(hdr_src); nr, nc = int(h["nrows"]), int(h["ncols"])
    with open(hdr_src) as fh:
        head = "".join(fh.readline() for _ in range(6))
    with open(path, "w") as fh:
        fh.write(head); np.savetxt(fh, np.full((nr, nc), value), fmt="%.4g")


def read_asc(path):
    return np.loadtxt(path, skiprows=6)


LUT = np.round(np.arange(0.0, 50.0001, 0.25), 2)


def write_lut(d):
    head = (f"ncols {len(LUT)}\nnrows 1\nxllcorner 0\nyllcorner 0\ncellsize 30.0\nNODATA_value -9999\n")
    for name, row in (("slope_lut.asc", LUT), ("dem_lut.asc", np.full(len(LUT), 100.0))):
        with open(d / name, "w") as fh:
            fh.write(head); np.savetxt(fh, row[None, :], fmt="%.2f")
    return d / "slope_lut.asc", d / "dem_lut.asc"


def tr_in(p, run, rates_ms, slope_file, dem_file, t0=None, out_times=None):
    t0 = T0 if t0 is None else t0; out_times = OUT_TIMES if out_times is None else out_times
    nper = len(rates_ms)
    capt = [0.0] + [3600.0 * (i + 1) for i in range(nper)]
    tout = [(t - t0).total_seconds() for t in out_times]
    zone = (f"cohesion,phi,  uws,   diffus,   K-sat, Theta-sat,Theta-res,Alpha\n"
            f"{p['c']*1e3:.4g}, {p['phi']:.4g}, {p['uws']*1e3:.4g}, {p['D0']:.4g}, {p['Ks']:.4g}, 0.45, 0.05, -0.5\n")
    L = ["Name of project (up to 255 characters)", f"Rangamati June 2017 {run}",
         "tx, nmax, mmax, zones", "1,   30,   100,   1",
         "nzs,  zmin,  uww,    nper    t", f"10,   0.001,  9.8e3,   {nper},  {capt[-1]:.0f}",
         "zmax,   depth,   rizero,  Min_Slope_Angle (degrees), Max_Slope_Angle (degrees)",
         f"{-p['zmax']:.3f},  {-p['dwt']:.3f},  {p['rizero']:.3g},       0.,  90.0",
         "zone, 1", zone.rstrip("\n"),
         "cri(1), cri(2), ..., cri(nper)", ", ".join(f"{r:.4g}" for r in rates_ms),
         "capt(1), capt(2), ..., capt(n), capt(n+1)", ", ".join(f"{c:.0f}" for c in capt),
         "File name of slope angle grid (slofil)", str(slope_file),
         "File name of digital elevation grid (elevfil)", str(dem_file),
         "File name of property zone grid (zonfil)", "zones.asc",
         "File name of depth grid (zfil)", "zmax.asc",
         "File name of initial depth of water table grid   (depfil)", "depthwt.asc",
         "File name of initial infiltration rate grid   (rizerofil)", "rizero.asc",
         "List of file name(s) of rainfall intensity for each period, (rifil())",
         *["none"] * nper,
         "File name of grid of D8 runoff receptor cell numbers (nxtfil)", "none",
         "File name of list of cells defining runoff computation order (ndxfil)", "none",
         "File name of list of all runoff receptor cells  (dscfil)", "none",
         "File name of list of runoff weighting factors  (wffil)", "none",
         "Folder where output grid files will be stored  (folder)", "out/",
         "Identification code to be added to names of output files (suffix)", "r",
         "Save grid files of runoff? Enter T (.true.) or F (.false.)", "F",
         "Save grid of minimum factor of safety? Enter T (.true.) or F (.false.)", "T",
         "Save grid of depth of minimum factor of safety? Enter T (.true.) or F (.false.)", "F",
         "Save grid of pressure head at depth of minimum factor of safety? Enter T (.true.) or F (.false.)", "F",
         "Save grid of computed water table depth or elevation? Enter T (.true.) or F (.false.) followed by 'depth,' or 'eleva'", "F, depth",
         "Save grid files of actual infiltration rate? Enter T (.true.) or F (.false.)", "F",
         "Save grid files of unsaturated zone basal flux? Enter T (.true.) or F (.false.)", "F",
         "Save listing of pressure head and factor of safety (\"flag\")? Enter flag value followed by down-sampling interval (integer).", "0,1",
         "Number of times to save output grids and (or) ijz/xmdv files", str(len(tout)),
         "Times of output grids and (or) ijz / xmdv files", ", ".join(f"{t:.0f}" for t in tout),
         "Skip other timesteps? Enter T (.true.) or F (.false.)", "F",
         "Use analytic solution for fillable porosity?  Enter T (.true.) or F (.false.)", "T",
         "Estimate positive pressure head in rising water table zone (i.e. in lower part of unsat zone)?  Enter T (.true.) or F (.false.)", "T",
         "Use psi0=-1/alpha? Enter T (.true.) or F (.false.) (False selects the default value, psi0=0)", "F",
         "Log mass balance results?   Enter T (.true.) or F (.false.)", "F",
         "Flow direction (Enter \"gener\", \"slope\", or \"hydro\")", "gener",
         "Add steady background flux to transient infiltration rate to prevent drying beyond the initial conditions during periods of zero infiltration?", "T",
         "Specify file extension for output grids. Enter T (.true.) for \".asc\" or F for \".txt\"", "T",
         "Ignore negative pressure head in computing factor of safety (saturated infiltration only)?   Enter T (.true.) or F (.false.)", "T",
         "Ignore height of capillary fringe in computing pressure head for unsaturated infiltration option?   Enter T (.true.) or F (.false.)", "T",
         "Parameters for deep pressure-head estimate in SCOOPS ijz output: Depth below ground surface (positive, use negative value to cancel this option), pressure option (enter 'zero' , 'flow' , 'hydr' , or 'relh')",
         "-50.0,flow"]
    return "\n".join(L) + "\n"


def auc(pos, neg):
    """Probability that a failure cell has lower FS than a non-failure cell (ties count half)."""
    allv = np.concatenate([pos, neg]); r = pd.Series(allv).rank().values
    rp = r[:len(pos)].sum()
    return 1 - (rp - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


def run(p, product, tag, grid="lookup", event="2017"):
    t0, OUT_TIMES, FAIL0, FAIL1, finp = clock(event)
    d = RES / tag; (d / "out").mkdir(parents=True, exist_ok=True)
    for stale in ("TRgrid_size.txt", "TIgrid_size.txt", "GMgrid_size.txt"):   # TRIGRS caches grid size
        (d / stale).unlink(missing_ok=True)                                  # beside the DEM; never reuse
    for g in (d / "out").glob("TR*"):
        g.unlink()
    slope_file, dem_file = write_lut(d) if grid == "lookup" else (INP / "slope.asc", INP / "dem.asc")
    for name, val in (("zones.asc", 1), ("zmax.asc", p["zmax"]), ("depthwt.asc", p["dwt"]), ("rizero.asc", p["rizero"])):
        write_const(d / name, dem_file, val)
    f = pd.read_csv(finp / "forcing_mm_per_h.csv", index_col=0, parse_dates=True)[product]
    rates = (f.values / 1000.0 / 3600.0).tolist()                    # mm/h -> m/s
    (d / "tr_in.txt").write_text(tr_in(p, tag, rates, slope_file, dem_file, t0, OUT_TIMES))
    log = subprocess.run([str(TRG)], cwd=d, capture_output=True, text=True)
    (d / "trg.log").write_text(log.stdout + log.stderr)
    if "TRIGRS finished" not in log.stdout:
        raise RuntimeError(f"TRIGRS failed for {tag}; see {d/'trg.log'}")
    slope = read_asc(INP / "slope.asc"); mask = np.load(INP / "failure_mask.npy").astype(bool)
    hill = slope >= 5.0
    fs = np.stack([np.atleast_2d(read_asc(d / "out" / f"TRfs_min_r_{i+1}.asc")) for i in range(len(OUT_TIMES))])
    fs = np.where(fs < 0, np.nan, fs)
    if grid == "lookup":                                              # slope -> FS, per output time
        np.save(d / "fs_lut.npy", fs[:, 0, :])
        fs = np.stack([np.interp(slope, LUT, f[0]) for f in fs]).astype(np.float32)
    below = fs < 1.0
    share_fail = below[:, mask].mean(axis=1); share_hill = below[:, hill & ~mask].mean(axis=1)
    first = np.where(below[:, mask].any(axis=0), below[:, mask].argmax(axis=0), -1)
    t_first = [OUT_TIMES[i] for i in first if i > 0]                 # failures triggered after the start
    tf = pd.Series(t_first, dtype="datetime64[ns]")
    final = fs[-1]
    res = {"tag": tag, "event": event, "product": product, "grid": grid, "params": p,
           "fail_cells": int(mask.sum()), "hill_cells": int((hill & ~mask).sum()),
           "share_fail_cells_fs_lt1_final": round(float(share_fail[-1]), 3),
           "share_hill_cells_fs_lt1_final": round(float(share_hill[-1]), 3),
           "share_fail_cells_fs_lt1_by_02_30": round(float(share_fail[OUT_TIMES <= FAIL0][-1]), 3),
           "share_hill_fs_lt1_prestorm": round(float(share_hill[0]), 3),
           "share_fail_fs_lt1_prestorm": round(float(share_fail[0]), 3),
           "share_fail_triggered_in_window": round(float(((tf >= FAIL0.floor("h")) & (tf <= FAIL1)).sum() / mask.sum()), 3),
           "share_fail_triggered_before_window": round(float((tf < FAIL0.floor("h")).sum() / mask.sum()), 3),
           "median_first_fs_lt1": str(tf.median()) if len(tf) else None,
           "auc_final_fs": round(float(auc(final[mask], final[hill & ~mask])), 3),
           "fs_final_fail_cells_pct": [round(float(np.nanpercentile(final[mask], q)), 2) for q in (10, 50, 90)],
           "timeline": {str(t): [round(float(a), 3), round(float(b), 3)] for t, a, b in zip(OUT_TIMES, share_fail, share_hill)}}
    (d / "result.json").write_text(json.dumps(res, indent=1))
    for g in (d / "out").glob("TRfs_min_r_*.asc"):                   # keep the first and last grids only
        if g.name not in ("TRfs_min_r_1.asc", f"TRfs_min_r_{len(OUT_TIMES)}.asc"):
            g.unlink()
    return res


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--product", default="era5land"); a.add_argument("--tag", default="base_era5")
    a.add_argument("--grid", default="lookup", choices=["lookup", "full"])
    a.add_argument("--event", default="2017", choices=sorted(EVENTS))
    a.add_argument("--c", type=float, default=6.0, help="cohesion, kPa")
    a.add_argument("--phi", type=float, default=31.0, help="friction angle, deg")
    a.add_argument("--uws", type=float, default=19.0, help="saturated unit weight, kN/m3")
    a.add_argument("--Ks", type=float, default=1e-5, help="saturated hydraulic conductivity, m/s")
    a.add_argument("--D0", type=float, default=5e-4, help="hydraulic diffusivity, m2/s")
    a.add_argument("--zmax", type=float, default=2.0, help="soil depth, m")
    a.add_argument("--dwt", type=float, default=1.6, help="initial water-table depth, m")
    a.add_argument("--rizero", type=float, default=1e-8, help="steady background flux, m/s")
    v = vars(a.parse_args()); prod, tag, grid, ev = v.pop("product"), v.pop("tag"), v.pop("grid"), v.pop("event")
    r = run(v, prod, tag, grid, ev)
    print(json.dumps({k: r[k] for k in r if k != "timeline"}, indent=1))
