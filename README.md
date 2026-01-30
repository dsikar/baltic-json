# Baltic Vector Data Cleaning Project

## Overview
This project focuses on cleaning vector data derived from raster sources for the Baltic region. The workflow processes GeoJSON polygon features to remove invalid geometries, artifacts, and prepare clean data for further analysis.

## Project Structure
```
baltic-json/
├── data/               # Raw data files (not included in repository)
├── prompts/            # Task definition prompts
│   └── 01-vector-data-cleaning.md
└── work-diary.md       # Project work log
```

## Data
The project works with GeoJSON FeatureCollection data containing:
- **Geometry Type**: Polygon
- **Properties**: DN (Digital Number) values from raster source
- **Coordinate System**: Projected coordinates
- **Size**: ~20MB

**Note**: Raw data files are not included in this repository. Please do not contact the author for data access.

## Workflow
The cleaning process is defined in `prompts/01-vector-data-cleaning.md` and includes:
1. Removing invalid and null geometries
2. Handling NoData values
3. Removing rasterization artifacts
4. Topology cleaning
5. Attribute validation

## Contact
**Corresponding Author**: Blazej Jan Barski
**Email**: blazej-jan.barski@city.ac.uk
**Institution**: City, University of London

## License
[To be determined]

## Requirements
- Python 3.x (for processing scripts)
- GeoPandas, Shapely, or similar geospatial libraries
- GDAL/OGR tools (optional)

## Status
🚧 Project in initial planning phase
