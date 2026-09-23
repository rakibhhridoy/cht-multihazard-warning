#!/usr/bin/env python3
"""Build Figures 1-3 for the three-storm manuscript.

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

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "figdata"; CACHE.mkdir(parents=True, exist_ok=True)
OUT = Path(__file__).resolve().parent

# ---- validated palette (dataviz reference, light, surface #ffffff) -----------------------
RAIN, SLIDE, FLOOD, WARN = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, INK2, MUTED, GRID, BAND = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#f0efec"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
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
    s.to_csv(f)
    return s

BANDARBAN = (22.1953, 92.2184)      # Bandarban town, where the 2017 gauge peak was reported
RANGAMATI = (22.5954, 92.1431)      # centroid of the 160 Rangamati failures, 13 Jun 2017

# ======================================================================================
# Figure 1 - three events, four lanes
# ======================================================================================
EVENTS = [
    # each item: (time, label, ha, level)  level 0 = just below marker, 1 = lower row
    dict(name="June 2017", start="2017-06-08", end="2017-06-16",
         flood=[("2017-06-12 12:00", "Matamuhuri above\ndanger level", "right", 0),        # F1
                ("2017-06-13 12:00", "Sangu peak\n+135 cm", "left", 0)],                    # F1
         slide=[("2017-06-13 05:00", "257 dated failures;\n~150-170 deaths", "center", 0)], # C2, D1
         warn=[], warn_none="no dedicated warning for either hazard"),                                      # F3, G1
    dict(name="August 2023", start="2023-08-02", end="2023-08-11",
         flood=[("2023-08-07 12:00", "Sangu +283 cm", "center", 0)],                          # H1
         slide=[("2023-08-08 12:00", "10 deaths, flood\nand landslides", "center", 0)],                 # H4
         warn=[("2023-08-07 07:00", "FFWC bulletin (24-48 h);\nBMD landslide alert", "right", 0),
               ("2023-08-10 12:00", "33,000\nsheltered", "center", 1)]),  # H2, H3
    dict(name="July 2026", start="2026-07-03", end="2026-07-13",
         flood=[("2026-07-08 09:00", "Sangu +96 cm", "center", 0)],                           # A6
         slide=[("2026-07-06 02:00", "8 killed,\ncamps", "right", 0),                        # I8
                ("2026-07-08 14:00", "5+ killed,\nCamp 5", "left", 0),                       # L6
                ("2026-07-12 12:00", "Rangamati:\n126 incidents,\n1 death", "center", 1)],  # I7
         warn=[("2026-07-05 09:00", "forecast;\nresponse\nactivated", "right", 0),          # I4
               ("2026-07-07 13:00", "Bulletin\n05/2026", "left", 0),                         # I2
               ("2026-07-12 12:00", "38,422\nsheltered", "center", 1)]),                     # I5
]

def fig1():
    fig, axes = plt.subplots(4, 3, figsize=(7.2, 5.6), sharex="col",
                             gridspec_kw={"height_ratios": [1.5, 1, 1, 1], "hspace": 0.06, "wspace": 0.12})
    lanes = [("Rainfall\n(mm per day)", RAIN), ("Flash flood", FLOOD), ("Landslides", SLIDE), ("Warning\nand action", WARN)]
    for c, ev in enumerate(EVENTS):
        day = era5land_point(*BANDARBAN, ev["start"], ev["end"] + " 23:00").resample("D").sum()
        ax = axes[0, c]
        ax.bar(day.index + pd.Timedelta(hours=12), day.values, width=0.82, color=RAIN, linewidth=0)
        ax.set_ylim(0, 130); ax.set_title(ev["name"], fontsize=9, color=INK, loc="left", pad=4)
        ax.yaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
        ax.tick_params(axis="x", length=0)
        if c: ax.set_yticklabels([])
        for r, key in [(1, "flood"), (2, "slide"), (3, "warn")]:
            a = axes[r, c]; col = lanes[r][1]
            a.set_ylim(0, 1); a.set_yticks([]); a.spines["left"].set_visible(False)
            if r < 3:
                a.spines["bottom"].set_color(GRID); a.tick_params(axis="x", length=0)
            for t, lab, ha, lvl in ev[key]:
                x = pd.Timestamp(t)
                a.plot([x], [0.8], marker="o", ms=8, color=col, mec="white", mew=1.2, zorder=3)
                dx = {"right": -pd.Timedelta(hours=4), "left": pd.Timedelta(hours=4), "center": pd.Timedelta(0)}[ha]
                y = 0.8 if ha != "center" else (0.6 if lvl == 0 else 0.62)
                va = "center" if ha != "center" else "top"
                if lvl == 1 and ha == "center": y = 0.6
                a.text(x + dx, y, lab, ha=ha, va=va, fontsize=6.3, color=INK, linespacing=1.05)
            if key == "warn" and ev.get("warn_none"):
                mid = pd.Timestamp(ev["start"]) + (pd.Timestamp(ev["end"]) - pd.Timestamp(ev["start"])) * 0.62
                a.text(mid, 0.5, ev["warn_none"], ha="center", va="center", fontsize=7, color=INK2, style="italic")
        for r in range(4):
            axes[r, c].set_xlim(pd.Timestamp(ev["start"]), pd.Timestamp(ev["end"]) + pd.Timedelta(days=1))
        axes[3, c].xaxis.set_major_locator(mdates.DayLocator(interval=2))
        axes[3, c].xaxis.set_major_formatter(mdates.DateFormatter("%d"))
        axes[3, c].set_xlabel(pd.Timestamp(ev["start"]).strftime("%B %Y"), fontsize=7)
    for r, (lab, col) in enumerate(lanes):
        axes[r, 0].set_ylabel(lab, fontsize=7, color=INK2, rotation=0, ha="right", va="center", labelpad=6)
    fig.savefig(OUT / "fig1_three_events.pdf", bbox_inches="tight"); fig.savefig(OUT / "fig1_three_events.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

# ======================================================================================
# Figure 2 - Rangamati, 2017 vs 2026 (slope chart, one axis, same unit)
# ======================================================================================
def fig2():
    fig, ax = plt.subplots(figsize=(3.4, 3.0))
    x = [0, 1]
    series = [("Slope failures", [160, 126], RAIN),     # C2, I7
              ("Deaths", [121, 1], SLIDE)]              # D1, I7
    for name, y, col in series:
        ax.plot(x, y, color=col, lw=2, solid_capstyle="round", zorder=2, label=name)
        ax.scatter(x, y, s=64, color=col, edgecolor="white", linewidth=1.2, zorder=3, clip_on=False)
        ax.text(-0.06, y[0], f"{y[0]}", ha="right", va="center", fontsize=8, color=INK)
        ax.text(1.06, y[1], f"{y[1]}", ha="left", va="center", fontsize=8, color=INK)
        if name == "Slope failures":
            ax.text(0.5, (y[0] + y[1]) / 2 + 9, name, ha="center", va="bottom", fontsize=7.5, color=INK2)
        else:
            ax.text(0.56, (y[0] + y[1]) / 2, name, ha="left", va="center", fontsize=7.5, color=INK2)
    ax.set_xticks(x); ax.set_xticklabels(["June 2017\nno dedicated warning", "July 2026\nwarning layer"])
    ax.set_xlim(-0.35, 1.35); ax.set_ylim(0, 165); ax.set_ylabel("Count")
    ax.yaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.5, 1.12), ncol=2)
    fig.savefig(OUT / "fig2_rangamati.pdf", bbox_inches="tight"); fig.savefig(OUT / "fig2_rangamati.png", dpi=200, bbox_inches="tight")
    plt.close(fig)

# ======================================================================================
# Figure 3 - June 2017 hourly: intensity (top) and rolling 24-h total with thresholds (bottom)
# ======================================================================================
def fig3():
    d = pd.read_csv(ROOT / "data" / "results" / "june2017_hourly_rangamati.csv", index_col=0, parse_dates=True)
    prods = [("ERA5-Land", "era5land_raw", RAIN), ("IMERG", "imerg_raw", SLIDE)]
    t0, t1 = pd.Timestamp("2017-06-10 12:00"), pd.Timestamp("2017-06-14 00:00")
    win = (pd.Timestamp("2017-06-13 02:30"), pd.Timestamp("2017-06-13 11:00"))      # D1, published clock times
    fig, (a, b) = plt.subplots(2, 1, figsize=(7.2, 4.4), sharex=True, gridspec_kw={"height_ratios": [1, 1.6], "hspace": 0.1})
    for ax in (a, b):
        ax.axvspan(*win, color=BAND, zorder=0); ax.yaxis.grid(True, color=GRID, linewidth=0.5); ax.set_axisbelow(True)
    hits = {57.4: [], 200.0: []}
    for lab, col_raw, colr in prods:
        raw = d[col_raw].loc[t0 - pd.Timedelta(hours=24):t1]
        K = 343.0 / raw.rolling(24, min_periods=1).sum().max()                     # gauge anchor (A1)
        corr = raw * K
        a.step(corr.index, corr.values, where="post", color=colr, lw=1.4, label=f"{lab} x{K:.2f}")
        r24 = corr.rolling(24, min_periods=1).sum(); r24raw = raw.rolling(24, min_periods=1).sum()
        b.plot(r24raw.index, r24raw.values, color=colr, lw=1.0, ls=(0, (3, 2)))
        b.plot(r24.index, r24.values, color=colr, lw=2, label=f"{lab}, gauge-corrected (x{K:.2f})")
        for val in hits:
            h = r24[r24 >= val].index.min(); hits[val].append(h)
            b.plot([h], [val], marker="o", ms=8, color=colr, mec="white", mew=1.2, zorder=4)
    a.set_ylabel("Hourly rainfall,\ngauge-corrected\n(mm)", fontsize=7)
    b.text(win[0] + (win[1] - win[0]) / 2, 392, "failure window", ha="center", va="top", fontsize=6.5, color=INK2)
    for val, lab in [(57.4, "empirical 57.4 mm (Roy et al. 2022)"), (200, "installed 200 mm (Ali et al. 2018)")]:
        b.axhline(val, color=INK2, lw=0.8, ls=(0, (4, 3)))
        b.text(t0 + pd.Timedelta(hours=1), val + 5, lab, fontsize=6.5, color=INK2, va="bottom")
        h0, h1 = min(hits[val]), max(hits[val])
        l0, l1 = [(win[0] - h).total_seconds() / 3600 for h in (h1, h0)]
        txt = f"{h0:%d %b %H:%M} to {h1:%H:%M}\n{math.floor(l0):+d} to {math.ceil(l1):+d} h before first failures"
        tx, ty, ha = (h0 - pd.Timedelta(hours=1), 80, "right") if val < 100 else (h0 - pd.Timedelta(hours=2), 275, "right")
        b.text(tx, ty, txt, ha=ha, va="bottom", fontsize=6.3, color=INK)
    b.set_ylabel("Rolling 24-h total (mm)", fontsize=7); b.set_ylim(0, 400)
    b.legend(frameon=False, fontsize=6.8, loc="upper left", bbox_to_anchor=(0.0, 0.96))
    b.set_xlim(t0, t1); b.xaxis.set_major_locator(mdates.HourLocator(byhour=[0, 12]))
    b.xaxis.set_major_formatter(mdates.DateFormatter("%d %b\n%H:%M")); b.set_xlabel("Bangladesh Standard Time (UTC+6); dashed lines uncorrected", fontsize=7)
    fig.savefig(OUT / "fig3_june2017_hourly.pdf", bbox_inches="tight"); fig.savefig(OUT / "fig3_june2017_hourly.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    return {v: [str(x) for x in h] for v, h in hits.items()}

if __name__ == "__main__":
    fig1(); fig2(); hits = fig3()
    print(f"figures written to {OUT}; crossings {hits}")
