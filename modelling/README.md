# Physical and causal models

Scripts and derived results for the models in the manuscript (Results "What physical models add",
Methods "Physical and causal models", Supplementary Note 4; claims register block M). They reuse
the gauge-anchored rainfall of `data/scripts/` and need the same downloads, plus the landslide
inventory at `data/rabby_li_inventory/inventory_wgs84.csv` (see the main README).

```bash
pip install xarray netCDF4 pandas numpy scipy pyproj rasterio whitebox tigramite earthaccess h5py cdsapi requests
```

## Model codes

Neither model is redistributed here. Build each from its public release into the path the
scripts expect:

| Model | Source | Expected binary |
|---|---|---|
| TRIGRS 2.1 (USGS) | `build/TRIGRS.txt` | `modelling/trigrs/src/TRIGRS/trg` |
| LISFLOOD-FP 8 (Bristol) | `build/LISFLOOD-FP.txt` | `modelling/lisflood/bin/lisflood` |

TRIGRS: in `src/TRIGRS`, `make trg MPIF90=gfortran F90="gfortran -w -O3" F90FLAGS="-w -O3 -std=legacy" CCFLAGS=""`.
LISFLOOD-FP must be built with NetCDF (`dynamicrainfile`). The macOS arm64 build needed the two
CMake configurations in `build/lisflood-config/` and the stub header in `build/lisflood-macshim/`;
`build/LISFLOOD-FP.txt` lists every patch. On Linux the stock configuration should work.

## Slope model, Rangamati (register M1-M8)

```bash
python modelling/scripts/prep_rangamati.py        # 30 m domain around the 160 failures of 13 June 2017, forcing
python modelling/scripts/run_trigrs.py --grid full --tag full_check   # optional: confirms the slope-lookup shortcut (M3)
python modelling/scripts/ensemble_trigrs.py --n 400 --seed 2017
python modelling/scripts/analyse_ensemble.py       # -> results/ensemble_2017_summary.json
python modelling/scripts/prep_forcing2026.py
python modelling/scripts/replay2026.py --seed 2017 --workdir /tmp/trigrs_r26
python modelling/scripts/fetch_icesat2.py          # needs NASA Earthdata credentials in ~/.netrc
python modelling/scripts/icesat2_slopes.py
```

With uniform soil properties each cell's factor of safety depends on its slope alone, so each run
solves one row of slopes from 0 to 50 degrees and fills the landscape by interpolation.

## Causal lags (register M9)

```bash
python modelling/scripts/fetch_pcmci_era5land.py   # needs a ~/.cdsapirc key; rerun to resume
python modelling/scripts/pcmci_lags.py
```

## Flood model, Sangu above Bandarban (register M10)

```bash
python modelling/scripts/prep_sangu.py
for ev in 2017 2023 2026; do
  python modelling/scripts/run_lisflood.py $ev --tag fr1                     # reference
  python modelling/scripts/run_lisflood.py $ev --tag s_n030  --n 0.03        # floodplain roughness
  python modelling/scripts/run_lisflood.py $ev --tag s_n080  --n 0.08
  python modelling/scripts/run_lisflood.py $ev --tag s_cn025 --sgc_n 0.025   # channel roughness
  python modelling/scripts/run_lisflood.py $ev --tag s_cn050 --sgc_n 0.05
  python modelling/scripts/run_lisflood.py $ev --tag s_inf2  --infil_mm_h 2  # infiltration
  python modelling/scripts/run_lisflood.py $ev --tag s_inf5  --infil_mm_h 5
  python modelling/scripts/run_lisflood.py $ev --tag s_w18   --w_coef 1.8    # channel width
  python modelling/scripts/run_lisflood.py $ev --tag s_w35   --w_coef 3.5
done
python modelling/scripts/lisflood_sensitivity.py   # summary table (Supplementary Table 2)
python modelling/scripts/lisflood_overlay.py 2017_fr1
```

Two solver behaviours matter. Without `max_Froude 1` the sub-grid channel creates water while the
solver's own volume error stays small, so every run's stored volume is checked against cumulative
rain (column 12 of the `.mass` file). The sub-grid solver also ignores the scalar `infiltration`
keyword and applies only `infilfile`; the reference runs therefore have no infiltration (the
scalar line in their `run.par` had no effect), and infiltration enters only as a sensitivity case.

## Global reanalysis (register M11)

```bash
python modelling/scripts/fetch_glofas.py   # CEMS Early Warning Data Store; accept the CEMS-FLOODS licence first
python modelling/scripts/glofas_check.py
```

## Derived results

`results/` holds the ensemble and replay tables, the ICESat-2 slope comparison, the PCMCI+ lags,
the GloFAS series and, for each flood run in `results/lisflood/`, its parameter file, summary,
outflow and depth at the town. Gridded model output and the inventory-derived inputs are not
included; the scripts regenerate them. `figures/make_model_figures.py` builds Fig. 6 and
Supplementary Fig. 1 from these files alone.
