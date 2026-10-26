#!/usr/bin/env python3
"""Build the six manuscript figures (version 2, Nature/npj style).

File names follow the rendered figure numbers:
  fig1_june2017_hourly  - study area and the June 2017 storm (Section 3)
  fig2_skill            - correcting the reanalysis and the cost of the thresholds (Section 3)
  fig3_three_events     - the three compound events (Section 4)
  fig4_rangamati        - Rangamati 2017 against 2026, and where the 2026 deaths fell (Section 5)
  fig5_climatology      - 1950-2025 annual maxima (Section 5)
  fig6_models           - TRIGRS timing and the 2026 replay (Section 6)

Rainfall: ERA5-Land hourly from the Copernicus CDS and IMERG V07 half-hourly, processed by
data/scripts/rain_analysis.py (de-accumulation, local time, gauge anchoring).
Terrain: Copernicus GLO-90 tiles in data/dem/cop90/. Districts: geoBoundaries ADM2 in data/admin/.
Both, and the camp outlines, are fetched by data/scripts/fetch_public_inputs.py. The map figures also
need geopandas, shapely and rasterio.
Camps: ISCG/RRRC A1 camp outlines (12 Apr 2023). Failures: Rabby & Li inventory, 13 Jun 2017.
Event facts are taken from review/claims-register.md (IDs noted inline).
The version-1 figures and script are kept in figures/_v1_2026-10-08/.
"""
import json, math, urllib.request, urllib.parse, time, sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

# The same file runs from the public repository (figures/) and from the manuscript tree
# (manuscript/figures/), so the project root is the nearest ancestor holding data/.
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "data" / "scripts").is_dir())
CACHE = ROOT / "data" / "figdata"; CACHE.mkdir(parents=True, exist_ok=True)
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "data" / "scripts"))

# ---- validated palette (dataviz reference, light; all checks pass) ------------------------
RAIN, SLIDE, FLOOD, WARN = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, MUTED, GRID, BAND = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#f0efec"
SLIDE_T, WARN_T, SEA = "#fbe1d6", "#fcefcc", "#e4ecf2"

# ---- typography: Nature style, sans-serif, 5-7 pt, TrueType embedded ---------------------
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7, "axes.titlesize": 7, "axes.labelsize": 7,
    "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "legend.fontsize": 6.5,
    "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.5, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5, "lines.linewidth": 1.0,
    "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none",
    "savefig.facecolor": "white", "figure.facecolor": "white", "savefig.dpi": 300,
})
HALO = [pe.withStroke(linewidth=2.2, foreground="white")]
W2 = 7.09                                   # double-column width, 180 mm


def letter(ax, s, x=-0.02, y=1.0, fig=None):
    """Bold lower-case panel letter, Nature style, at the top-left of an axes."""
    ax.text(x, y, s, transform=ax.transAxes, fontsize=8, fontweight="bold", color=INK,
            ha="right", va="bottom")


def heading(ax, s, pad=4):
    ax.set_title(s, loc="left", fontsize=7, color=INK, pad=pad, fontweight="normal")


def grid(ax, axis="y"):
    ax.grid(axis=axis, color=GRID, lw=0.45); ax.set_axisbelow(True)


def save(fig, stem):
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ======================================================================================
# data helpers (unchanged from version 1)
# ======================================================================================
def hourly(lat, lon, start, end, tag):
    f = CACHE / f"{tag}.csv"
    if f.exists():
        return pd.read_csv(f, parse_dates=["time"])
    q = urllib.parse.urlencode({"latitude": lat, "longitude": lon, "start_date": start, "end_date": end,
                                "hourly": "precipitation", "timezone": "Asia/Dhaka"})
    for i in range(4):
        try:
            d = json.load(urllib.request.urlopen("https://archive-api.open-meteo.com/v1/archive?" + q, timeout=60))
            break
        except Exception:
            time.sleep(3 * (i + 1))
    df = pd.DataFrame({"time": pd.to_datetime(d["hourly"]["time"]), "mm": d["hourly"]["precipitation"]}).fillna(0)
    df.to_csv(f, index=False)
    return df


import rain_analysis as ra
_ERA = None
def era5land_point(lat, lon, start, end):
    """Hourly ERA5-Land at a point, cached to data/figdata/ so the figure rebuilds without the
    raw NetCDF. Delete the cache file to re-derive the series from source."""
    f = CACHE / ("era5land_%s_%s_%s.csv" % (lat, lon, start[:10]))
    if f.exists():
        return pd.read_csv(f, index_col=0, parse_dates=True).iloc[:, 0]
    global _ERA
    if _ERA is None:
        _ERA = ra.era5land_hourly()[1]
    s = ra.point(_ERA, lat, lon, "valid_time").loc[start:end]
    if s.index.max() < pd.Timestamp(end):
        # The event files stop on 14 July 2026; the season file of the climatology archive
        # gives identical hourly values at this cell (checked to 4e-6 mm) and runs further.
        import climatology as cl
        season = sorted((cl.ARCHIVE).glob("era5land_tp_%s.nc" % start[:4]))
        _glob, cl.glob.glob = cl.glob.glob, (lambda p: [str(x) for x in season])
        try:
            ext = cl.point_series(cl.load_hourly(), lat, lon)
        finally:
            cl.glob.glob = _glob
        s = pd.concat([s, ext.loc[s.index.max() + pd.Timedelta(hours=1):end]])
    s.to_csv(f)
    return s


BANDARBAN = (22.1953, 92.2184)      # Bandarban town, where the 2017 gauge peak was reported
RANGAMATI = (22.5954, 92.1431)      # centroid of the 160 Rangamati failures, 13 Jun 2017

# ======================================================================================
# map layers
# ======================================================================================
ADM2 = ROOT / "data" / "admin" / "bgd_adm2.geojson"          # geoBoundaries ADM2, data/scripts/fetch_public_inputs.py
CAMPS = ROOT / "data" / "camps" / "20230412_A1_Camp_Outlines.shp"
DEM90 = ROOT / "data" / "dem" / "cop90"
REGION = ["Rangamati", "Bandarban", "Khagrachhari", "Chittagong", "Cox's Bazar"]
# BMD rain gauges (town coordinates, as data/scripts/event2026.py) and FFWC river gauges
# (as data/scripts/shared_clock.py)
RAIN_GAUGES = {"Rangamati": (22.64, 92.20), "Bandarban": (22.20, 92.22), "Chattogram": (22.35, 91.82),
               "Cox's Bazar": (21.43, 91.93), "Kutubdia": (21.82, 91.85)}
RIVER_GAUGES = {"Sangu": (22.195, 92.218), "Matamuhuri": (21.78, 92.19)}


def layers():
    import geopandas as gpd
    adm = gpd.read_file(ADM2).to_crs(4326)
    adm["geometry"] = adm.geometry.simplify(0.001, preserve_topology=True)   # ~100 m, far below print size
    camps = gpd.read_file(CAMPS).to_crs(4326)
    inv = pd.read_csv(ROOT / "data" / "rabby_li_inventory" / "inventory_wgs84.csv")
    inv["Date"] = inv["Date"].astype(str).str.strip().replace(ra.DATE_FIXES)
    f17 = inv[inv.Date == "13/06/2017"]                                   # Q2: 257 points
    assert len(f17) == 257, len(f17)
    return adm, camps, f17


def hillshade(bounds, res=0.0022):
    """Merged GLO-90 elevation and a multidirectional hillshade on a lon/lat grid, cached."""
    f = CACHE / ("hillshade_%.2f_%.2f_%.2f_%.2f_%g.npz" % (*bounds, res))
    if f.exists():
        z = np.load(f); return z["hs"], z["elev"], tuple(z["ext"])
    import rasterio
    from rasterio.merge import merge
    srcs = [rasterio.open(p) for p in sorted(DEM90.glob("Copernicus_*.tif"))]
    elev, tr = merge(srcs, bounds=bounds, res=res, nodata=-9999, resampling=rasterio.enums.Resampling.average)
    elev = elev[0].astype(float); elev[elev == -9999] = np.nan
    lat0 = (bounds[1] + bounds[3]) / 2
    dy = res * 111_320; dx = dy * math.cos(math.radians(lat0))
    z = np.nan_to_num(elev, nan=0.0) * 2.0                                  # mild exaggeration
    gy, gx = np.gradient(z, dy, dx)
    slope = np.arctan(np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    hs = np.zeros_like(z)
    for az, w in [(315, 0.5), (270, 0.25), (360, 0.25)]:
        a, alt = math.radians(az), math.radians(40)
        hs += w * (np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(a - aspect))
    ext = (bounds[0], bounds[2], bounds[1], bounds[3])
    np.savez_compressed(f, hs=hs, elev=elev, ext=np.array(ext))
    return hs, elev, ext


def basemap(ax, adm, bounds, region_fade=True):
    """Hillshaded terrain, sea, Bangladesh districts; terrain outside Bangladesh is faded."""
    from matplotlib.colors import LinearSegmentedColormap
    hs, elev, ext = hillshade(bounds)
    ax.set_facecolor(SEA)
    land = np.isfinite(elev) & (elev > 0.5)
    shade = LinearSegmentedColormap.from_list("hs", ["#7f7c75", "#c9c6bf", "#fbfaf7"])
    rgba = shade(np.clip((hs - 0.45) / 0.5, 0, 1))
    rgba[..., 3] = np.where(land, 1.0, 0.0)
    ax.imshow(rgba, extent=ext, origin="upper", interpolation="bilinear", zorder=0)
    # fade terrain outside Bangladesh by drawing a white veil with Bangladesh cut out
    import shapely
    bd = adm.union_all() if hasattr(adm, "union_all") else adm.unary_union
    box = shapely.box(bounds[0], bounds[1], bounds[2], bounds[3])
    outside = box.difference(bd)
    import geopandas as gpd
    gpd.GeoSeries([outside]).plot(ax=ax, color="white", alpha=0.62, lw=0, zorder=1)
    import shapely
    adm = adm.clip(shapely.box(bounds[0] - 0.1, bounds[1] - 0.1, bounds[2] + 0.1, bounds[3] + 0.1))
    adm.boundary.plot(ax=ax, color="white", lw=0.9, zorder=2)
    adm.boundary.plot(ax=ax, color="#7d7a73", lw=0.35, zorder=2)
    gpd.GeoSeries([bd]).boundary.plot(ax=ax, color=INK2, lw=0.6, zorder=2)
    ax.set_xlim(bounds[0], bounds[2]); ax.set_ylim(bounds[1], bounds[3])
    ax.set_aspect(1 / math.cos(math.radians((bounds[1] + bounds[3]) / 2)))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True); s.set_color(INK2); s.set_linewidth(0.5)


def scalebar(ax, lon, lat, km=20):
    dlon = km / (111.32 * math.cos(math.radians(lat)))
    ax.plot([lon, lon + dlon], [lat, lat], color=INK, lw=1.4, solid_capstyle="butt", zorder=6)
    ax.text(lon + dlon / 2, lat + 0.03, f"{km} km", ha="center", va="bottom", fontsize=5.8, color=INK, zorder=6,
            path_effects=HALO)


def north(ax, lon, lat):
    ax.annotate("N", xy=(lon, lat + 0.09), xytext=(lon, lat), ha="center", va="bottom", fontsize=6,
                fontweight="bold", color=INK, zorder=6,
                arrowprops=dict(arrowstyle="-|>", lw=0.6, color=INK, shrinkA=6, shrinkB=0))


# ======================================================================================
# Figure 1 - where, and the June 2017 storm hour by hour
# ======================================================================================
def fig1():
    adm, camps, f17 = layers()
    reg = adm[adm.shapeName.isin(REGION)]
    d = pd.read_csv(ROOT / "data" / "results" / "june2017_hourly_rangamati.csv", index_col=0, parse_dates=True)
    prods = [("ERA5-Land", "era5land_raw", RAIN), ("IMERG", "imerg_raw", SLIDE)]
    t0, t1 = pd.Timestamp("2017-06-10 12:00"), pd.Timestamp("2017-06-14 00:00")
    win = (pd.Timestamp("2017-06-13 02:30"), pd.Timestamp("2017-06-13 11:00"))      # Q4, published clock times

    fig = plt.figure(figsize=(W2, 4.35))
    gs = fig.add_gridspec(2, 2, width_ratios=[0.78, 2.0], height_ratios=[1, 1.75],
                          wspace=0.16, hspace=0.12, left=0.01, right=0.99, top=0.95, bottom=0.11)
    m = fig.add_subplot(gs[:, 0]); a = fig.add_subplot(gs[0, 1]); b = fig.add_subplot(gs[1, 1], sharex=a)

    # ---- (a) map ----
    bounds = (91.68, 20.72, 92.70, 23.20)
    basemap(m, adm, bounds)
    camps.plot(ax=m, color=INK, lw=0, zorder=3)
    m.scatter(f17.lon, f17.lat, s=3.2, color=SLIDE, lw=0.15, edgecolor="white", zorder=4)
    for nm, (la, lo) in RAIN_GAUGES.items():
        m.scatter(lo, la, s=13, marker="s", facecolor="white", edgecolor=RAIN, lw=0.9, zorder=5)
    for nm, (la, lo) in RIVER_GAUGES.items():
        m.scatter(lo + 0.035, la, s=15, marker="^", color=FLOOD, edgecolor="white", lw=0.4, zorder=5)
    lab = {"Rangamati": (92.30, 22.86), "Bandarban": (92.40, 21.98), "Chittagong": (91.86, 22.66),
           "Cox's Bazar": (92.05, 21.62), "Khagrachhari": (92.02, 23.10)}
    show = {"Chittagong": "Chattogram"}
    for k, (lo, la) in lab.items():
        m.text(lo, la, show.get(k, k), fontsize=6, color=INK2, ha="center", style="italic", zorder=6, path_effects=HALO)
    m.text(91.80, 21.25, "Bay of\nBengal", fontsize=5.8, color="#6d8597", ha="center", style="italic", zorder=6)
    m.annotate("Rohingya\ncamps", xy=(92.15, 21.12), xytext=(91.80, 20.92), fontsize=5.8, color=INK, ha="center",
               zorder=6, path_effects=HALO, arrowprops=dict(arrowstyle="-", lw=0.5, color=INK, shrinkB=2))
    scalebar(m, 91.74, 20.80); north(m, 92.62, 22.98)
    hd = [Line2D([], [], ls="", marker="o", ms=3.2, mfc=SLIDE, mec="white", mew=0.2, label="failure, 13 Jun 2017 (n = 257)"),
          Line2D([], [], ls="", marker="s", ms=3.6, mfc="white", mec=RAIN, mew=0.9, label="rain gauge (BMD)"),
          Line2D([], [], ls="", marker="^", ms=4, mfc=FLOOD, mec="white", mew=0.3, label="river gauge (FFWC)"),
          Line2D([], [], ls="", marker="s", ms=4, mfc=INK, mec=INK, label="refugee camp")]
    m.legend(handles=hd, loc="upper left", bbox_to_anchor=(0.0, -0.005), frameon=False, fontsize=5.8,
             handletextpad=0.3, borderaxespad=0.2, labelspacing=0.35)
    letter(m, "a", x=0.0, y=1.01)
    # inset: where the region sits in Bangladesh
    ins = m.inset_axes([0.70, 0.015, 0.29, 0.20])
    adm.simplify(0.02).plot(ax=ins, color="#d9d7d0", lw=0)
    reg.simplify(0.02).plot(ax=ins, color=INK2, lw=0)
    ins.set_xlim(88.0, 92.75); ins.set_ylim(20.6, 26.7); ins.set_aspect(1.08)
    ins.set_xticks([]); ins.set_yticks([]); ins.set_facecolor("white")
    for s in ins.spines.values():
        s.set_visible(True); s.set_color(MUTED); s.set_linewidth(0.4)

    # ---- (b) hourly intensity, gauge-corrected ----
    hits = {57.4: [], 200.0: []}; plabs = []
    for ax in (a, b):
        ax.axvspan(*win, color=SLIDE_T, lw=0, zorder=0)
        grid(ax)
    for lab_, col_raw, colr in prods:
        raw = d[col_raw].loc[t0 - pd.Timedelta(hours=24):t1]
        K = 343.0 / raw.rolling(24, min_periods=1).sum().max()                     # gauge anchor (A1)
        corr = raw * K
        a.step(corr.index, corr.values, where="post", color=colr, lw=0.9)
        r24 = corr.rolling(24, min_periods=1).sum(); r24raw = raw.rolling(24, min_periods=1).sum()
        b.plot(r24raw.index, r24raw.values, color=colr, lw=0.7, ls=(0, (2.5, 1.8)), alpha=0.55)
        b.plot(r24.index, r24.values, color=colr, lw=1.6, solid_capstyle="round")
        plabs.append(Line2D([], [], color=colr, lw=1.6, label=f"{lab_} (×{K:.2f} to gauge)"))
        for val in hits:
            h = r24[r24 >= val].index.min(); hits[val].append(h)
            b.plot([h], [val], marker="o", ms=4.6, color=colr, mec="white", mew=0.8, zorder=5)
    a.set_ylim(0, 40); a.set_yticks([0, 20, 40])
    a.set_ylabel("Hourly rain (mm)")
    a.tick_params(axis="x", labelbottom=False)
    a.text(win[0] + (win[1] - win[0]) / 2, 39, "failures", ha="center", va="top", fontsize=6.3, color=SLIDE,
           fontweight="bold")
    heading(a, "June 2017 storm at the Rangamati failure cluster, gauge-corrected")
    letter(a, "b", x=-0.075)

    # ---- (c) rolling 24-h total, thresholds and how much warning each would have given ----
    for val, lab_ in [(57.4, "empirical threshold 57.4 mm"), (200, "installed threshold 200 mm")]:
        b.axhline(val, color=INK2, lw=0.6, ls=(0, (1, 1.6)), zorder=1)
        b.text(t0 + pd.Timedelta(hours=1), val + 6, lab_, fontsize=6.2, color=INK2, va="bottom")
        h0, h1 = min(hits[val]), max(hits[val])
        l0, l1 = [(win[0] - h).total_seconds() / 3600 for h in (h1, h0)]
        y = val + (26 if val < 100 else -26)
        b.annotate("", xy=(win[0], y), xytext=(h0, y),
                   arrowprops=dict(arrowstyle="-|>", lw=0.8, color=INK, mutation_scale=6, shrinkA=0, shrinkB=0))
        b.plot([h0, h0], [val, y], color=INK, lw=0.5)
        b.text(h0 + (win[0] - h0) / 2, y + (5 if val < 100 else -5),
               f"{math.floor(l0)}–{math.ceil(l1)} h lead", fontsize=6.5, fontweight="bold", color=INK,
               ha="center", va="bottom" if val < 100 else "top", path_effects=HALO)
    b.set_ylabel("Rolling 24-h rain (mm)"); b.set_ylim(0, 400)
    b.set_xlim(t0, t1)
    b.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    b.xaxis.set_major_formatter(mdates.DateFormatter("%d Jun\n%H:%M"))
    b.set_xlabel("Bangladesh Standard Time (UTC+6)")
    b.legend(handles=plabs + [Line2D([], [], color=INK2, lw=1.6, label="gauge-corrected"),
                      Line2D([], [], color=INK2, lw=0.7, ls=(0, (2.5, 1.8)), label="uncorrected")],
             loc="upper left", frameon=False, handlelength=1.8)
    letter(b, "c", x=-0.075)
    save(fig, "fig1_june2017_hourly")
    return {v: [str(x) for x in h] for v, h in hits.items()}


# ======================================================================================
# Figure 2 - correcting the reanalysis, and what each threshold would cost
# ======================================================================================
def fig2():
    res = ROOT / "data" / "results"
    g = json.loads((res / "event2026.json").read_text())["gauge_check"]
    sk = json.loads((res / "skill.json").read_text())
    tq = pd.read_csv(res / "qm_transfer.csv")
    fig, (a, b) = plt.subplots(1, 2, figsize=(W2, 2.75), gridspec_kw={"width_ratios": [1, 1.45], "wspace": 0.28})
    fig.subplots_adjust(left=0.07, right=0.99, top=0.9, bottom=0.16)
    # ---- (a) gauge check ----
    era = np.array([r["era5land_mm"] for r in g["pairs"]]); gau = np.array([r["gauge_mm"] for r in g["pairs"]])
    xs = np.linspace(0, 130, 50)
    a.fill_between(xs, xs, 2.95 * xs, color=BAND, lw=0, zorder=0)
    a.plot(xs, xs, color=MUTED, lw=0.6, ls=(0, (1, 1.5)))
    a.plot(xs, 2.95 * xs, color=INK, lw=0.9)
    xq = tq.era5land_mm.clip(upper=130)
    a.plot(xq, np.interp(xq, tq.era5land_mm, tq.gauge_mm), color=RAIN, lw=1.1, ls=(0, (4, 1.6)))
    a.scatter(era, gau, s=20, color=SLIDE, edgecolor="white", lw=0.6, zorder=3)
    a.text(36, 2.95 * 36 + 4, "×2.95\n2017 anchor", fontsize=6.2, color=INK, ha="right", va="bottom")
    a.text(127, 236, "quantile\nmapping", fontsize=6.2, color=RAIN, ha="right", va="top")
    a.text(127, 132, "1:1", fontsize=6.2, color=MUTED, ha="right", va="bottom")
    a.text(4, 372, f"10 BMD gauge totals, 6–9 July 2026\nmedian ratio {g['median_ratio']:.2f}",
           fontsize=6.3, color=INK, va="top")
    a.set_xlim(0, 130); a.set_ylim(0, 380)
    a.set_xlabel("ERA5-Land 24-h total (mm)"); a.set_ylabel("Gauge 24-h total (mm)")
    grid(a, "both")
    heading(a, "Reanalysis sees a third of the gauge rain")
    letter(a, "a", x=-0.13)
    # ---- (b) detection against alarm days ----
    note = {("flat", "installed_24h_200"): (8, -2, "left"), ("qm", "installed_24h_200"): (-8, 2, "right"),
            ("flat", "empirical_24h_57.4"): (-8, 4, "right"), ("qm", "empirical_24h_57.4"): (8, -6, "left")}
    for mode, col, lab in [("qm", RAIN, "quantile-mapped"), ("flat", INK, f"flat factor {g['median_ratio']:.2f}")]:
        sw = sk["sweep_24h"][mode]
        x = [r["alarm_days_mean"] for r in sw]; y = [r["pod"] for r in sw]
        b.plot(x, y, color=col, lw=1.0, marker="o", ms=2.2, label=lab, zorder=2)
        for tn, thr, mk in [("empirical_24h_57.4", 57.4, "s"), ("installed_24h_200", 200, "D")]:
            ad = np.mean(list(sk["alarm_days_per_season_1979_2025"][mode][tn].values()))
            pod = sk["detection"][mode][tn]["pod_all"]
            b.scatter([ad], [pod], s=34, marker=mk, facecolor="white", edgecolor=col, lw=1.2, zorder=4)
            dx, dy, ha = note[(mode, tn)]
            b.annotate(f"{ad:.1f} d, {100 * pod:.0f}%", (ad, pod), xytext=(dx, dy), textcoords="offset points",
                       fontsize=6.2, color=INK, ha=ha, va="center", path_effects=HALO)
    b.set_xscale("log"); b.set_xlim(0.15, 90); b.set_ylim(0, 1)
    b.set_xticks([0.2, 0.5, 1, 2, 5, 10, 20, 50]); b.set_xticklabels(["0.2", "0.5", "1", "2", "5", "10", "20", "50"])
    b.set_yticks([0, 0.25, 0.5, 0.75, 1]); b.set_yticklabels(["0", "25", "50", "75", "100"])
    b.scatter([], [], marker="s", facecolor="white", edgecolor=INK2, label="empirical 57.4 mm")
    b.scatter([], [], marker="D", facecolor="white", edgecolor=INK2, label="installed 200 mm")
    b.legend(frameon=False, loc="upper left", handletextpad=0.4)
    b.set_xlabel("Days per May–October season the threshold fires (1979–2025 mean)")
    b.set_ylabel(f"Landslide district-days detected (%, n = {sk['detection']['qm']['empirical_24h_57.4']['n']})")
    grid(b, "both")
    heading(b, "Detection rises only with many more alarm days")
    letter(b, "b", x=-0.09)
    save(fig, "fig2_skill")


# ======================================================================================
# Figure 3 - three events, four lanes
# ======================================================================================
EVENTS = [
    # (time, label). Vertical placement is computed by measuring the rendered text, so labels
    # are never hand-positioned and cannot silently collide when a label is edited.
    dict(name="June 2017", start="2017-06-08", end="2017-06-16",
         flood=[("2017-06-12 12:00", "Matamuhuri above\ndanger level", "right"),                   # F1
                ("2017-06-13 12:00", "Sangu peak\n+135 cm", "left")],                             # F1
         slide=[("2017-06-13 05:00", "257 dated failures;\n~150–170 deaths")],            # Q2, Y4
         warn=[], warn_none="no dedicated warning\nfor either hazard"),                     # F3, G1
    dict(name="August 2023", start="2023-08-02", end="2023-08-11",
         flood=[("2023-08-07 12:00", "Sangu +283 cm")],                                    # H1
         slide=[("2023-08-08 12:00", "10 deaths, flood\nand landslides")],                # R4
         warn=[("2023-08-07 07:00", "FFWC bulletin (24–48 h);\nBMD landslide alert"),     # H2, H3
               ("2023-08-10 12:00", "33,000\nsheltered")]),
    dict(name="July 2026", start="2026-07-03", end="2026-07-18",
         flood=[("2026-07-08 09:00", "Sangu +96 cm")],                                     # A6
         slide=[("2026-07-06 02:00", "8 killed,\ncamps"),                                 # I8
                ("2026-07-08 14:00", "5+ killed,\nCamp 5"),                               # L6
                ("2026-07-12 12:00", "Rangamati:\n126 incidents,\n1 death")],            # I7
         warn=[("2026-07-05 09:00", "forecast;\nresponse activated"),                     # I4
               ("2026-07-07 13:00", "Bulletin\n05/2026"),                                 # I2
               ("2026-07-12 12:00", "38,422\nsheltered")]),                               # I5
]

LANE_LEVELS = [0.68, 0.43, 0.19]   # text top, in axis fraction, per stacking level
DOT_Y, LAB_FS, PAD = 0.87, 6.2, 0.015


def _place_lane(fig, a, items, col, t0, t1):
    """Draw each mark with its label, stacking labels only as far down as they must go."""
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    placed = []
    for it in items:
        t, lab = it[:2]
        x = pd.Timestamp(t)
        frac = (x - t0) / (t1 - t0)
        ha = it[2] if len(it) > 2 else ("left" if frac < 0.17 else ("right" if frac > 0.83 else "center"))
        probe = a.text(x, 0.5, lab, ha=ha, va="top", fontsize=LAB_FS, linespacing=1.12)
        w = probe.get_window_extent(renderer=rend).transformed(a.transAxes.inverted()).width
        probe.remove()
        x0, x1 = {"center": (frac - w / 2, frac + w / 2), "left": (frac, frac + w), "right": (frac - w, frac)}[ha]
        lvl = 0
        while any(l == lvl and not (x1 + PAD < q0 or x0 - PAD > q1) for l, q0, q1 in placed):
            lvl += 1
        lvl = min(lvl, len(LANE_LEVELS) - 1)
        placed.append((lvl, x0, x1))
        ty = LANE_LEVELS[lvl]
        a.plot([x, x], [DOT_Y - 0.08, ty + 0.04], color=col, lw=0.6, alpha=0.7, zorder=1)
        a.plot([x], [DOT_Y], marker="o", ms=6, color=col, mec="white", mew=1.0, zorder=3)
        a.text(x, ty, lab, ha=ha, va="top", fontsize=LAB_FS, color=INK, linespacing=1.12, zorder=4,
               path_effects=HALO)


def fig3():
    fig, axes = plt.subplots(4, 3, figsize=(W2, 5.0), sharex="col",
                             gridspec_kw={"height_ratios": [1.35, 1.0, 1.5, 1.3], "hspace": 0.0, "wspace": 0.08})
    fig.subplots_adjust(left=0.115, right=0.99, top=0.93, bottom=0.08)
    lanes = [("Rain\n(mm per day)", RAIN), ("Flash flood", FLOOD), ("Landslides", SLIDE), ("Warning\nand action", WARN)]
    for c, ev in enumerate(EVENTS):
        t0, t1 = pd.Timestamp(ev["start"]), pd.Timestamp(ev["end"]) + pd.Timedelta(days=1)
        day = era5land_point(*BANDARBAN, ev["start"], ev["end"] + " 23:00").resample("D").sum()
        ax = axes[0, c]
        ax.bar(day.index + pd.Timedelta(hours=12), day.values, width=0.78, color=RAIN, linewidth=0)
        ax.set_ylim(0, 130); ax.set_yticks([0, 50, 100])
        ax.set_title(ev["name"], fontsize=8, fontweight="bold", color=INK, loc="left", pad=6)
        grid(ax); ax.tick_params(axis="x", length=0)
        if c:
            ax.set_yticklabels([]); ax.tick_params(axis="y", length=0)
        for r in range(4):
            axes[r, c].set_xlim(t0, t1)
        # after the first warning, every lane is shaded: what followed happened under warning
        first = min((pd.Timestamp(w[0]) for w in ev["warn"]), default=None)
        for r, key in [(1, "flood"), (2, "slide"), (3, "warn")]:
            a = axes[r, c]; col = lanes[r][1]
            a.set_ylim(0, 1); a.set_yticks([]); a.spines["left"].set_visible(False)
            a.spines["bottom"].set_color(GRID if r < 3 else INK2)
            if r < 3:
                a.tick_params(axis="x", length=0)
            if first is not None:
                a.axvspan(first, t1, color="#fdf5e1", lw=0, zorder=0)
                a.axvline(first, color=WARN, lw=0.6, alpha=0.8, zorder=0)
            _place_lane(fig, a, ev[key], col, t0, t1)
            if key == "warn" and ev.get("warn_none"):
                a.add_patch(Rectangle((0.04, 0.2), 0.92, 0.66, transform=a.transAxes, facecolor="none",
                                      edgecolor=MUTED, lw=0.6, ls=(0, (2, 1.5))))
                a.text(0.5, 0.53, ev["warn_none"], transform=a.transAxes, ha="center", va="center",
                       fontsize=6.5, color=INK2, style="italic", linespacing=1.2)
        if first is not None:
            axes[3, c].text(first, 0.035, " warning issued →", fontsize=5.6, color="#9a6a00", ha="left",
                            va="bottom", transform=axes[3, c].get_xaxis_transform())
        axes[3, c].xaxis.set_major_locator(mdates.DayLocator(interval=2))
        axes[3, c].xaxis.set_major_formatter(mdates.DateFormatter("%d"))
    for r, (lab, col) in enumerate(lanes):
        axes[r, 0].set_ylabel(lab, fontsize=6.8, color=INK, rotation=0, ha="right", va="center", labelpad=8)
    for r in (1, 2, 3):
        axes[r, 0].text(-0.035, 0.87, "●", transform=axes[r, 0].transAxes, color=lanes[r][1], fontsize=7,
                        ha="right", va="center")
    fig.text(0.55, 0.025, "Day of month (rain: ERA5-Land at Bandarban, uncorrected)", ha="center", fontsize=6.8, color=INK2)
    save(fig, "fig3_three_events")


# ======================================================================================
# Figure 4 - Rangamati 2017 vs 2026, and where the 2026 deaths fell
# ======================================================================================
# The three settings whose landslide deaths can be separated from other causes; they sum to the
# 21 of Section 5.1. Rangamati's single 2026 death is shown apart: the source does not state its
# cause, so it is not an identifiable landslide death.
RESIDUAL = [("Rohingya camps", 13, None),            # L3: 8 on 6 Jul + >=5 Camp 5, 8 Jul
            ("Cox's Bazar\nhost community", 5, (21.47, 91.99)),   # I9 (district total; placed at the town)
            ("Chattogram", 3, (22.36, 91.83))]        # L3 (placed at the city)


def fig4():
    adm, camps, _ = layers()
    fig = plt.figure(figsize=(W2, 3.3))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.12, 1.0], wspace=0.10, left=0.03, right=0.99, top=0.9, bottom=0.02)
    left = gs[0].subgridspec(2, 2, height_ratios=[0.26, 1], hspace=0.08, wspace=0.1)
    m = fig.add_subplot(gs[1]); m.set_anchor("W")

    # ---- (a) same gauge, comparable rain; district deaths as one dot each ----   [Q2, Y4, I7, A1, A6]
    cols = [("June 2017", 343, 121), ("July 2026", 287, 1)]
    n = 11
    for j, (yr, rain, dead) in enumerate(cols):
        r = fig.add_subplot(left[0, j]); u = fig.add_subplot(left[1, j])
        r.barh([0], [400], height=0.42, color=BAND, lw=0, zorder=0)
        r.barh([0], [rain], height=0.42, color=RAIN, lw=0)
        r.set_xlim(0, 400); r.set_ylim(-0.6, 1.2); r.axis("off")
        r.text(0, 0.55, yr, fontsize=8, fontweight="bold", color=INK, va="bottom")
        r.text(rain + 8, 0, f"{rain} mm", fontsize=6.5, color=INK, va="center")
        r.text(0, -0.5, "peak 24-h rain, Rangamati gauge", fontsize=5.8, color=INK2, va="top")
        xx = np.arange(dead) % n; yy = -(np.arange(dead) // n)
        u.scatter(xx, yy, s=17, color=SLIDE, lw=0)
        u.set_xlim(-0.7, n - 0.3); u.set_ylim(-n + 0.4, 2.2); u.set_aspect("equal"); u.axis("off")
        u.text(-0.5, 1.0, f"{dead}", fontsize=13, fontweight="bold", color=SLIDE, va="bottom")
        u.text(-0.5 + (2.6 if dead > 9 else 1.0), 1.15, ("deaths" if dead > 1 else "death") + " in the district",
               fontsize=6.5, color=INK, va="bottom")
        if dead == 1:
            u.text(1.0, 0, "cause not stated\nin the source", fontsize=5.8, color=INK2, va="center")
        if j == 0:
            letter(r, "a", x=-0.02, y=1.0)
    # ---- (b) where the identifiable 2026 landslide deaths fell ----       [L3, I7, I9]
    bounds = (91.62, 20.85, 92.62, 22.95)
    basemap(m, adm, bounds)
    camps.plot(ax=m, color=INK, lw=0, zorder=3)
    cc = camps.geometry.union_all() if hasattr(camps.geometry, "union_all") else camps.geometry.unary_union
    clon, clat = cc.centroid.x, cc.centroid.y
    pts = [(lab, v, (clat, clon) if xy is None else xy) for lab, v, xy in RESIDUAL]
    scale = 30                                       # marker area per death, points^2
    for lab, v, (la, lo) in pts:
        m.scatter(lo, la, s=scale * v, color=SLIDE, alpha=0.8, edgecolor="white", lw=0.8, zorder=5)
        m.text(lo, la, str(v), ha="center", va="center", fontsize=7 if v > 4 else 6, fontweight="bold",
               color="white", zorder=6)
    m.text(clon - 0.12, clat, "Rohingya\ncamps", ha="right", va="center", fontsize=6.3, color=INK,
           zorder=6, path_effects=HALO)
    m.text(91.99 - 0.09, 21.47 + 0.02, "Cox's Bazar\nhost community", ha="right", va="center", fontsize=6.3,
           color=INK, zorder=6, path_effects=HALO)
    m.text(91.83, 22.36 + 0.08, "Chattogram", ha="center", va="bottom", fontsize=6.3, color=INK,
           zorder=6, path_effects=HALO)
    # Rangamati: many incidents, one death of unstated cause -> hollow, not counted     [I7]
    m.scatter(RANGAMATI[1], RANGAMATI[0], s=scale, facecolor="white", edgecolor=SLIDE, lw=1.0, zorder=5)
    m.text(RANGAMATI[1] + 0.06, RANGAMATI[0] + 0.02, "Rangamati\n126 incidents,\n1 death,\ncause not stated",
           ha="left", va="center", fontsize=5.8, color=INK, zorder=6, path_effects=HALO)
    scalebar(m, 92.32, 20.93)
    heading(m, "Identifiable landslide deaths, July 2026: 13 of 21 in the camps")
    letter(m, "b", x=-0.02, y=1.0)
    save(fig, "fig4_rangamati")


# ======================================================================================
# Figure 5 - annual maxima 1950-2025
# ======================================================================================
def fig5():
    """Annual maximum rolling 24-h ERA5-Land rainfall, 1950-2025, from data/scripts/climatology.py.
    Uncorrected values, so only ranks and relative changes are interpreted. Registers W2-W6."""
    from climatology import mann_kendall
    am = pd.read_csv(ROOT / "data" / "results" / "climatology_annual_maxima.csv")
    am = am[am.window == "24h"]
    fig, axes = plt.subplots(1, 2, figsize=(W2, 2.55), sharey=True)
    fig.subplots_adjust(wspace=0.06, top=0.88, bottom=0.15, left=0.075, right=0.99)
    for a, (pt, lab) in zip(axes, [("Rangamati", "a"), ("Bandarban", "b")]):
        s = am[am.point == pt].set_index("year").annual_max_mm
        full, part = s[s.index <= 2025], s[s.index > 2025]
        a.axvspan(1949.5, 1978.5, color=BAND, lw=0, zorder=0)
        a.text(1964, 10, "before satellite data\nentered the reanalysis", ha="center", va="bottom",
               fontsize=5.8, color=INK2, linespacing=1.15, zorder=6)
        a.vlines(full.index, 0, full.values, color=RAIN, lw=0.5, alpha=0.35, zorder=2)
        a.scatter(full.index, full.values, s=8, color=RAIN, lw=0, zorder=3)
        for lo, hi in [(1950, 1978), (1979, 2025)]:
            md = full.loc[lo:hi].median()
            a.plot([lo, hi], [md, md], color=INK, lw=1.3, solid_capstyle="butt", zorder=4)
            a.text(lo + 0.5, md + 9, f"median {md:.0f} mm", fontsize=6, color=INK,
                   ha="left", va="bottom", zorder=6, path_effects=HALO)
        x = full.loc[1979:]; mk = mann_kendall(x.values)
        yrs = np.array(x.index); bslope = mk["sen_slope_per_year"]
        c0 = np.median(x.values - bslope * (yrs - yrs[0]))
        a.plot(yrs, c0 + bslope * (yrs - yrs[0]), color=SLIDE, lw=1.1, zorder=4)
        a.text(1981, 385, f"1979–2025 trend {1000 * bslope / x.median():+.0f}% per decade (p = {mk['p']:.2f})",
               fontsize=6.2, color=SLIDE, ha="left", va="top", zorder=6, path_effects=HALO)
        for yr in (2017, 2023):
            a.scatter([yr], [s[yr]], s=30, facecolor="none", edgecolor=INK, lw=0.9, zorder=5)
            a.annotate(str(yr), (yr, s[yr]), xytext=(-14, 16 if yr == 2017 else -14), textcoords="offset points",
                       ha="center", va="center", fontsize=6, color=INK, zorder=6, path_effects=HALO,
                       arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.5, shrinkA=0, shrinkB=3))
        if len(part):
            a.scatter(part.index, part.values, s=30, facecolor="none", edgecolor=MUTED, lw=0.9, ls=(0, (1, 1)), zorder=5)
        heading(a, pt)
        letter(a, lab, x=-0.02 if lab == "b" else -0.1)
        a.set_xlim(1948, 2029); a.set_ylim(0, 400); a.set_yticks([0, 100, 200, 300, 400])
        a.set_xlabel("Year")
        grid(a)
    axes[0].set_ylabel("Annual maximum 24-h rain (mm)")
    save(fig, "fig5_climatology")


# ======================================================================================
# Figure 6 - slope model: timing in 2017, and the 2026 storm on the same slopes
# ======================================================================================
MRES = ROOT / "modelling" / "results"


def fig6():
    d = pd.read_csv(MRES / "ensemble_2017.csv")
    adm_ = d[d.share_hill_fs_lt1_prestorm < 0.05]
    adm_ = adm_[adm_.share_fail_cells_fs_lt1_final > adm_.share_fail_fs_lt1_prestorm]   # as analyse_ensemble.py
    t = pd.to_datetime(adm_.median_first_fs_lt1).dropna()
    r = pd.read_csv(MRES / "replay2026_2017.csv")
    fit = r[r.share_fail_triggered_in_window > 0]
    x, y = 100 * fit.share_hill_cells_fs_lt1_final, 100 * fit.r26_share_hill_cells_fs_lt1_final
    n_up = int((y > x).sum())
    assert (len(t), len(fit), n_up) == (442, 97, 67), (len(t), len(fit), n_up)       # 06b_models.tex

    fig, (a, b) = plt.subplots(1, 2, figsize=(W2, 2.7), gridspec_kw={"width_ratios": [1.45, 1], "wspace": 0.3})
    fig.subplots_adjust(left=0.07, right=0.985, top=0.88, bottom=0.2)
    w0, w1 = pd.Timestamp("2017-06-13 02:30"), pd.Timestamp("2017-06-13 11:00")
    bins = pd.date_range("2017-06-11 12:00", "2017-06-13 18:00", freq="3h")
    cnt, _ = np.histogram(t, bins=bins)
    inwin = [(lo >= w0 - pd.Timedelta(hours=3)) and (lo < w1) for lo in bins[:-1]]
    a.axvspan(w0, w1, color=SLIDE_T, lw=0, zorder=0)
    a.bar(bins[:-1], cnt, width=pd.Timedelta(hours=3) * 0.86, align="edge",
          color=[SLIDE if i else "#b9b7b0" for i in inwin], lw=0, zorder=2)
    a.text(w0 + (w1 - w0) / 2, 0.98, "observed\nfailures", transform=a.get_xaxis_transform(), ha="center",
           va="top", fontsize=6.3, color=SLIDE, fontweight="bold")
    med = t.median(); lead = (w0 - med).total_seconds() / 3600
    assert abs(lead - 23.5) < 0.01, lead                                              # 06b_models.tex
    a.axvline(med, color=INK, lw=0.8, ls=(0, (3, 1.5)), zorder=3)
    a.text(med + pd.Timedelta(hours=1.5), 0.97, f"median of {len(t)} runs,\n{lead:.1f} h before the\nfirst reported failure",
           transform=a.get_xaxis_transform(), fontsize=6.3, color=INK, va="top", path_effects=HALO, zorder=4)
    a.set_xlim(bins[0], bins[-1]); a.set_ylabel("TRIGRS runs")
    a.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    a.xaxis.set_major_formatter(mdates.DateFormatter("%d Jun\n%H:%M"))
    grid(a)
    heading(a, "Modelled first failure, June 2017 (BST)")
    letter(a, "a", x=-0.08)

    hi = float(max(x.max(), y.max())) * 1.06
    b.fill_between([0, hi], [0, hi], [hi, hi], color=SLIDE_T, lw=0, zorder=0)
    b.plot([0, hi], [0, hi], color=INK2, lw=0.6, ls=(0, (3, 2)))
    for prod, col, mk, lab in (("era5land", RAIN, "o", "ERA5-Land"), ("imerg", WARN, "D", "IMERG")):
        mm = fit["product"] == prod
        b.scatter(x[mm], y[mm], s=11 if mk == "o" else 9, marker=mk, color=col, alpha=0.85, edgecolor="white",
                  lw=0.3, label=lab, zorder=3)
    b.text(0.04 * hi, 0.93 * hi, f"more unstable in 2026\n{n_up} of {len(fit)} runs", fontsize=6.3, color=SLIDE,
           fontweight="bold", va="top")
    b.text(0.97 * hi, 0.05 * hi, "less unstable", fontsize=6.2, color=INK2, ha="right")
    b.set_xlim(0, hi); b.set_ylim(0, hi); b.set_aspect("equal")
    b.set_xlabel("Unstable hillslope, 2017 (%)"); b.set_ylabel("Unstable hillslope, 2026 (%)")
    b.legend(frameon=False, loc="lower right", bbox_to_anchor=(1.0, 0.1), handletextpad=0.2)
    heading(b, "Runs that fit 2017 timing, replayed with 2026 rain")
    letter(b, "b", x=-0.2)
    save(fig, "fig6_models")


# ======================================================================================
# Supplementary Figure 1 - the Sangu at Bandarban town: flood model and GloFAS
# ======================================================================================
FLOOD_EV = {"2017": ("June 2017", "2017-06-10", "2017-06-17", "2017-06-13"),
            "2023": ("August 2023", "2023-08-01", "2023-08-13", "2023-08-07"),
            "2026": ("July 2026", "2026-07-03", "2026-07-12", "2026-07-08")}


def figS1():
    """LISFLOOD-FP depth at the town cell (reference run, range of the eight sensitivity runs) above
    GloFAS v5.0 daily discharge, each on its own axis. Registers M10, M11."""
    g = pd.read_csv(MRES / "glofas_sangu.csv", index_col=0, parse_dates=True).q_m3s
    fig, axs = plt.subplots(2, 3, figsize=(W2, 3.4), sharex="col", sharey="row",
                            gridspec_kw={"height_ratios": [1.5, 1], "hspace": 0.12, "wspace": 0.08})
    fig.subplots_adjust(left=0.08, right=0.99, top=0.9, bottom=0.12)
    for c, (ev, (name, a0, a1, obs)) in enumerate(FLOOD_EV.items()):
        top, bot = axs[0, c], axs[1, c]
        ref = pd.read_csv(MRES / "lisflood" / f"{ev}_fr1" / "town_depth.csv", index_col=0, parse_dates=True).depth_m
        sens = [pd.read_csv(f, index_col=0, parse_dates=True).depth_m
                for f in sorted((MRES / "lisflood").glob(f"{ev}_s_*/town_depth.csv"))]
        o = pd.Timestamp(obs)
        for ax in (top, bot):
            ax.axvspan(o, o + pd.Timedelta(days=1), color="#d6f1e6", lw=0, zorder=0)
            grid(ax)
        if sens:
            env = pd.concat([s.reindex(ref.index, method="nearest", tolerance=pd.Timedelta("10min")) for s in sens], axis=1)
            top.fill_between(ref.index, env.min(1), env.max(1), color=FLOOD, alpha=0.25, lw=0)
        top.plot(ref.index, ref.values, color=FLOOD, lw=1.2)
        gg = g.loc[a0:a1]
        bot.step(gg.index + pd.Timedelta(hours=6), gg.values, where="post", color=RAIN, lw=1.0)
        top.set_title(name, fontsize=8, fontweight="bold", loc="left", color=INK, pad=4)
        top.text(o + pd.Timedelta(hours=12), 16.3, "recorded\npeak day", ha="center", va="top", fontsize=5.8,
                 color="#0f7a53")
        bot.set_xlim(pd.Timestamp(a0), pd.Timestamp(a1))
        bot.xaxis.set_major_locator(mdates.DayLocator(interval=2 if ev != "2023" else 3))
        bot.xaxis.set_major_formatter(mdates.DateFormatter("%d"))
        letter(top, "abc"[c], x=-0.04 if c else -0.16)
    axs[0, 0].set_ylim(0, 17); axs[0, 0].set_ylabel("Modelled depth\nat town (m)")
    axs[1, 0].set_ylim(0, 900); axs[1, 0].set_ylabel("GloFAS discharge\n(m$^3$ s$^{-1}$)")
    axs[0, 0].legend(handles=[Line2D([], [], color=FLOOD, lw=1.2, label="reference run"),
                              plt.Rectangle((0, 0), 1, 1, color=FLOOD, alpha=0.25, lw=0, label="eight sensitivity runs")],
                     loc="lower right", frameon=False, fontsize=5.8, handlelength=1.4)
    fig.text(0.54, 0.02, "Day of month (BST; GloFAS days 06:00 to 06:00)", ha="center", fontsize=6.8, color=INK2)
    save(fig, "figS1_flood")


if __name__ == "__main__":
    only = set(sys.argv[1:])
    fns = {"1": fig1, "2": fig2, "3": fig3, "4": fig4, "5": fig5, "6": fig6, "S1": figS1}
    out = {}
    for k, fn in fns.items():
        if not only or k in only:
            out[k] = fn()
    print(f"figures written to {OUT}; crossings {out.get('1')}")
