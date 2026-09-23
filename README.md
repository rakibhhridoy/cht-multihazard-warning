# Compound landslide and flash flood events in the Chittagong Hill Tracts

Analysis code, derived data and the claims register for a study of three compound
landslide and flash flood events on the same slopes and rivers of south-eastern
Bangladesh: **June 2017**, **August 2023** and **July 2026**.

The study compares what was observed, what was forecast, what was advised and what was
acted on across the three events, using gauge-anchored rainfall, a date-audited landslide
inventory, river stage records and agency situation reports. Manuscript in preparation.

## What is here

| Path | Contents |
|---|---|
| `data/scripts/fetch_era5land.py` | Retrieves ERA5-Land hourly total precipitation from the Copernicus Climate Data Store |
| `data/scripts/fetch_imerg.py` | Retrieves and subsets GPM IMERG V07 Final half-hourly precipitation |
| `data/scripts/rain_analysis.py` | De-accumulation of ERA5-Land hourly totals, gauge anchoring, threshold crossings, and the rainfall-based inventory date audit |
| `figures/make_figures.py` | Builds the three manuscript figures from the derived data in `data/` |
| `data/results/` | Derived outputs: the June 2017 hourly series at Rangamati, the threshold crossing times, and the inventory date audit table |
| `data/figdata/` | Cached point rainfall series for the three events: ERA5-Land extractions at Bandarban, and the gauge-comparison series |
| `review/claims-register.md` | Every load-bearing quantitative claim in the study, its status, and its source |

## The claims register

`review/claims-register.md` is the audit trail. Each claim carries a status:

- `SOLID` — an official or primary source is in hand
- `PRESS` — press reporting only
- `INFER` — an inference drawn in this study
- `OPEN` — unconfirmed

The register also records claims that were retracted or corrected during the work, including
several that earlier drafts had stated too strongly. It takes precedence over any other file
here where the two disagree.

## Reproducing the analysis

```bash
pip install xarray netCDF4 pandas numpy matplotlib cdsapi earthaccess
```

The figures rebuild from the derived data shipped in this repository, with no downloads:

```bash
python figures/make_figures.py
```

The rainfall analysis itself reads hourly NetCDF that is **not** redistributed here, because
it is better taken fresh from the providers. Retrieve it first, then rerun:

```bash
python data/scripts/fetch_era5land.py     # needs a ~/.cdsapirc key
python data/scripts/fetch_imerg.py        # needs NASA Earthdata credentials in ~/.netrc
python data/scripts/rain_analysis.py
python data/scripts/rain_analysis.py audit
```

`rain_analysis.py` carries a unit test on the ERA5-Land de-accumulation convention, in which
accumulations run from 00 UTC and reset at 01 UTC. It runs on import and will fail loudly if
a future data revision changes that convention.

The landslide inventory is the supplementary dataset of Rabby and Li (2020) and is not
redistributed here. Download it from the publisher and place the WGS-84 CSV at
`data/rabby_li_inventory/inventory_wgs84.csv` before running the date audit.

## Third-party data

| Source | Terms |
|---|---|
| ERA5-Land hourly, Copernicus Climate Data Store | Copernicus licence; attribution required |
| GPM IMERG V07 Final, NASA GES DISC | Freely available; attribution required |
| Landslide inventory, Rabby and Li (2020) | Obtain from the publisher; cite the original |
| Flood Forecasting and Warning Centre annual reports; agency situation reports | Obtain from the issuing organisations |

Publisher PDFs, agency reports and raw reanalysis files are deliberately excluded from this
repository. The scripts that fetch them are included instead.

## Licence

Code in `data/scripts/` and `figures/` is released under the MIT Licence (`LICENSE`).
Derived data in `data/` and the claims register in `review/` are released under
Creative Commons Attribution 4.0 International (`LICENSE-data`).

## Authors

Md Rakib Hasan ([0009-0002-4007-7590](https://orcid.org/0009-0002-4007-7590)),
Shoumik Zubyer ([0009-0006-4085-1493](https://orcid.org/0009-0006-4085-1493)),
Mst Anika Khatun Rupa ([0009-0008-4347-4288](https://orcid.org/0009-0008-4347-4288)),
A. S. M. Mohiuddin

Fermium Systems, Dhaka, and the Department of Soil, Water and Environment,
University of Dhaka.

Correspondence: rakibhhridoy@fermium.systems
