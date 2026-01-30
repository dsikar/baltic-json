# Contour Line Generation Workflow

## Project Context
This is the **third step** in the data processing pipeline. It takes the raster TIFF output from the vector-to-raster conversion and generates contour lines at regular intervals.

### Complete Pipeline
1. **Step 1**: Vector data cleaning (`prompts/01-vector-data-cleaning.md`)
2. **Step 2**: Vector to raster conversion (`prompts/02-vector-to-raster-conversion.md`)
3. **Step 3**: Contour line generation (this document)

### Background
- **Project**: Baltic vector data cleaning and conversion project
- **Repository**: baltic-json (GitHub: dsikar/baltic-json)
- **Related Documentation**:
  - See `README.md` for project overview
  - See `prompts/02-vector-to-raster-conversion.md` for raster creation
  - See `work-diary.md` for project history

## Overview
Generate contour lines (isolines) from a raster TIFF file based on DN (Digital Number) values. Contours represent boundaries between value classes at regular intervals of 25, creating 10 classification levels.

## Input Data
- **File**: `output/test_raster.tif` (or similar, from Step 2)
- **Format**: GeoTIFF with single band
- **Value Range**: 0-255 (DN values)
- **Data Type**: UInt8 or UInt16
- **CRS**: Projected coordinates (should be embedded in TIFF)
- **Geographic Area**: Scotland and NE England (or subset for POC)

## Contour Specifications

### Classification Scheme
- **Number of Classes**: 10
- **Interval**: 25 DN units
- **Contour Levels**: 25, 50, 75, 100, 125, 150, 175, 200, 225, 250

### Contour Classes
```
Class  1:   0 -  25
Class  2:  25 -  50
Class  3:  50 -  75
Class  4:  75 - 100
Class  5: 100 - 125
Class  6: 125 - 150
Class  7: 150 - 175
Class  8: 175 - 200
Class  9: 200 - 225
Class 10: 225 - 255
```

## Workflow Steps

### 1. Load and Validate Raster
- Read TIFF file using Rasterio
- Validate data type and value range
- Check CRS information
- Display basic statistics:
  - Min/max values
  - Value distribution
  - NoData handling
  - Raster dimensions

### 2. Prepare Data for Contouring
- Extract raster array
- Handle NoData values (mask or set to appropriate value)
- Create coordinate arrays (X, Y) from geotransform
- Verify data is suitable for contouring (not too sparse, appropriate resolution)

### 3. Generate Contour Lines
- Calculate contour lines at specified intervals (25, 50, 75, ..., 250)
- Options for contour generation:
  - **Option A**: Use GDAL contour utilities
  - **Option B**: Use matplotlib.pyplot.contour
  - **Option C**: Use scikit-image contour finding
  - **Option D**: Use rasterio.features.shapes with classification

### 4. Convert Contours to Vector Format
- Convert contour arrays/geometries to vector format
- Create LineString geometries for each contour level
- Assign attributes:
  - Contour level (DN value)
  - Class number (1-10)
  - Class range (e.g., "25-50")
- Set CRS to match input raster

### 5. Simplify and Clean Contours
- Remove very short contour segments (artifacts)
- Simplify geometries to reduce vertex count
- Smooth contours if needed (optional)
- Remove duplicates or overlapping segments

### 6. Create Output Files
- Save as GeoJSON with all contour lines
- Optional: Separate files per class/level
- Optional: Create styled visualization (colored by class)

### 7. Validation and Visualization
- Check contour topology
- Verify contour values are correct
- Create preview map showing all contours
- Color-code by class for visual inspection

## Output Requirements

### Primary Output
- **File**: `output/contours.geojson`
- **Format**: GeoJSON FeatureCollection
- **Geometry Type**: LineString or MultiLineString
- **Properties**:
  - `level`: Contour DN value (25, 50, 75, ...)
  - `class`: Class number (1-10)
  - `class_range`: Human-readable range (e.g., "25-50")
  - `class_label`: Optional descriptive label
- **CRS**: Same as input raster

### Optional Outputs
- `output/contours_class_{N}.geojson` - Separate file per class
- `output/contours_preview.png` - Visualization with color coding
- `output/contours_styled.qml` - QGIS style file (optional)

### Metadata/Report
- Processing parameters used
- Number of contours per level
- Total contour length by class
- Value distribution statistics
- Processing time

## Technical Specifications

### Python Libraries Required
- `rasterio` - Raster reading
- `geopandas` - Vector output
- `shapely` - Geometry operations
- `numpy` - Array operations
- `matplotlib` (optional) - Contour generation and visualization
- `scikit-image` (optional) - Alternative contour finding
- `gdal/osgeo` (optional) - GDAL contour tools

### Key Functions Needed
```python
1. load_raster(filepath) -> (array, transform, crs, metadata)
2. prepare_coordinate_grids(array, transform) -> (X, Y)
3. generate_contours(array, X, Y, levels) -> contour_data
4. contours_to_geodataframe(contour_data, levels, crs) -> GeoDataFrame
5. simplify_contours(gdf, tolerance) -> GeoDataFrame
6. assign_contour_attributes(gdf, levels) -> GeoDataFrame
7. export_contours(gdf, output_path)
8. visualize_contours(gdf, output_png_path)
```

## Configuration Parameters

### Adjustable Settings
- `contour_levels`: List of DN values for contours [25, 50, 75, ..., 250]
- `interval`: Contour interval (25)
- `min_length`: Minimum contour segment length to keep (remove artifacts)
- `simplify_tolerance`: Douglas-Peucker simplification tolerance (optional)
- `smooth_iterations`: Number of smoothing iterations (optional, 0 = none)
- `output_format`: 'geojson', 'shapefile', 'gpkg'
- `separate_by_class`: Boolean - create separate files per class

### Contour Styling (for visualization)
```python
class_colors = {
    1: '#f7fbff',  # Very light blue
    2: '#deebf7',
    3: '#c6dbef',
    4: '#9ecae1',
    5: '#6baed6',
    6: '#4292c6',
    7: '#2171b5',
    8: '#08519c',
    9: '#08306b',
    10: '#041e42'  # Very dark blue
}
```

## Success Criteria
- Contour lines successfully generated at all specified levels
- Contours are topologically valid (no self-intersections)
- Output file loads correctly in GIS software (QGIS, ArcGIS)
- Contours align with raster data visually
- Class attributes correctly assigned
- CRS metadata correctly embedded

## Validation Steps
1. Open contours in QGIS/GIS viewer
2. Overlay contours on original raster
3. Verify contour values match raster values at those locations
4. Check for:
   - Missing contours
   - Incorrect contour levels
   - Topology errors
   - Appropriate simplification
5. Verify attribute table has all expected fields

## Notes for Implementation
- Start with basic contour generation (no smoothing/simplification)
- GDAL's `gdal_contour` is very robust - consider using it first
- If using matplotlib, contours need to be converted to Shapely geometries
- Handle edge effects (contours at raster boundaries)
- Consider memory usage for large rasters - may need tiling
- NoData areas should not generate contours

## Example Code Snippet
```python
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape
import numpy as np

# Load raster
with rasterio.open('output/test_raster.tif') as src:
    array = src.read(1)
    transform = src.transform
    crs = src.crs

# Classify into 10 classes
classified = np.digitize(array, bins=[25, 50, 75, 100, 125, 150, 175, 200, 225, 250])

# Generate contours using GDAL or matplotlib
# ... implementation details ...
```

## Expected Deliverables

### 1. Python Script
- Filename: `scripts/generate_contours.py`
- Configurable parameters at top
- Command-line arguments for input/output paths
- Progress logging
- Error handling

### 2. Output Files
- `output/contours.geojson` - All contour lines
- `output/contours_preview.png` - Visualization
- `output/contours_report.txt` - Statistics

### 3. Documentation
- Update `work-diary.md` with:
  - Parameters used
  - Number of contours generated
  - Issues encountered
  - Results and observations

## Alternative: Using GDAL Command Line
```bash
# Generate contours using GDAL
gdal_contour -a DN -i 25 \
  -f "GeoJSON" \
  output/test_raster.tif \
  output/contours.geojson

# This creates contours at intervals of 25
# -a DN: attribute name for contour value
# -i 25: interval of 25
```

## Future Enhancements
- Contour smoothing algorithms
- Index contours (every 5th contour thicker/labeled)
- Automatic labeling of contour values
- Hatching for elevation bands
- 3D visualization
- Contour interpolation between levels
- Integration with interactive web maps

## Quick Start for Agent
```bash
# 1. Verify input raster exists
ls -lh output/test_raster.tif

# 2. Check GDAL availability
gdal_contour --version
# OR use Python libraries

# 3. Test with single contour level first
gdal_contour -a DN -fl 150 output/test_raster.tif output/test_contour.geojson

# 4. Generate all contours
# Implement full script with all 10 levels

# 5. Validate in QGIS
qgis output/test_raster.tif output/contours.geojson
```

## Reference Information
- **Corresponding Author**: Blazej Jan Barski (blazej-jan.barski@city.ac.uk)
- **Repository**: github.com:dsikar/baltic-json.git
- **Current Branch**: main
- **Previous Step**: Vector to raster conversion (prompts/02-vector-to-raster-conversion.md)
