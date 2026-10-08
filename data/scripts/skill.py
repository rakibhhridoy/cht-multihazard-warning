#!/usr/bin/env python3
"""Skill of the published thresholds against the dated record, on gauge-corrected ERA5-Land.

Events: every district-date in the Rabby & Li inventory with a full date in May-October
(DATE_FIXES applied), plus the district-dates of landslide deaths or incidents recorded in the
2023 and 2026 situation reports. A threshold 'detects' an event if the corrected rolling total at
the district's landslide centroid reaches it at any hour of the recorded date or the day before
(the inventory date can lag the rain by a day). Detection is reported with a bootstrap interval.

False alarms cannot be counted against an inventory that misses most landslides, so the cost side
is reported as the number of days per May-October season on which each threshold would fire,
1979-2025, per district. A threshold that fires on a third of the monsoon cannot carry an
evacuation trigger whatever its detection rate.

Detection is set against chance (a random date in the same district and season) and recomputed
leaving out one event year at a time, to show the rate does not rest on any one storm year.

Correction is bracketed: 'qm' maps ERA5-Land onto the two coastal gauges by quantiles (right for
ordinary days, low for the heaviest), 'flat' multiplies by the 2026 gauge median of 2.79 (right
for the heaviest days, high for ordinary ones). Writes data/results/skill.json."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import climatology as cl
import rain_analysis as ra
import bias_qm as qm

RES = cl.RES
K_FLAT = 2.79          # ERA5-Land median gauge ratio, July 2026 (event2026.json)
THRESH = [("empirical_24h_57.4", 24, 57.4), ("empirical_72h_130", 72, 130.0),
          ("installed_24h_200", 24, 200.0), ("installed_72h_350", 72, 350.0)]
# Situation-report events (district, date BST), register entries in brackets.
SITREP = [("Bandarban", "2023-08-08"),       # H5, R4: landslides with deaths/road blocks
          ("Cox's Bazar", "2026-07-06"),     # I8: 8 dead in three camps
          ("Cox's Bazar", "2026-07-08"),     # L6: Camp 5 madrasa
          ("Chittagong", "2026-07-08"),      # L3: two children, city and Sitakunda
          ("Chittagong", "2026-07-10"),      # L3: Rangunia
          ("Rangamati", "2026-07-08")]       # I6, I7: 126 incidents over four days, 287 mm to 8 Jul
# Event dates Roy et al. (2022) used to derive the empirical threshold (their Table 1, Cox's Bazar,
# 1997-2021). Inventory events within a day of one are not independent tests of that threshold.
ROY_DATES = pd.to_datetime(["1997-07-11", "2003-06-16", "2003-07-29", "2008-07-03", "2008-07-06",
                            "2008-08-18", "2010-06-13", "2010-06-15", "2012-06-24", "2012-10-30",
                            "2015-06-26", "2015-07-27", "2015-09-01", "2017-06-14", "2017-07-05",
                            "2017-07-24", "2017-07-25", "2018-05-04", "2018-06-11", "2018-07-25",
                            "2018-07-28", "2019-05-11", "2019-07-06", "2019-07-14", "2019-09-09",
                            "2021-05-27", "2021-06-05", "2021-06-19", "2021-07-27", "2021-07-28"])


def corrected(s, x, y, mode):
    """Hourly series rescaled so that its rolling 24-h totals follow the chosen correction."""
    if mode == "raw":
        return s
    if mode == "flat":
        return s * K_FLAT
    r24 = s.rolling(24, center=True, min_periods=1).sum()
    ratio = pd.Series(qm.apply(r24.values, x, y), index=s.index) / r24.where(r24 > 0.1)
    return s * ratio.fillna(1.0)


def robustness(events, roll, hrs, thr):
    """Detection against chance, and its stability across years.

    Chance: the share of May-October days in the event's own district and year whose window (that
    day or the day before, as for the events) reaches the threshold, i.e. the detection a date drawn
    at random from the same season would score. Leave-one-year-out: detection recomputed with each
    event year removed in turn, so no single storm year carries the rate."""
    hits, base, years = [], [], []
    for _, e in events.iterrows():
        r = roll[e.District][hrs]
        w = r.loc[e.D - pd.Timedelta(days=1): e.D + pd.Timedelta(hours=23)]
        if not len(w):
            continue
        hits.append(bool((w >= thr).any())); years.append(e.D.year)
        ry = r[(r.index.year == e.D.year) & r.index.month.isin(range(5, 11))]
        day = (ry >= thr).groupby(ry.index.normalize()).any()
        day = day.reindex(pd.date_range(day.index.min(), day.index.max(), freq="D"), fill_value=False)
        base.append(float((day | day.shift(1, fill_value=False)).mean()))
    hits, years = np.array(hits), np.array(years)
    loyo = [float(hits[years != y].mean()) for y in np.unique(years)]
    return {"pod": round(float(hits.mean()), 2), "chance": round(float(np.mean(base)), 2),
            "pod_without_2017": round(float(hits[years != 2017].mean()), 2),
            "n_without_2017": int((years != 2017).sum()),
            "loyo_min": round(min(loyo), 2), "loyo_max": round(max(loyo), 2),
            "events_per_year": {int(y): int((years == y).sum()) for y in np.unique(years)}}


def load_inventory():
    inv = pd.read_csv(ra.ROOT / "rabby_li_inventory" / "inventory_wgs84.csv")
    d = inv["Date"].astype(str).str.strip().replace(ra.DATE_FIXES)
    inv["D"] = pd.to_datetime(d.where(d.str.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}")), dayfirst=True, errors="coerce")
    return inv


def main():
    hourly = cl.load_hourly()
    tq = pd.read_csv(RES / "qm_transfer.csv"); x, y = tq.era5land_mm.values, tq.gauge_mm.values
    inv = load_inventory()
    cent = inv.groupby("District")[["lat", "lon"]].mean()
    dated = inv.dropna(subset=["D"])
    ev = dated[dated.D.dt.month.between(5, 10)].groupby(["District", "D"]).size().reset_index(name="n")
    ev["source"] = "inventory"
    extra = pd.DataFrame([{"District": d, "D": pd.Timestamp(t), "n": np.nan, "source": "sitrep"} for d, t in SITREP])
    events = pd.concat([ev, extra], ignore_index=True)
    excluded = int(dated[~dated.D.dt.month.between(5, 10)].groupby(["District", "D"]).ngroups)

    series = {dist: cl.point_series(hourly, r.lat, r.lon) for dist, r in cent.iterrows()}
    out = {"events": {"inventory_may_oct": int((events.source == "inventory").sum()),
                      "sitrep": int((events.source == "sitrep").sum()),
                      "excluded_outside_may_oct": excluded},
           "centroids": {d: [round(r.lat, 3), round(r.lon, 3)] for d, r in cent.iterrows()},
           "detection": {}, "alarm_days_per_season_1979_2025": {}}
    rng = np.random.default_rng(1)
    for mode in ["raw", "qm", "flat"]:
        cs = {d: corrected(s, x, y, mode) for d, s in series.items()}
        roll = {d: {h: s.rolling(h, min_periods=h).sum() for h in (24, 72)} for d, s in cs.items()}
        det = {}
        for tn, hrs, thr in THRESH:
            hits = []
            for _, e in events.iterrows():
                r = roll[e.District][hrs]
                w = r.loc[e.D - pd.Timedelta(days=1): e.D + pd.Timedelta(hours=23)]
                hits.append(bool((w >= thr).any()) if len(w) else np.nan)
            hv = np.array(hits, float); ok = ~np.isnan(hv); hv = hv[ok]
            src = events.source.values[ok]
            boot = [rng.choice(hv, len(hv)).mean() for _ in range(2000)]
            det[tn] = {"pod_all": round(float(hv.mean()), 2),
                       "ci90": [round(float(np.percentile(boot, 5)), 2), round(float(np.percentile(boot, 95)), 2)],
                       "pod_inventory": round(float(hv[src == "inventory"].mean()), 2),
                       "pod_sitrep": round(float(hv[src == "sitrep"].mean()), 2), "n": int(len(hv))}
        out["detection"][mode] = det
        if mode in ("qm", "flat"):
            out.setdefault("robustness", {})[mode] = {tn: robustness(events, roll, hrs, thr)
                                                      for tn, hrs, thr in THRESH}
            near = events.D.apply(lambda t: bool((abs((ROY_DATES - t).days) <= 1).any()))
            roy = (events.District == "Cox's Bazar") & near
            cxb = events.District == "Cox's Bazar"
            out.setdefault("independent_of_roy", {})[mode] = {
                "n_overlap": int(roy.sum()),
                "pooled": {tn: robustness(events[~roy], roll, hrs, thr) for tn, hrs, thr in THRESH},
                "coxs_bazar": {tn: robustness(events[cxb & ~roy], roll, hrs, thr) for tn, hrs, thr in THRESH},
                "coxs_bazar_overlap_pod": {tn: robustness(events[roy], roll, hrs, thr)["pod"]
                                           for tn, hrs, thr in THRESH}}
        # sensitivity: recorded date only, without the day before
        same = {}
        for tn, hrs, thr in THRESH:
            hv = []
            for _, e in events.iterrows():
                w = roll[e.District][hrs].loc[e.D: e.D + pd.Timedelta(hours=23)]
                if len(w): hv.append(bool((w >= thr).any()))
            same[tn] = round(float(np.mean(hv)), 2)
        out.setdefault("detection_recorded_date_only", {})[mode] = same
        alarm = {}
        for tn, hrs, thr in THRESH:
            per = {}
            for d in cs:
                r = roll[d][hrs]; r = r[(r.index.year >= 1979) & (r.index.year <= 2025)]
                days = (r >= thr).groupby(r.index.normalize()).any()
                per[d] = round(float(days.groupby(days.index.year).sum().mean()), 1)
            alarm[tn] = per
        out["alarm_days_per_season_1979_2025"][mode] = alarm
        # sweep of the 24-h threshold: detection against alarm days, pooled over districts
        if mode in ("qm", "flat"):
            sweep = []
            for thr in list(range(40, 101, 10)) + list(range(120, 301, 20)):
                hits = []
                for _, e in events.iterrows():
                    w = roll[e.District][24].loc[e.D - pd.Timedelta(days=1): e.D + pd.Timedelta(hours=23)]
                    if len(w): hits.append(bool((w >= thr).any()))
                ad = []
                for d in cs:
                    r = roll[d][24]; r = r[(r.index.year >= 1979) & (r.index.year <= 2025)]
                    days = (r >= thr).groupby(r.index.normalize()).any()
                    ad.append(float(days.groupby(days.index.year).sum().mean()))
                sweep.append({"thr_24h_mm": thr, "pod": round(float(np.mean(hits)), 2),
                              "alarm_days_mean": round(float(np.mean(ad)), 1)})
            out.setdefault("sweep_24h", {})[mode] = sweep
    (RES / "skill.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
