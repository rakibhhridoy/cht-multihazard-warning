#!/usr/bin/env python3
"""Does the river answer the rain before the slope does? PCMCI+ on ERA5-Land, 2001-2026 monsoons.

Question (modelling README): flood versus landslide order. Slopes in the TRIGRS ensemble fail on
pore pressure at 1-4 m, which the deep soil layer (swvl3, 28-100 cm) tracks best of the ERA5-Land
layers. Rivers here rise on quickflow (surface runoff, sro) and are sustained by subsurface runoff
(ssro = ro - sro). So the order of hazards becomes the order in which rain reaches sro, ssro and
swvl3, and whether the deep soil carries memory of earlier days that runoff does not.

Three analyses, at the inventory landslide centroids of Rangamati and Bandarban (the points the
skill analysis uses):

1. PCMCI+ (Runge 2020) on daily anomalies, May-October 2001-2026, tau_max 5 d, with rain
   constrained to be exogenous (nothing in the land surface causes rain). Contemporaneous links
   matter because a UTC day of rain reaches soil and runoff within the same day, which plain
   PCMCI cannot orient. RobustParCorr carries the heavy-tailed rain and runoff marginals; ParCorr
   and a looser pc_alpha are reported as checks, as is each half of the record.
2. Composite of the dated inventory and sitrep events (skill.py), standardised anomalies over
   days -5..+3: on which day does each variable peak relative to the recorded landslide date?
3. Hourly order in the two storm months: hour of peak sro, ssro and of the steepest rise in
   swvl3, against the Rangamati failure window (02:30-11:00 BST 13 June 2017).

Daily labels: the 00 UTC field of day D+1 holds the accumulation of UTC day D (06:00 BST D to
06:00 BST D+1) and the soil state at its end, so every variable is labelled D. Seasons are
separated by tau_max missing rows so no lag straddles a winter. Writes modelling/results/pcmci_*.json."""
import glob, json, sys, zipfile, tempfile
from pathlib import Path
import numpy as np, pandas as pd, xarray as xr

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "data" / "scripts"))
DATA, RES = ROOT / "data" / "pcmci", ROOT / "modelling" / "results"
NAMES = ["rain", "sm1", "sm2", "sm3", "sro", "ssro"]
TAU = 5
MISSING = -999.0
FAIL_2017 = (pd.Timestamp("2017-06-13 02:30"), pd.Timestamp("2017-06-13 11:00"))   # BST


def open_nc(path):
    """CDS may return a zip of per-stream NetCDFs even when 'unarchived' is asked for."""
    if zipfile.is_zipfile(path):
        d = Path(tempfile.mkdtemp()); zipfile.ZipFile(path).extractall(d)
        return xr.merge([xr.open_dataset(f).drop_vars(["number", "expver"], errors="ignore")
                         for f in sorted(d.glob("*.nc"))], compat="override")
    return xr.open_dataset(path).drop_vars(["number", "expver"], errors="ignore")


def nearest(ds, lat, lon):
    valid = ds["swvl3"].notnull().any(ds["swvl3"].dims[0])
    d = ((ds.latitude - lat) ** 2 + (ds.longitude - lon) ** 2).where(valid)
    i, j = np.unravel_index(int(np.nanargmin(d.values)), d.shape)
    return ds.isel(latitude=i, longitude=j)


def daily(lat, lon):
    out = []
    for f in sorted(glob.glob(str(DATA / "daily_*.nc"))):
        ds = nearest(open_nc(f), lat, lon)
        t = "valid_time" if "valid_time" in ds.dims else "time"
        df = pd.DataFrame({"rain": ds.tp.values * 1000, "sm1": ds.swvl1.values, "sm2": ds.swvl2.values,
                           "sm3": ds.swvl3.values, "sro": ds.sro.values * 1000,
                           "ssro": (ds.ro.values - ds.sro.values) * 1000},
                          index=pd.DatetimeIndex(ds[t].values) - pd.Timedelta(days=1))
        out.append(df)
    df = pd.concat(out).sort_index()
    df = df[~df.index.duplicated()]
    return df[df.index.month.isin(range(5, 11))].dropna()


def anomalies(df):
    """Departure from a 31-day smoothed day-of-year climatology, so the monsoon cycle itself
    cannot appear as a causal link."""
    doy = df.index.dayofyear
    clim = df.groupby(doy).mean().reindex(range(1, 367)).interpolate(limit_direction="both")
    clim = pd.concat([clim.iloc[-15:], clim, clim.iloc[:15]]).rolling(31, center=True).mean().iloc[15:-15]
    clim.index = range(1, 367)
    return df - clim.loc[doy].values


def stack(anom):
    blocks = []
    for _, g in anom.groupby(anom.index.year):
        blocks.append(g[NAMES].values); blocks.append(np.full((TAU, len(NAMES)), MISSING))
    return np.vstack(blocks)


def assumptions():
    """Default PCMCI+ link set, except rain is exogenous: no land-surface variable causes rain,
    at any lag, and a same-day rain link points out of rain."""
    n = len(NAMES); la = {}
    for j in range(n):
        la[j] = {}
        for i in range(n):
            for tau in range(0, TAU + 1):
                if tau == 0 and i == j:
                    continue
                if j == 0 and i != 0:
                    continue                                   # nothing into rain
                if tau == 0:
                    la[j][(i, 0)] = "-?>" if i == 0 else ("<?-" if j == 0 else "o?o")
                else:
                    la[j][(i, -tau)] = "-?>"
    for j in range(1, n):
        la[0][(j, 0)] = "<?-"
    return la


def run(arr, test="robust", pc_alpha=0.01):
    from tigramite import data_processing as pp
    from tigramite.pcmci import PCMCI
    from tigramite.independence_tests.parcorr import ParCorr
    from tigramite.independence_tests.robust_parcorr import RobustParCorr
    df = pp.DataFrame(arr, var_names=NAMES, missing_flag=MISSING)
    ci = RobustParCorr() if test == "robust" else ParCorr()
    p = PCMCI(dataframe=df, cond_ind_test=ci, verbosity=0)
    r = p.run_pcmciplus(tau_min=0, tau_max=TAU, pc_alpha=pc_alpha, link_assumptions=assumptions())
    links = []
    g, v, pv = r["graph"], r["val_matrix"], r["p_matrix"]
    for i in range(len(NAMES)):
        for j in range(len(NAMES)):
            for tau in range(TAU + 1):
                e = g[i, j, tau]
                if e == "" or (tau == 0 and i > j and e in ("o-o", "x-x")):
                    continue                                   # undirected same-day edges listed once
                if tau == 0 and e == "<--":
                    continue                                   # listed from the other end as -->
                links.append({"from": NAMES[i], "to": NAMES[j], "lag_d": tau, "edge": e,
                              "val": round(float(v[i, j, tau]), 3), "p": float(f"{pv[i, j, tau]:.2g}")})
    return links


def summary(links):
    """Per target, the lags at which rain and the soil layers enter, and the target's own memory."""
    s = {}
    for t in NAMES[1:]:
        into = [l for l in links if l["to"] == t and l["edge"] in ("-->", "o-o", "x-x")]
        s[t] = {"from_rain_lags": sorted(l["lag_d"] for l in into if l["from"] == "rain"),
                "rain_lag0_val": next((l["val"] for l in into if l["from"] == "rain" and l["lag_d"] == 0), None),
                "own_memory_lags": sorted(l["lag_d"] for l in into if l["from"] == t),
                "parents": sorted({f'{l["from"]}(-{l["lag_d"]})' for l in into})}
    return s


def composite(df, events, district):
    z = (anomalies(df) / anomalies(df).std())
    rows = []
    for d in events[events.District == district].D:
        d = pd.Timestamp(d).normalize()
        w = z.reindex(pd.date_range(d - pd.Timedelta(days=5), d + pd.Timedelta(days=3)))
        if w[NAMES].notna().all(axis=1).sum() == 9:
            w.index = range(-5, 4); rows.append(w)
    if not rows:
        return None
    m = pd.concat(rows).groupby(level=0).median()
    return {"n_events": len(rows), "peak_day": {k: int(m[k].idxmax()) for k in NAMES},
            "median_z": {k: [round(float(x), 2) for x in m[k]] for k in NAMES}}


def deaccum(x, t):
    """ERA5-Land hourly accumulation from 00 UTC, reset at 01 UTC (as climatology.load_hourly)."""
    x = pd.Series(np.asarray(x, float), index=t).sort_index()
    h = x.diff(); h[x.index.hour == 1] = x[x.index.hour == 1]
    return h.clip(lower=0).dropna()                    # first hour has no predecessor


def hourly_order(lat, lon, tag):
    f = DATA / f"hourly_{tag}.nc"
    if not f.exists():
        return None
    ds = nearest(open_nc(f), lat, lon)
    t = pd.DatetimeIndex(ds["valid_time" if "valid_time" in ds.dims else "time"].values)
    rain = deaccum(ds.tp.values * 1000, t); ro = deaccum(ds.ro.values * 1000, t)
    sro = deaccum(ds.sro.values * 1000, t); ssro = (ro - sro).clip(lower=0)
    sm3 = pd.Series(ds.swvl3.values, index=t).sort_index(); sm1 = pd.Series(ds.swvl1.values, index=t).sort_index()
    bst = lambda s: (s.dropna().idxmax() + pd.Timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
    r24 = rain.rolling(24).sum()
    out = {"peak_rain_24h_end_bst": bst(r24), "peak_rain_hour_bst": bst(rain),
           "peak_sro_hour_bst": bst(sro), "peak_ssro_hour_bst": bst(ssro),
           "steepest_sm3_rise_6h_end_bst": bst(sm3.diff(6)), "peak_sm3_bst": bst(sm3), "peak_sm1_bst": bst(sm1),
           "sm3_range": [round(float(sm3.min()), 3), round(float(sm3.max()), 3)]}
    if tag == "2017_06":
        # how close the deep layer was to its peak when the first slopes failed
        tf = FAIL_2017[0] - pd.Timedelta(hours=6)
        s = sm3.loc[:tf]
        out["sm3_at_first_failure_share_of_rise"] = round(float((s.iloc[-1] - sm3.loc["2017-06-08":].min()) /
                                                              (sm3.max() - sm3.loc["2017-06-08":].min())), 2)
        out["ssro_at_first_failure_share_of_peak"] = round(float(ssro.loc[:tf].iloc[-1] / ssro.max()), 2)
    return out


def main():
    import skill
    inv = skill.load_inventory()
    cent = inv.groupby("District")[["lat", "lon"]].mean()
    dated = inv.dropna(subset=["D"])
    ev = dated[dated.D.dt.month.between(5, 10)][["District", "D"]].drop_duplicates()
    ev = pd.concat([ev, pd.DataFrame([{"District": d, "D": pd.Timestamp(t)} for d, t in skill.SITREP])])
    ev = ev[ev.D.dt.year >= 2001]
    out = {}
    for dist in ["Rangamati", "Bandarban"]:
        lat, lon = cent.loc[dist]
        df = daily(lat, lon); anom = anomalies(df); arr = stack(anom)
        res = {"point": [round(lat, 3), round(lon, 3)], "days": int(len(df)),
               "years": [int(df.index.year.min()), int(df.index.year.max())]}
        links = run(arr)
        res["links"] = links; res["summary"] = summary(links)
        res["checks"] = {"parcorr": summary(run(arr, "parcorr")),
                         "robust_pc_alpha_0.05": summary(run(arr, pc_alpha=0.05))}
        for lab, yrs in [("2001_2013", range(2001, 2014)), ("2014_2026", range(2014, 2027))]:
            res["checks"][lab] = summary(run(stack(anom[anom.index.year.isin(yrs)])))
        res["composite"] = composite(df, ev, dist)
        res["hourly"] = {tag: hourly_order(lat, lon, tag) for tag in ("2017_06", "2026_07")}
        out[dist] = res
        print(dist, json.dumps(res["summary"], indent=1), flush=True)
    (RES / "pcmci_lags.json").write_text(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
