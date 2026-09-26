#!/usr/bin/env python3
"""Downloads the small public inputs of the enhancement analyses, which are retrieved rather than
redistributed: GHCN-Daily records of the Chattogram airport and Cox's Bazar gauges (bias_qm.py),
the ISCG camp outlines of 12 April 2023 (HDX, CC0) and the Copernicus GLO-30 elevation tiles
N20/N21 E092 (camp_slopes.py)."""
import urllib.request, zipfile
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
for rel, url in GET:
    out = ROOT / rel; out.parent.mkdir(exist_ok=True)
    if not out.exists():
        print("fetch", rel, flush=True)
        urllib.request.urlretrieve(url, out)
zipfile.ZipFile(ROOT / "camps" / "a1_camp_outlines.zip").extractall(ROOT / "camps")
print("done")
