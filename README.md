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
│   └── 02-vector-to-raster-conversion.md
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

## Workflows

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
2. Spatial subset for proof of concept
3. Filter by DN threshold (high-value areas)
4. Determine raster parameters
5. Rasterize polygons
6. Create GeoTIFF output
7. Visualization and validation

Reference visualization: `images/Screenshot 2026-01-30 at 15.56.09.png` shows expected output with high-value areas highlighted.

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
