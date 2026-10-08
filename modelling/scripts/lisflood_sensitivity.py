#!/usr/bin/env python3
"""Does the flood model's timing and ranking survive its uncertain parameters?

One-at-a-time variants around the reference runs (<event>_fr1: floodplain n 0.05, channel n 0.035,
no infiltration, channel width 2.6 A^0.5), each run for all three storms by run_lisflood.py
with tag s_*. For every variant: the water-balance check (stored volume never above net rain), the
modelled town peak against the observed peak day, and whether peak depth and peak 3 h outflow rank
the storms 2023 > 2017 > 2026 as the FFWC record does. Writes modelling/results/lisflood_sensitivity.{csv,json}."""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "modelling" / "results" / "lisflood"
EVENTS = ["2023", "2017", "2026"]                      # observed order, highest first
LABEL = {"fr1": "reference", "s_n030": "floodplain n 0.03", "s_n080": "floodplain n 0.08",
         "s_cn025": "channel n 0.025", "s_cn050": "channel n 0.05", "s_inf2": "infiltration 2 mm/h",
         "s_inf5": "infiltration 5 mm/h", "s_w18": "width 1.8 A^0.5", "s_w35": "width 3.5 A^0.5"}


def main():
    rows = []
    for tag, lab in LABEL.items():
        for e in EVENTS:
            f = RES / f"{e}_{tag}" / "summary.json"
            if not f.exists():
                continue
            s = json.loads(f.read_text())
            peak = pd.Timestamp(s["depth_peak_bst"])
            rows.append({"variant": lab, "tag": tag, "event": e, "depth_peak_m": s["depth_peak_m"],
                         "depth_peak_bst": s["depth_peak_bst"],
                         "peak_offset_d": (peak.normalize() - pd.Timestamp(s["obs_peak_bst"])).days,
                         "qout_peak_3h_m3s": s["qout_peak_3h_m3s"], "overbank_hours": s["overbank_hours"],
                         "max_stored_over_net_rain": s.get("max_stored_over_net_rain"),
                         "returncode": s["returncode"]})
    df = pd.DataFrame(rows); df.to_csv(ROOT / "modelling" / "results" / "lisflood_sensitivity.csv", index=False)
    out = {}
    for tag, g in df.groupby("tag", sort=False):
        g = g.set_index("event")
        if set(g.index) != set(EVENTS):
            out[LABEL[tag]] = {"complete": False}; continue
        rank = lambda col: list(g[col].sort_values(ascending=False).index)
        out[LABEL[tag]] = {"complete": True,
                           "rank_depth": rank("depth_peak_m"), "rank_depth_ok": rank("depth_peak_m") == EVENTS,
                           "rank_qout": rank("qout_peak_3h_m3s"), "rank_qout_ok": rank("qout_peak_3h_m3s") == EVENTS,
                           "depth_spread_m": round(float(g.depth_peak_m.max() - g.depth_peak_m.min()), 2),
                           "peak_offset_d": {e: int(g.loc[e, "peak_offset_d"]) for e in EVENTS},
                           "max_stored_over_net_rain": g.max_stored_over_net_rain.max()}
    (ROOT / "modelling" / "results" / "lisflood_sensitivity.json").write_text(json.dumps(out, indent=1, default=str))
    print(df.to_string(index=False)); print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
