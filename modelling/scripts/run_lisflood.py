#!/usr/bin/env python3
"""LISFLOOD-FP rain-on-grid for the Sangu above Bandarban town, three storms.

Questions (modelling README): flood versus landslide order, and where both hazards hit. The test
is the FFWC Bandarban stage record (register F1, H1, Y3): the river peaked on 13 June 2017
(+135 cm over danger level), 7 August 2023 (+283 cm) and 8 July 2026 (+96 cm). A model worth
reading for timing should put the peaks on those days and rank them 2023 > 2017 > 2026.

Domain from prep_sangu.py (GLO-30 at 90 m, 2,158 km2 catchment plus a 5.4 km downstream reach,
free boundaries). Rain: IMERG V07 half-hourly, confined to the catchment, as a dynamicrainfile
on 900 m tiles aligned with the DEM; scaled by one factor per storm so that IMERG at the
Bandarban station cell matches the station record, the same flat-anchor logic the manuscript
uses (2017: max 24 h = 332 mm, FFWC; 2026: max 24 h = 309 mm, BMD; 2023: 1-10 Aug = 856 mm,
NAWG). Inertial solver with the rainfall routing scheme for shallow flow on steep cells, uniform
Manning n (literature value) and no infiltration in the reference, uniform infiltration as a
sensitivity run. The sub-grid solver ignores the scalar 'infiltration' keyword (found 2026-10-06:
identical runs at 0, 2 and 5 mm/h); only an 'infilfile' grid (mm/h) is applied, to floodplain water.
Sub-grid channel (Neal et al. 2012) on the face-connected network: without it the Sangu is one
90 m cell with floodplain friction, cannot carry the flood, and spreads 7-13 m deep across the
valley floor (first runs, 2026-10-06). Channel width and depth are hydraulic-geometry guesses,
so stage is compared as timing and rank, never as an absolute level.

Usage: run_lisflood.py EVENT [--n 0.05] [--infil_mm_h 0] [--tag base]
Writes modelling/results/lisflood/<event>_<tag>/ and a summary JSON."""
import argparse, json, os, shutil, subprocess, time
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr, netCDF4
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
INP = ROOT / "modelling" / "inputs" / "sangu"
BIN = ROOT / "modelling" / "lisflood" / "bin" / "lisflood"
RES = ROOT / "modelling" / "results" / "lisflood"
# Runs execute in LISFLOOD_WORKDIR when set (internal disk) and are copied to RES when finished:
# the external SSD disconnected mid-run once (2026-10-06) and killed two runs.
WORK = Path(os.environ["LISFLOOD_WORKDIR"]) if os.environ.get("LISFLOOD_WORKDIR") else RES
STATION = (92.218, 22.195)
CH_MIN_KM2 = 5.0                                    # channel where four-neighbour drainage area >= 5 km2
W_COEF = 2.6                          # FFWC Bandarban (Sangu)
TILE = 10                                            # rain tile = 10 DEM cells = 900 m
BST = pd.Timedelta(hours=6)
EVENTS = {
    "2017": dict(imerg="imerg_hh_2017-06_cht.nc", t0="2017-06-09 18:00", t1="2017-06-14 06:00",
                 anchor=("max24h", 332.0), obs_peak_bst="2017-06-13", obs_cm_over_dl=135),
    "2023": dict(imerg="imerg_hh_2023-08_cht.nc", t0="2023-07-31 18:00", t1="2023-08-12 18:00",
                 anchor=("total", 856.0, "2023-07-31 18:00", "2023-08-10 18:00"),
                 obs_peak_bst="2023-08-07", obs_cm_over_dl=283),
    "2026": dict(imerg="imerg_hh_2026-07_cht.nc", t0="2026-07-02 18:00", t1="2026-07-10 18:00",
                 anchor=("max24h", 309.0), obs_peak_bst="2026-07-08", obs_cm_over_dl=96),
}


def header():
    h = {}
    with open(INP / "dem.asc") as f:
        for _ in range(6):
            k, v = f.readline().split(); h[k.lower()] = float(v)
    return h


def rain_grid(ev, h, mask):
    """IMERG (mm/h, half-hour steps) -> catchment-only accumulated mm per step on 900 m tiles."""
    da = xr.open_dataset(ROOT / "data" / "imerg" / ev["imerg"])["precipitation"]
    t = pd.DatetimeIndex([pd.Timestamp(str(x)) for x in da.time.values])
    da = da.assign_coords(time=t).sel(time=slice(ev["t0"], ev["t1"]))
    da = da.transpose("time", "lat", "lon")
    # anchor at the station cell
    st = da.sel(lon=STATION[0], lat=STATION[1], method="nearest").to_series() * 0.5      # mm per half hour
    if ev["anchor"][0] == "max24h":
        raw = float(st.rolling(48).sum().max())
    else:
        raw = float(st.loc[ev["anchor"][2]:ev["anchor"][3]].sum())
    k = ev["anchor"][1] / raw
    ny, nx = int(h["nrows"]), int(h["ncols"])
    ty, tx = -(-ny // TILE), -(-nx // TILE)
    # tile centres in UTM -> lon/lat -> nearest IMERG cell
    xs = h["xllcorner"] + (np.arange(tx) + 0.5) * TILE * h["cellsize"]
    top = h["yllcorner"] + ny * h["cellsize"]                                            # shared top edge
    ys = top - (np.arange(ty) + 0.5) * TILE * h["cellsize"]
    X, Y = np.meshgrid(xs, ys)
    lon, lat = Transformer.from_crs("EPSG:32646", "EPSG:4326", always_xy=True).transform(X, Y)
    li = np.abs(da.lon.values[None, None, :] - lon[..., None]).argmin(-1)
    la = np.abs(da.lat.values[None, None, :] - lat[..., None]).argmin(-1)
    # catchment fraction of each tile; the DEM grid is padded at the bottom/right to whole tiles
    mp = np.zeros((ty * TILE, tx * TILE)); mp[:ny, :nx] = mask
    frac = mp.reshape(ty, TILE, tx, TILE).mean(axis=(1, 3))
    vals = da.values[:, la, li] * 0.5 * k * frac[None]                                   # mm per step
    return vals.astype("f4"), xs, ys, t[(t >= ev["t0"]) & (t <= ev["t1"])], k, raw, frac


def write_rain(path, vals, xs, ys, times):
    hrs = (times - times[0]).total_seconds().values / 3600.0
    with netCDF4.Dataset(path, "w") as nc:
        nc.createDimension("time", len(hrs)); nc.createDimension("y", len(ys)); nc.createDimension("x", len(xs))
        v = nc.createVariable("time", "f8", ("time",)); v[:] = hrs; v.units = "hours"   # time first: reader
        v = nc.createVariable("y", "f8", ("y",)); v[:] = ys                              # takes its var id as
        v = nc.createVariable("x", "f8", ("x",)); v[:] = xs                              # the dim id
        v = nc.createVariable("rainfall_depth", "f4", ("time", "y", "x")); v[:] = vals; v.units = "mm"


def main(event, n, infil, tag, sgc_n=0.035, sim_h=None, extra=(), drop=(), w_coef=W_COEF):
    ev = EVENTS[event]; h = header()
    mask = np.load(INP / "mask.npy"); dom = json.loads((INP / "domain.json").read_text())
    run = WORK / f"{event}_{tag}"; shutil.rmtree(run, ignore_errors=True); run.mkdir(parents=True)
    vals, xs, ys, times, k, raw, frac = rain_grid(ev, h, mask)
    # the tile grid extends below the DEM's lower edge when rows are not a multiple of TILE; LISFLOOD
    # requires the same lower-left origin, so shift the DEM's yll down by the padding instead
    ny = int(h["nrows"]); pad = (-ny) % TILE
    dem = np.loadtxt(INP / "dem.asc", skiprows=6)
    nx = dem.shape[1]; padx = (-nx) % TILE
    dem = np.pad(dem, ((0, pad), (0, padx)), constant_values=-9999.0)
    yll = h["yllcorner"] - pad * h["cellsize"]
    hdr = (f"ncols {nx + padx}\nnrows {ny + pad}\nxllcorner {h['xllcorner']}\nyllcorner {yll}\n"
           f"cellsize {h['cellsize']}\nNODATA_value -9999")
    np.savetxt(run / "dem.asc", dem, fmt="%.4f", header=hdr, comments="")
    write_rain(run / "rain.nc", vals, xs, ys, times)
    # sub-grid channel on the face-connected network (prep_sangu.d4_accumulation), width from
    # downstream hydraulic geometry w = a * A^0.5 (A in km2), a = 2.6 giving ~120 m at the town,
    # capped below the 90 m cell; depth = SGCr * w^SGCp (LISFLOOD defaults 0.3, 0.76)
    A = np.load(INP / "acc4.npy") * h["cellsize"] ** 2 / 1e6
    width = np.where(A >= float(os.environ.get("LF_CH_MIN_KM2", CH_MIN_KM2)), np.minimum(w_coef * np.sqrt(A), 0.95 * h["cellsize"]), 0.0)
    width = np.pad(width, ((0, pad), (0, padx)))
    np.savetxt(run / "width.asc", width, fmt="%.2f", header=hdr, comments="")
    ox, oy = dom["outlet_utm"]
    (run / "town.stage").write_text(f"1\n{ox} {oy}\n")
    x0, x1 = h["xllcorner"], h["xllcorner"] + (nx + padx) * h["cellsize"]
    y0, y1 = yll, yll + (ny + pad) * h["cellsize"]
    (run / "free.bci").write_text(f"N {x0} {x1} FREE\nS {x0} {x1} FREE\nE {y0} {y1} FREE\nW {y0} {y1} FREE\n")
    sim = float((times[-1] - times[0]).total_seconds()) + 1800
    if sim_h:
        sim = min(sim, sim_h * 3600.0)                      # short diagnostic runs
    par = f"""DEMfile dem.asc
resroot run
dirroot out
sim_time {sim:.0f}
initial_tstep 10
massint 900
saveint {sim:.0f}
fpfric {n}
SGCwidth width.asc
SGCbank dem.asc
SGCn {sgc_n}
SGCr 0.3
SGCp 0.76
max_Froude 1
dynamicrainfile rain.nc
routing
routingspeed 0.1
routesfthresh 0.1
depththresh 0.003
bcifile free.bci
stagefile town.stage
elevoff
"""
    if infil > 0:
        np.savetxt(run / "infil.asc", np.full(dem.shape, infil), fmt="%.3f", header=hdr, comments="")
        par += "infilfile infil.asc\n"
    # diagnostic variants: drop par keywords (and the SGC block with 'SGC'), add others
    par = "".join(l + "\n" for l in par.splitlines() if not any(l.split()[0].startswith(d) for d in drop))
    par += "".join(e + "\n" for e in extra)
    (run / "run.par").write_text(par)
    t_start = time.time()
    env = {**os.environ, "OMP_NUM_THREADS": os.environ.get("LF_THREADS", "8")}
    with open(run / "lisflood.log", "w") as lg:
        rc = subprocess.run([str(BIN), "-v", "run.par"], cwd=run, stdout=lg, stderr=subprocess.STDOUT, env=env).returncode
    wall = time.time() - t_start
    out = {"event": event, "tag": tag, "n": n, "sgc_n": sgc_n, "w_coef": w_coef, "infil_mm_h": infil, "returncode": rc, "wall_s": round(wall),
           "anchor_factor": round(k, 3), "imerg_station_raw_mm": round(raw, 1),
           "catchment_rain_mm": round(float((vals.sum(0) * frac).sum() / frac.sum() / 1) if frac.sum() else 0, 1),
           "obs_peak_bst": ev["obs_peak_bst"], "obs_cm_over_dl": ev["obs_cm_over_dl"]}
    def series(path, col):
        """LISFLOOD text outputs: header lines, then 'Time; ...', then numeric rows."""
        lines = path.read_text().splitlines()
        i = next(k for k, l in enumerate(lines) if l.lstrip().startswith("Time"))
        rows = np.array([[float(v) for v in l.split()] for l in lines[i + 1:] if l.strip()])
        return pd.Series(rows[:, col], index=times[0] + pd.to_timedelta(rows[:, 0], unit="s") + BST)
    st = run / "out" / "run.stage"
    if st.exists():
        d = series(st, 1)
        out["depth_start_m"] = round(float(d.iloc[0]), 2)
        out["depth_peak_m"] = round(float(d.max()), 2)
        out["depth_peak_bst"] = d.idxmax().strftime("%Y-%m-%d %H:%M")
        out["first_above_half_peak_bst"] = d[d >= d.max() / 2].index[0].strftime("%Y-%m-%d %H:%M")
        w_out = min(w_coef * np.sqrt(dom["catchment_km2"]), 0.95 * h["cellsize"])
        bank = 0.3 * w_out ** 0.76                                                     # SGCr * w^SGCp
        out["bankfull_depth_m"] = round(bank, 2)
        over = d[d > bank]
        out["overbank_start_bst"] = over.index[0].strftime("%Y-%m-%d %H:%M") if len(over) else None
        out["overbank_hours"] = round(len(over) * 0.25, 1)
        d.to_csv(run / "town_depth.csv", header=["depth_m"])
    ms = run / "out" / "run.mass"
    if ms.exists():
        # Qout = outflow through the free boundaries; rain falls only in the catchment, so this is
        # the Sangu 5.4 km below the town
        q = series(ms, 8)
        q3 = q.rolling(12, center=True).mean()                       # 3 h mean: Qout oscillates at the free boundary
        out["qout_peak_3h_m3s"] = round(float(q3.max())); out["qout_peak_3h_bst"] = q3.idxmax().strftime("%Y-%m-%d %H:%M")
        vol = series(ms, 5); rn = series(ms, 11)
        out["max_stored_over_net_rain"] = round(float((vol / rn.where(rn > 1e6)).max()), 3)   # > 1 means the solver made water
        out["stored_end_mm"] = round(float(vol.iloc[-1]) / (mask.sum() * 8100) * 1000, 1)
        q.to_csv(run / "outflow.csv", header=["q_m3s"])
    (run / "summary.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out, indent=1))
    if WORK != RES:
        dest = RES / run.name; shutil.rmtree(dest, ignore_errors=True)
        shutil.copytree(run, dest, ignore=shutil.ignore_patterns("._*"))
    return out


if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("event"); a.add_argument("--n", type=float, default=0.05)
    a.add_argument("--infil_mm_h", type=float, default=0.0); a.add_argument("--tag", default="base")
    a.add_argument("--sim_h", type=float); a.add_argument("--par", action="append", default=[], help="extra par line")
    a.add_argument("--drop", action="append", default=[], help="drop par keywords starting with this")
    a.add_argument("--sgc_n", type=float, default=0.035); a.add_argument("--w_coef", type=float, default=W_COEF)
    p = a.parse_args(); main(p.event, p.n, p.infil_mm_h, p.tag, sgc_n=p.sgc_n, sim_h=p.sim_h, extra=p.par, drop=p.drop,
                             w_coef=p.w_coef)
