#!/usr/bin/env python3
"""Download ICESat-2 ATL08 (land and vegetation height, v007) granules crossing the Rangamati
TRIGRS domain, 2018-10 to 2026-09. Credentials come from ~/.netrc (urs.earthdata.nasa.gov) and
are never written to disk here. Files go to data/icesat2/atl08/."""
from pathlib import Path
import pandas as pd, earthaccess
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "icesat2" / "atl08"; OUT.mkdir(parents=True, exist_ok=True)
f = pd.read_csv(ROOT / "modelling" / "inputs" / "rangamati2017" / "failures.csv")
BBOX = (f.lon.min() - 0.015, f.lat.min() - 0.015, f.lon.max() + 0.015, f.lat.max() + 0.015)
earthaccess.login(strategy="netrc")
g = earthaccess.search_data(short_name="ATL08", bounding_box=BBOX, temporal=("2018-10-01", "2026-09-30"))
todo = [x for x in g if not (OUT / x["umm"]["GranuleUR"]).exists()]
print(f"{len(g)} granules, {len(todo)} to fetch", flush=True)
earthaccess.download(todo, local_path=str(OUT), threads=4)
print("done", len(list(OUT.glob("*.h5"))), "files", flush=True)
