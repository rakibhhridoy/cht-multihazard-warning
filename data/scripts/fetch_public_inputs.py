#!/usr/bin/env python3
"""Downloads the small public inputs of the enhancement analyses, which are retrieved rather than
redistributed: GHCN-Daily records of the Chattogram airport and Cox's Bazar gauges (bias_qm.py),
the ISCG camp outlines of 12 April 2023 (HDX, CC0) and the Copernicus GLO-30 elevation tiles
N20/N21 E092 (camp_slopes.py), and for the maps of Figs. 1 and 4 the geoBoundaries ADM2 districts of
Bangladesh and the Copernicus GLO-90 tiles N20-N23, E091-E092."""
import time, urllib.request, zipfile
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
GET = [
    ("ghcnd/BGM00041978.csv.gz", "https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/BGM00041978.csv.gz"),
    ("ghcnd/BGM00041992.csv.gz", "https://www.ncei.noaa.gov/pub/data/ghcn/daily/by_station/BGM00041992.csv.gz"),
    ("camps/a1_camp_outlines.zip",
     "https://data.humdata.org/dataset/1a67eb3b-57d8-4062-b562-049ad62a85fd/resource/"
     "ace4b0a6-ef0f-46e4-a50a-8c552cfe7bf3/download/20230412_a1_camp_outlines.zip"),
    ("dem/cop30_N21_E092.tif", "https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N21_00_E092_00_DEM/"
                               "Copernicus_DSM_COG_10_N21_00_E092_00_DEM.tif"),
    ("dem/cop30_N20_E092.tif", "https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N20_00_E092_00_DEM/"
                               "Copernicus_DSM_COG_10_N20_00_E092_00_DEM.tif"),
]
GET.append(("admin/bgd_adm2.geojson",
            "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/BGD/ADM2/geoBoundaries-BGD-ADM2.geojson"))
# GLO-90 has no tile for N20 E091, which is open sea
for la in (20, 21, 22, 23):
    for lo in ("091", "092"):
        if (la, lo) == (20, "091"):
            continue
        n = f"Copernicus_DSM_COG_30_N{la}_00_E{lo}_00_DEM"
        GET.append((f"dem/cop90/{n}.tif", f"https://copernicus-dem-90m.s3.amazonaws.com/{n}/{n}.tif"))
for rel, url in GET:
    out = ROOT / rel; out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        print("fetch", rel, flush=True)
        # write to a .part file and rename, so an interrupted download is retried on the next run
        # rather than left behind as a truncated file that looks complete
        part = out.with_name(out.name + ".part")
        for attempt in range(4):
            try:
                urllib.request.urlretrieve(url, part)
                part.rename(out)
                break
            except OSError as e:
                print("  retry", attempt + 1, e, flush=True)
                time.sleep(5 * (attempt + 1))
        else:
            raise SystemExit("could not fetch " + url)
zipfile.ZipFile(ROOT / "camps" / "a1_camp_outlines.zip").extractall(ROOT / "camps")
print("done")
