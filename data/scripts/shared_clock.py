#!/usr/bin/env python3
"""The shared clock: for each event, when the landslide thresholds were crossed at the two river
gauge sites in the hills (Sangu at Bandarban, Matamuhuri at Lama) against the day each river
crossed its danger level and the first dated slope failures or landslide deaths.
River crossings are known only to the day, so the comparison is made in days, not hours.
Rainfall is ERA5-Land corrected both ways (quantile mapping and flat factor, see skill.py).
Writes data/results/shared_clock.json."""
import json, sys
from pathlib import Path
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rain_analysis as ra
import skill as sk

SITES = {"Sangu at Bandarban": (22.195, 92.218), "Matamuhuri at Lama": (21.78, 92.19)}
EVENTS = {
    "June 2017": {"window": ("2017-06-01", "2017-06-15"),
                  "river_dl": {"Matamuhuri at Lama": "2017-06-12", "Sangu at Bandarban": "2017-06-13"},   # F1
                  "first_slides": "2017-06-13 02:30"},                                                   # Q4
    "August 2023": {"window": ("2023-07-20", "2023-08-11"),
                    "river_dl": {"Matamuhuri at Lama": "2023-08-06", "Sangu at Bandarban": "2023-08-07"},  # R3
                    "first_slides": "2023-08-07 00:00"},       # BDRCS SitRep 1 (7 Aug): slides already reported; day only
    "July 2026": {"window": ("2026-06-24", "2026-07-14"),
                  "river_dl": {"Matamuhuri at Lama": "2026-07-08", "Sangu at Bandarban": "2026-07-08"},    # Y3, DailyStar2026
                  "first_slides": "2026-07-06 00:00"},                                                   # I8
}
THR = [("empirical_24h_57.4", 24, 57.4), ("installed_24h_200", 24, 200.0),
       ("empirical_72h_130", 72, 130.0), ("installed_72h_350", 72, 350.0)]


def main():
    import numpy as np
    # season files of the climatology archive: identical values to the event files where they
    # overlap, and they start early enough that no crossing is cut off by the start of a record
    import climatology as cl
    hourly = cl.load_hourly()
    tq = pd.read_csv(ra.RES / "qm_transfer.csv"); x, y = tq.era5land_mm.values, tq.gauge_mm.values
    out = {}
    for name, e in EVENTS.items():
        t0, t1 = e["window"]
        rec = {"river_dl": e["river_dl"], "first_slides": e["first_slides"], "sites": {}}
        for site, (la, lo) in SITES.items():
            s = cl.point_series(hourly, la, lo).loc[t0:t1 + " 23:00"]
            cx = {}
            for mode in ("qm", "flat"):
                cs = sk.corrected(s, x, y, mode)
                for tn, hrs, thr in THR:
                    r = cs.rolling(hrs, min_periods=hrs).sum(); hit = r[r >= thr]
                    cx[f"{tn}_{mode}"] = None if hit.empty else str(hit.index[0])[:16]
                    # days on which the threshold was exceeded at some hour, within the window
                    days = sorted({str(t)[:10] for t in hit.index})
                    cx[f"{tn}_{mode}_days"] = days
            rec["sites"][site] = cx
        out[name] = rec
    (ra.RES / "shared_clock.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    print(json.dumps(main(), indent=1))
