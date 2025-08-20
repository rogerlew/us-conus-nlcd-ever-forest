# US CONUS NLCD Ever Forest Collection

![Ever Forest Map](https://media.githubusercontent.com/media/rogerlew/us-conus-nlcd-ever-forest/main/ever_forest_map.png)

This repository contains scripts and metadata for building derived land cover layers from the **Annual National Land Cover Database (NLCD) Collection 1 Products (ver. 1.1, June 2025)**.  

These derived products were created to support **watershed modeling in [WEPPcloud](https://wepp.cloud/)**.  

---

## Dataset Description

### Ever Forest Layer
- A **static composite layer** (`ever_forest/ever_forest_cog.tif`) identifying forested areas across the CONUS.
- Forest classes are aggregated from the NLCD land cover codes:
  - **41**: Deciduous Forest  
  - **42**: Evergreen Forest  
  - **43**: Mixed Forest  
- Useful for long-term watershed landuse characterization.

### Yearly Ever Forest Layers
- A **time series of yearly maps** (`1985` … `2024` directories) showing the intersection of NLCD annual land cover data and the Ever Forest mask.
- Each yearly product preserves the NLCD land cover class for forested areas and substitutes the year code elsewhere.
- Supports **change detection**, **historical analysis**, and **watershed-scale simulation**.

---

## Build Instructions

The repository includes scripts to automate download, processing, and dataset generation:

1. **Acquire Annual NLCD Maps**
   ```bash
   ./_0_acquire_and_build_vrts.sh
   ```
   - Downloads NLCD annual land cover bundles (`1985–2024`).
   - Extracts and builds per-year `.vrt` mosaics.

2. **Build Ever Forest Layer**
   ```bash
   python _1_build_ever_forest.py
   ```
   - Aggregates classes 41, 42, 43.
   - Produces a Cloud-Optimized GeoTIFF (`ever_forest/ever_forest_cog.tif`).

3. **Build Yearly Ever Forest Layers**
   ```bash
   python _2_build_yearly_ever_forest.py
   ```
   - Applies the Ever Forest mask to each year.
   - Produces annual ever forest maps (`<year>/ever_forest_<year>.tif`).

4. **Symlink Metadata**
   ```bash
   ./_3_symlink_metadata.sh
   ```
   - Creates symlinks to `metadata.json` inside each year’s directory.
   - Ensures consistent dataset description.

5. **Symlink Ever Forest Metadata**
   ```bash
   ./_4_symlink_ever_forest_metadata.sh
   ```
   - Creates symlinks to `ever_forest_metadata.json` inside each year’s directory.
   - Ensures consistent dataset description.

6. **Create Cloud Optimized Geotiffs**
   ```bash
   ./_6_make_ever_forest_cogs.sh
   ```
   - Cloud Optimizes Ever Forest .tif files

---

## Metadata

Metadata is provided in [`ever_forest_metadata.json`](ever_forest_metadata.json).  
Example fields:

```json
{
  "dataset": "Ever Forest Derived from Annual National Land Cover Database (NLCD) Collection 1 Products (ver. 1.1, June 2025)",
  "publisher": "University of Idaho (Roger Lew)",
  "year": 2025,
  "variable": "land cover",
  "units": "N/A",
  "source_url": "https://github.com/rogerlew/us-conus-nlcd-ever-forest/",
  "rights": "Public Domain"
}
```

---

## Usage Rights and Disclaimer

- **Source Data**: U.S. Geological Survey (USGS) National Land Cover Database (NLCD).  
- **Rights**: Public Domain. Works of the USGS are not subject to copyright in the United States.  
- **Disclaimer**:  
  This repository and derived products are provided *as is* with no warranty.  
  They are intended for research and educational purposes, particularly in watershed modeling.  
  Users should consult the official [MRLC NLCD site](https://www.mrlc.gov/) for authoritative data products.  

---

## Citation

If you use this dataset, please cite:

- **NLCD**:  
  U.S. Geological Survey. National Land Cover Database (NLCD).  
  [https://www.mrlc.gov/](https://www.mrlc.gov/)

- **Ever Forest Derived Products**:  
  Lew, R. (2025). *Ever Forest Derived from Annual NLCD Collection 1 Products (ver. 1.1, June 2025).* University of Idaho.  
  [GitHub Repository](https://github.com/rogerlew/us-conus-nlcd-ever-forest/)

### BibTeX

```bibtex
@misc{lew2025everforest,
  author       = {Lew, Roger},
  title        = {Ever Forest Derived from Annual National Land Cover Database (NLCD) Collection 1 Products (ver. 1.1, June 2025)},
  year         = {2025},
  publisher    = {University of Idaho},
  howpublished = {\url{https://github.com/rogerlew/us-conus-nlcd-ever-forest/}},
  note         = {Public Domain. Derived from USGS NLCD data.}
}
```

---

