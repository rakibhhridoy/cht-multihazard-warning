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
| `data/scripts/fetch_era5land_climatology.py` | Retrieves ERA5-Land hourly precipitation for May to October of every year from 1950, one verified file per season |
| `data/scripts/climatology.py` | Annual maximum 24- and 72-hour rainfall at Rangamati and Bandarban, Mann-Kendall trends and Sen slopes (full record and 1979 onward), GEV return periods, and threshold-exceedance days |
| `data/scripts/fetch_imerg_event.py` | Retrieves and subsets IMERG V07 half-hourly precipitation for a comparator event (Late run for July 2026), resumably |
| `data/scripts/fetch_public_inputs.py` | Retrieves the GHCN-Daily gauge records, the ISCG camp outlines and the Copernicus 30 m elevation tiles |
| `data/scripts/event2026.py` | Checks ERA5-Land and IMERG Late against the ten BMD 24-hour gauge totals of July 2026 and replays the thresholds at Rangamati, the Ukhiya camps and Chattogram |
| `data/scripts/bias_qm.py` | Quantile mapping of ERA5-Land onto the Chattogram and Cox's Bazar gauges, validated out of sample on July 2026 |
| `data/scripts/skill.py` | Detection of dated landslide district-days by each threshold, days per season on which each would fire, and a sweep of the 24-hour threshold |
| `data/scripts/shared_clock.py` | Threshold crossings at the Sangu and Matamuhuri gauge sites against river danger-level crossings, for all three events |
| `data/scripts/warming.py` | Sensitivity of the thresholds' alarm days and detection to 1-3 degrees of warming at the Clausius-Clapeyron rate |
| `data/scripts/camp_slopes.py` | Slope and relief of the 33 Rohingya camps from the Copernicus 30 m elevation model, by fatal and listed status |
| `figures/make_figures.py` | Builds the five manuscript figures from the derived data in `data/` |
| `data/results/` | Derived outputs: the June 2017 hourly series at Rangamati, the threshold crossing times, the inventory date audit table, and the 1950-2025 rainfall climatology |
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
pip install xarray netCDF4 pandas numpy scipy matplotlib cdsapi earthaccess
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

The 1950-2025 climatology needs one CDS request per monsoon season, because the CDS cost
limit refuses two seasons in one request. Queue time dominates, so expect about a day. The
fetch is resumable and decides what is missing by opening every file and counting its hours:

```bash
python data/scripts/fetch_era5land_climatology.py   # rerun until it reports nothing remaining
python data/scripts/climatology.py
```

ERA5-Land captures about a third of the June 2017 gauge total, so the climatology interprets
only rank-based results. The Mann-Kendall test is unchanged by any constant scaling, and the
Sen slope is reported as a percentage of the median per decade.

`rain_analysis.py` carries a unit test on the ERA5-Land de-accumulation convention, in which
accumulations run from 00 UTC and reset at 01 UTC. It runs on import and will fail loudly if
a future data revision changes that convention.

The enhancement analyses read the same hourly archives plus three small public inputs, which
are fetched rather than redistributed, and IMERG Late for July 2026:

```bash
python data/scripts/fetch_public_inputs.py
python data/scripts/fetch_imerg_event.py GPM_3IMERGHHL 2026-07-02T18:00 2026-07-10T18:00 2026-07
python data/scripts/event2026.py      # 2026 gauge check and threshold replay
python data/scripts/bias_qm.py        # quantile mapping, needs the climatology archive
python data/scripts/skill.py
python data/scripts/shared_clock.py
python data/scripts/camp_slopes.py
python data/scripts/warming.py
```

Version 1.2.0 also corrects the hour labelling of IMERG in `rain_analysis.py`. IMERG hours were
labelled at their start and ERA5-Land hours at their end, so every IMERG threshold crossing in
earlier versions was one hour early. The ERA5-Land results are unchanged.

The landslide inventory is the supplementary dataset of Rabby and Li (2020) and is not
redistributed here. Download it from the publisher and place the WGS-84 CSV at
`data/rabby_li_inventory/inventory_wgs84.csv` before running the date audit.

## Third-party data

| Source | Terms |
|---|---|
| ERA5-Land hourly, Copernicus Climate Data Store | Copernicus licence; attribution required |
| GPM IMERG V07 Final and Late, NASA GES DISC | Freely available; attribution required |
| GHCN-Daily, NOAA NCEI | Public domain |
| Copernicus GLO-30 elevation model, ESA | Copernicus licence; attribution required |
| Camp outlines, Inter Sector Coordination Group via HDX | CC0 |
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
