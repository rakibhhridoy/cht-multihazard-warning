#!/usr/bin/env python3
"""Build the four manuscript figures.

File names follow the rendered figure numbers: fig1 = June 2017 hourly (Section 3),
fig2 = the three events (Section 4), fig3 = Rangamati and the residual (Section 5), fig4 = the 1950-2025
rainfall climatology (Section 5).
The builder functions keep their original names.

Rainfall: ERA5-Land hourly from the Copernicus CDS and IMERG V07 half-hourly, processed by
data/scripts/rain_analysis.py (de-accumulation, local time, gauge anchoring).
Event facts are taken from review/claims-register.md (IDs noted inline).
"""
import json, math, urllib.request, urllib.parse, time
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as pe

# The same file runs from the public repository (figures/) and from the manuscript tree
# (manuscript/figures/), so the project root is the nearest ancestor holding data/.
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "data" / "scripts").is_dir())
CACHE = ROOT / "data" / "figdata"; CACHE.mkdir(parents=True, exist_ok=True)
OUT = Path(__file__).resolve().parent

# ---- validated palette (dataviz reference, light, surface #ffffff) -----------------------
RAIN, SLIDE, FLOOD, WARN = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, MUTED, GRID, BAND = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#f0efec"
# ---- typography: match the manuscript body face (Latin Modern Roman) ---------------------
# Latin Modern ships with TeX Live. If it is not on this machine the figures still build, in
# the nearest serif, and only the letterforms differ.
def _register_latin_modern():
    import glob
    from matplotlib import font_manager as fm
    pats = ["/usr/local/texlive/*/texmf-dist/fonts/opentype/public/lm/lmroman*.otf",
            "/opt/homebrew/Cellar/texlive/*/share/texmf-dist/fonts/opentype/public/lm/lmroman*.otf",
            "/usr/share/texmf/fonts/opentype/public/lm/lmroman*.otf",
            "/usr/share/texlive/texmf-dist/fonts/opentype/public/lm/lmroman*.otf"]
    files = [f for pat in pats for f in glob.glob(pat)]
    for f in files:
        try: fm.fontManager.addfont(f)
        except Exception: pass
    return bool(files) and "Latin Modern Roman" in {f.name for f in fm.fontManager.ttflist}

SERIF = "Latin Modern Roman" if _register_latin_modern() else "DejaVu Serif"

plt.rcParams.update({
    "font.family": "serif", "font.serif": [SERIF, "DejaVu Serif"],
    "mathtext.fontset": "cm",
    "font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False,
    "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "savefig.facecolor": "white", "figure.facecolor": "white",
})

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

import sys
sys.path.insert(0, str(ROOT / "data" / "scripts"))
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
# Figure 1 - three events, four lanes
# ======================================================================================
EVENTS = [
    # (time, label). Vertical placement is computed in fig1() by measuring the rendered text,
    # so labels are never hand-positioned and cannot silently collide when a label is edited.
    dict(name="June 2017", start="2017-06-08", end="2017-06-16",
         flood=[("2017-06-12 12:00", "Matamuhuri above\ndanger level"),                   # F1
                ("2017-06-13 12:00", "Sangu peak\n+135 cm")],                             # F1
         slide=[("2017-06-13 05:00", "257 dated failures;\n~150-170 deaths")],            # Q2, Y4
         warn=[], warn_none="no dedicated warning\nfor either hazard"),                     # F3, G1
    dict(name="August 2023", start="2023-08-02", end="2023-08-11",
         flood=[("2023-08-07 12:00", "Sangu +283 cm")],                                    # H1
         slide=[("2023-08-08 12:00", "10 deaths, flood\nand landslides")],                # R4
         warn=[("2023-08-07 07:00", "FFWC bulletin (24-48 h);\nBMD landslide alert"),     # H2, H3
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

LANE_LEVELS = [0.70, 0.45, 0.21]   # text top, in axis fraction, per stacking level
DOT_Y, LAB_FS, PAD = 0.88, 6.8, 0.015

def _place_lane(fig, a, items, col, t0, t1):
    """Draw each mark with its label, stacking labels only as far down as they must go.

    Text width is measured from the actual renderer, so a label that is edited later cannot
    quietly overlap its neighbour; it drops to the next free level instead.
    """
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    placed = []                                   # (level, x0, x1) in axis fraction
    for t, lab in items:
        x = pd.Timestamp(t)
        frac = (x - t0) / (t1 - t0)
        ha = "left" if frac < 0.17 else ("right" if frac > 0.83 else "center")
        probe = a.text(x, 0.5, lab, ha=ha, va="top", fontsize=LAB_FS, linespacing=1.12)
        w = probe.get_window_extent(renderer=rend).transformed(a.transAxes.inverted()).width
        probe.remove()
        x0, x1 = {"center": (frac - w / 2, frac + w / 2),
                  "left":   (frac, frac + w),
                  "right":  (frac - w, frac)}[ha]
        lvl = 0
        while any(l == lvl and not (x1 + PAD < q0 or x0 - PAD > q1) for l, q0, q1 in placed):
            lvl += 1
        lvl = min(lvl, len(LANE_LEVELS) - 1)
        placed.append((lvl, x0, x1))
        ty = LANE_LEVELS[lvl]
        a.plot([x, x], [DOT_Y - 0.09, ty + 0.05], color=col, lw=0.6, alpha=0.55, zorder=1)
        a.plot([x], [DOT_Y], marker="o", ms=7, color=col, mec="white", mew=1.1, zorder=3)
        # a white halo keeps a leader line that passes a neighbouring label legible
        a.text(x, ty, lab, ha=ha, va="top", fontsize=LAB_FS, color=INK, linespacing=1.12,
               zorder=4, path_effects=[pe.withStroke(linewidth=2.2, foreground="white")])

def fig1():
    fig, axes = plt.subplots(4, 3, figsize=(6.27, 6.4), sharex="col",
                             gridspec_kw={"height_ratios": [1.40, 1.10, 1.55, 1.35],
                                          "hspace": 0.08, "wspace": 0.10})
    lanes = [("Rainfall\n(mm per day)", RAIN), ("Flash flood", FLOOD),
             ("Landslides", SLIDE), ("Warning\nand action", WARN)]
    for c, ev in enumerate(EVENTS):
        t0, t1 = pd.Timestamp(ev["start"]), pd.Timestamp(ev["end"]) + pd.Timedelta(days=1)
        day = era5land_point(*BANDARBAN, ev["start"], ev["end"] + " 23:00").resample("D").sum()
        ax = axes[0, c]
        ax.bar(day.index + pd.Timedelta(hours=12), day.values, width=0.80, color=RAIN, linewidth=0)
        ax.set_ylim(0, 130)
        ax.set_title(ev["name"], fontsize=9.5, color=INK, loc="left", pad=5)
        ax.yaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
        ax.tick_params(axis="x", length=0)
        if c: ax.set_yticklabels([])
        for r in range(4):
            axes[r, c].set_xlim(t0, t1)
        for r, key in [(1, "flood"), (2, "slide"), (3, "warn")]:
            a = axes[r, c]; col = lanes[r][1]
            a.set_ylim(0, 1); a.set_yticks([]); a.spines["left"].set_visible(False)
            if r < 3:
                a.spines["bottom"].set_color(GRID); a.tick_params(axis="x", length=0)
            _place_lane(fig, a, ev[key], col, t0, t1)
            if key == "warn" and ev.get("warn_none"):
                a.text(t0 + (t1 - t0) * 0.5, 0.55, ev["warn_none"], ha="center", va="center",
                       fontsize=6.9, color=INK2, style="italic", linespacing=1.2)
        axes[3, c].xaxis.set_major_locator(mdates.DayLocator(interval=2))
        axes[3, c].xaxis.set_major_formatter(mdates.DateFormatter("%d"))
        axes[3, c].tick_params(axis="x", labelsize=7)
    for r, (lab, col) in enumerate(lanes):
        axes[r, 0].set_ylabel(lab, fontsize=7.5, color=INK2, rotation=0, ha="right",
                              va="center", labelpad=10)
    # the month is already in each panel title, so the axis carries only the day of month
    fig.text(0.5, 0.055, "Day of month", ha="center", fontsize=7.5, color=INK2)
    fig.savefig(OUT / "fig2_three_events.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig2_three_events.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

# ======================================================================================
# Figure 3 - Rangamati 2017 vs 2026, and where the 2026 residual fell
# ======================================================================================
# (a) the like-for-like district comparison under comparable forcing  [Q2, Y4, I7, A1, A6]
# (b) the identifiable landslide deaths of July 2026 by setting       [L3, I7, I9]
# The three settings whose landslide deaths can be separated from other causes; they sum to the
# 21 of Section 5.1. Rangamati's single 2026 death is deliberately absent: the source does not
# state its cause, so it is not an identifiable landslide death.
RESIDUAL = [("Rohingya camps,\nCox's Bazar", 13),   # L3: 8 on 6 Jul + >=5 Camp 5, 8 Jul
            ("Cox's Bazar\nhost community", 5),     # I9
            ("Chattogram", 3)]                       # L3

def fig2():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(6.27, 3.2),
                                   gridspec_kw={"width_ratios": [1, 1.15], "wspace": 0.42})

    # ---- (a) slope chart: one axis, same unit, direct labels only (no legend) ----
    x = [0, 1]
    for name, y, col, lab_dx, lab_dy in [("Slope failures", [160, 126], RAIN, 0.50, 11),
                                         ("Deaths",         [121, 1],   SLIDE, 0.56, 6)]:
        axL.plot(x, y, color=col, lw=2, solid_capstyle="round", zorder=2)
        axL.scatter(x, y, s=58, color=col, edgecolor="white", linewidth=1.2, zorder=3, clip_on=False)
        axL.text(-0.07, y[0], f"{y[0]}", ha="right", va="center", fontsize=8.5, color=INK)
        axL.text(1.07, y[1], f"{y[1]}", ha="left", va="center", fontsize=8.5, color=INK)
        axL.text(lab_dx, (y[0] + y[1]) / 2 + lab_dy, name, ha="center", va="bottom",
                 fontsize=7.5, color=col)
    axL.set_xticks(x)
    axL.set_xticklabels(["June 2017\nno dedicated warning", "July 2026\nwarning layer"], fontsize=7.5)
    axL.set_xlim(-0.40, 1.40); axL.set_ylim(0, 168); axL.set_ylabel("Count", fontsize=8)
    axL.yaxis.grid(True, color=GRID, linewidth=0.5); axL.set_axisbelow(True)
    axL.set_title("(a) Rangamati district", fontsize=8.5, color=INK, loc="left", pad=24)
    axL.text(0, 1.015, "peak 24-h rain: 332-343 mm at the Bandarban\ngauge in 2017, 287 mm at Rangamati in 2026",
             transform=axL.transAxes, fontsize=6.8, color=MUTED, va="bottom")

    # ---- (b) where the residual fell ----
    labs = [l for l, _ in RESIDUAL][::-1]
    vals = [v for _, v in RESIDUAL][::-1]
    ypos = range(len(vals))
    axR.barh(list(ypos), vals, height=0.5, color=SLIDE, linewidth=0)
    for i, v in enumerate(vals):
        axR.text(v + 0.35, i, str(v), va="center", ha="left", fontsize=8.5, color=INK)
    axR.set_yticks(list(ypos)); axR.set_yticklabels(labs, fontsize=7.5)
    axR.set_xlim(0, 15); axR.set_xlabel("Identifiable landslide deaths, July 2026", fontsize=8)
    axR.set_xticks([0, 5, 10, 15])          # deaths are counts, so the axis carries integers
    axR.xaxis.grid(True, color=GRID, linewidth=0.5); axR.set_axisbelow(True)
    axR.tick_params(axis="y", length=0)
    axR.set_title("(b) Where the residual fell", fontsize=8.5, color=INK, loc="left", pad=24)
    axR.text(0, 1.015, "at least 21 deaths are identifiable\nfrom the incident records",
             transform=axR.transAxes, fontsize=6.8, color=MUTED, va="bottom")

    fig.savefig(OUT / "fig3_rangamati.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig3_rangamati.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

# ======================================================================================
# Figure 3 - June 2017 hourly: intensity (top) and rolling 24-h total with thresholds (bottom)
# ======================================================================================
def fig3():
    d = pd.read_csv(ROOT / "data" / "results" / "june2017_hourly_rangamati.csv", index_col=0, parse_dates=True)
    prods = [("ERA5-Land", "era5land_raw", RAIN), ("IMERG", "imerg_raw", SLIDE)]
    t0, t1 = pd.Timestamp("2017-06-10 12:00"), pd.Timestamp("2017-06-14 00:00")
    win = (pd.Timestamp("2017-06-13 02:30"), pd.Timestamp("2017-06-13 11:00"))      # D1, published clock times
    fig, (a, b) = plt.subplots(2, 1, figsize=(6.27, 4.4), sharex=True, gridspec_kw={"height_ratios": [1, 1.6], "hspace": 0.1})
    for ax in (a, b):
        ax.axvspan(*win, color=BAND, zorder=0); ax.yaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    hits = {57.4: [], 200.0: []}
    for lab, col_raw, colr in prods:
        raw = d[col_raw].loc[t0 - pd.Timedelta(hours=24):t1]
        K = 343.0 / raw.rolling(24, min_periods=1).sum().max()                     # gauge anchor (A1)
        corr = raw * K
        a.step(corr.index, corr.values, where="post", color=colr, lw=1.4, label=f"{lab} x{K:.2f}")
        r24 = corr.rolling(24, min_periods=1).sum(); r24raw = raw.rolling(24, min_periods=1).sum()
        b.plot(r24raw.index, r24raw.values, color=colr, lw=0.9, ls=(0, (3, 2)), alpha=0.5)
        b.plot(r24.index, r24.values, color=colr, lw=2, label=f"{lab}, gauge-corrected (x{K:.2f})")
        for val in hits:
            h = r24[r24 >= val].index.min(); hits[val].append(h)
            b.plot([h], [val], marker="o", ms=8, color=colr, mec="white", mew=1.2, zorder=4)
    a.set_ylabel("Hourly rainfall,\ngauge-corrected\n(mm)", fontsize=7)
    b.text(win[0] + (win[1] - win[0]) / 2, 392, "failure window", ha="center", va="top", fontsize=6.5, color=INK2)
    for val, lab in [(57.4, "empirical 57.4 mm (Roy et al. 2022)"), (200, "installed 200 mm (Ali et al. 2018)")]:
        b.axhline(val, color=INK2, lw=0.8, ls=(0, (1, 2)))
        b.text(t0 + pd.Timedelta(hours=1), val + 5, lab, fontsize=6.5, color=INK2, va="bottom")
        h0, h1 = min(hits[val]), max(hits[val])
        l0, l1 = [(win[0] - h).total_seconds() / 3600 for h in (h1, h0)]
        txt = f"{h0:%d %b %H:%M} to {h1:%H:%M}\n{math.floor(l0):+d} to {math.ceil(l1):+d} h before first failures"
        tx, ty = (h0 - pd.Timedelta(hours=2), 114) if val < 100 else (h0 - pd.Timedelta(hours=3), 268)
        b.annotate(txt, xy=(h0, val), xytext=(tx, ty), ha="right", va="bottom",
                   fontsize=6.3, color=INK,
                   arrowprops=dict(arrowstyle="-", lw=0.6, color=MUTED,
                                   shrinkA=3, shrinkB=6, connectionstyle="arc3,rad=0.12"))
    b.set_ylabel("Rolling 24-h total (mm)", fontsize=7); b.set_ylim(0, 400)
    b.legend(frameon=False, fontsize=6.8, loc="upper left", bbox_to_anchor=(0.0, 0.96))
    b.set_xlim(t0, t1); b.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    b.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M")); b.set_xlabel("Bangladesh Standard Time (UTC+6); dashed lines uncorrected", fontsize=7)
    fig.savefig(OUT / "fig1_june2017_hourly.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig1_june2017_hourly.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    return {v: [str(x) for x in h] for v, h in hits.items()}

def fig4():
    """Annual maximum rolling 24-h ERA5-Land rainfall, 1950-2025, from data/scripts/climatology.py.
    Values are uncorrected ERA5-Land, so only their ranks and relative changes are interpreted."""
    import numpy as np
    sys.path.insert(0, str(ROOT / "data" / "scripts"))
    from climatology import mann_kendall
    am = pd.read_csv(ROOT / "data" / "results" / "climatology_annual_maxima.csv")
    am = am[am.window == "24h"]
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.7), sharey=True, constrained_layout=True)
    for a, (pt, lab) in zip(axes, [("Rangamati", "a"), ("Bandarban", "b")]):
        s = am[am.point == pt].set_index("year").annual_max_mm
        full, part = s[s.index <= 2025], s[s.index > 2025]
        a.axvspan(1949.5, 1978.5, color=BAND, lw=0, zorder=0)
        a.text(1964, 300, "before satellite\ndata entered\nthe reanalysis", ha="center", va="top",
               fontsize=6.3, color=INK2)
        a.plot(full.index, full.values, color=RAIN, lw=0.7, alpha=0.55, zorder=2)
        a.scatter(full.index, full.values, s=7, color=RAIN, lw=0, zorder=3)
        meds = {}
        for lo, hi in [(1950, 1978), (1979, 2025)]:
            meds[lo] = m = full.loc[lo:hi].median()
            a.plot([lo - 0.5, hi + 0.5], [m, m], color=INK2, lw=0.8, ls=(0, (4, 2)), zorder=2)
        x = full.loc[1979:]; mk = mann_kendall(x.values)
        yrs = np.array(x.index); b = mk["sen_slope_per_year"]
        c0 = np.median(x.values - b * (yrs - yrs[0]))
        a.plot(yrs, c0 + b * (yrs - yrs[0]), color=INK, lw=1.0, zorder=4)
        a.text(2026, 405, f"dashed: median {meds[1950]:.0f} mm (1950\u201378), {meds[1979]:.0f} mm (1979\u20132025)\n"
               f"solid: Sen slope 1979\u20132025, {1000*b/x.median():+.0f}% per decade, p = {mk['p']:.2f}",
               fontsize=6.0, color=INK, ha="right", va="top", linespacing=1.5)
        for yr, nm in [(2017, "2017"), (2023, "2023")]:
            a.scatter([yr], [s[yr]], s=26, facecolor="none", edgecolor=SLIDE, lw=1.0, zorder=5)
            a.annotate(nm, (yr, s[yr]), xytext=(0, 9 if nm == "2017" else -12), textcoords="offset points",
                       ha="center", fontsize=6.3, color=SLIDE)
        if len(part):
            a.scatter(part.index, part.values, s=26, facecolor="none", edgecolor=MUTED, lw=1.0,
                      ls=(0, (1, 1)), zorder=5)
            a.annotate("2026 to\n21 Sep", (part.index[0], part.values[0]), xytext=(0, 10),
                       textcoords="offset points", ha="center", fontsize=6.0, color=MUTED)
        a.set_title(f"({lab}) {pt}", fontsize=8, loc="left", color=INK)
        a.set_xlim(1948, 2029); a.set_ylim(0, 410)
        a.set_xlabel("Year", fontsize=7)
        a.grid(axis="y", color=GRID, lw=0.5); a.set_axisbelow(True)
    axes[0].set_ylabel("Annual maximum 24-h total,\nERA5-Land, uncorrected (mm)", fontsize=7)
    fig.savefig(OUT / "fig4_climatology.pdf", bbox_inches="tight")
    fig.savefig(OUT / "fig4_climatology.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

if __name__ == "__main__":
    fig1(); fig2(); hits = fig3(); fig4()
    print(f"figures written to {OUT}; crossings {hits}")
