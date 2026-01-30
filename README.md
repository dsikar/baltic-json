# Baltic Vector Data Cleaning and Conversion Project

## Overview
This project focuses on cleaning and converting vector data derived from raster sources. The workflow processes GeoJSON polygon features with DN (Digital Number) values to:
1. Clean invalid geometries and artifacts
2. Filter high-value areas above a threshold
3. Convert vector polygons to raster TIFF format

**Geographic Area**: Scotland and NE England

## Project Structure
```
baltic-json/
├── data/               # Raw data files (not included in repository)
├── images/             # Reference visualizations
│   └── Screenshot 2026-01-30 at 15.56.09.png
├── prompts/            # Task definition prompts
│   ├── 01-vector-data-cleaning.md
│   ├── 02-vector-to-raster-conversion.md
│   └── 03-contour-generation.md
├── scripts/            # Processing scripts (to be created)
├── output/             # Generated output files (to be created)
└── work-diary.md       # Project work log
```

## Data
The project works with GeoJSON FeatureCollection data containing:
- **Geometry Type**: Polygon (derived from raster conversion)
- **Properties**: DN (Digital Number) values from raster source (range: 0-255)
- **Coordinate System**: Projected coordinates (UTM or similar)
- **Size**: ~20MB
- **Geographic Coverage**: Scotland and NE England

**Note**: Raw data files are not included in this repository. Please do not contact the author for data access.

## Complete Processing Pipeline

The project implements a three-stage pipeline for converting vector polygon data into classified contour lines:

```
Vector Polygons (GeoJSON) → Raster (TIFF) → Contour Lines (GeoJSON)
     Step 1: Clean         Step 2: Convert    Step 3: Generate
```

### 1. Vector Data Cleaning
Defined in `prompts/01-vector-data-cleaning.md`:
1. Removing invalid and null geometries
2. Handling NoData values
3. Removing rasterization artifacts
4. Topology cleaning
5. Attribute validation

### 2. Vector to Raster Conversion (Current POC)
Defined in `prompts/02-vector-to-raster-conversion.md`:
1. Load and validate vector data
2. Spatial subset for proof of concept (save as `output/subset_extract.json`)
3. **Quantize DN values to bucket centers** (12.5, 37.5, 62.5, ..., 240.0)
4. Filter by DN threshold (optional)
5. Determine raster parameters
6. Rasterize polygons with quantized values
7. Create GeoTIFF output
8. Visualization and validation

**Key Feature**: DN values are quantized to 10 bucket centers (intervals of 25) preparing data for contour generation.

Reference visualization: `images/Screenshot 2026-01-30 at 15.56.09.png` shows expected output with high-value areas highlighted.

### 3. Contour Line Generation
Defined in `prompts/03-contour-generation.md`:
1. Load and validate raster TIFF
2. Prepare data for contouring
3. Generate contour lines at 25 DN intervals
4. Convert to vector format (LineStrings)
5. Simplify and clean contours
6. Create classified output (10 classes: 0-25, 25-50, ..., 225-255)
7. Validation and visualization

**Output**: Contour lines representing isolines of equal DN value, classified into 10 categories.

## Contact
**Corresponding Author**: Blazej Jan Barski
**Email**: blazej-jan.barski@city.ac.uk
**Institution**: City, University of London

## License
[To be determined]

## Requirements
- Python 3.x (for processing scripts)
- GeoPandas (vector data handling)
- Rasterio (raster creation and TIFF writing)
- Shapely (geometry operations)
- NumPy (array operations)
- Matplotlib (optional, for visualization)
- GDAL/OGR tools (optional)

## Status
🚧 Proof of concept phase - implementing vector to raster conversion workflow
