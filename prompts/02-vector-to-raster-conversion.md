# Vector to Raster Conversion Workflow

## Project Context
This is a **proof of concept** workflow to convert vector polygon data (derived from raster sources) into a raster TIFF image. The goal is to visualize high-value areas that exceed a user-defined threshold.

### Background
- **Project**: Baltic vector data cleaning and conversion project
- **Repository**: baltic-json (GitHub: dsikar/baltic-json)
- **Related Documentation**:
  - See `README.md` for project overview
  - See `prompts/01-vector-data-cleaning.md` for data cleaning workflow
  - See `work-diary.md` for project history
  - Reference visualization: `images/Screenshot 2026-01-30 at 15.56.09.png`

### What We're Trying to Achieve
The reference screenshot (`images/Screenshot 2026-01-30 at 15.56.09.png`) shows the **desired output**: a map of Scotland and NE England where black areas represent polygons with the highest DN values (past a threshold). These high-value areas are the features of interest that need to be converted from vector to raster format.

## Overview
Convert GeoJSON vector polygon data to a raster TIFF image. This proof of concept:
1. Takes vector polygons with DN (Digital Number) values
2. Filters for high-value areas (above threshold)
3. Rasterizes these polygons into a TIFF image
4. Produces output similar to the reference visualization

## Input Data
- **File**: `data/kjbjkbjk-2.json`
- **Format**: GeoJSON FeatureCollection
- **Size**: ~20MB
- **Geometry Type**: Polygon (with some null geometries present)
- **Properties**: Each feature has a "DN" property (Digital Number from original raster)
- **DN Value Range**: 0-255 (observed values include 0, 164, 181, 249, 253, 254, 255)
- **Coordinate System**: Projected coordinates (large values like 2522509, appears to be UTM or similar)
- **Geographic Area**: Scotland and NE England
- **Data Characteristics**:
  - Contains many features with `null` geometries (need filtering)
  - Mix of large polygons (landmasses) and small artifacts
  - High DN values (253-255) represent areas of interest
  - Some DN values may represent NoData (e.g., 0)

### Sample Data Structure
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[2522509.579, 9851483.727], ...]]
      },
      "properties": {"DN": 253}
    },
    {
      "type": "Feature",
      "geometry": null,
      "properties": {"DN": 255}
    },
    ...
  ]
}
```

## Workflow Steps

### 1. Load and Validate Vector Data
- Read GeoJSON file using GeoPandas
- Validate geometry types
- Check coordinate reference system (CRS)
- Display basic statistics (feature count, DN value range, total area)

### 2. Spatial Subset for POC
- Define a bounding box for a small test area
  - Option A: Manually specify coordinates
  - Option B: Select features within a region
  - Option C: Take first N features
- Crop vector data to subset area
- Verify subset contains representative data (mix of geometries, DN values)
- Save subset as intermediate file (optional)

### 3. Data Filtering (Optional for POC)
- Filter polygons by DN value threshold
- Remove null/invalid geometries
- Remove very small artifacts if needed
- Keep only high-value areas for visualization

### 4. Determine Raster Parameters
- Calculate bounding box (extent) of all geometries
- Determine appropriate pixel resolution
  - Based on area size and desired detail level
  - Consider: 10m, 50m, 100m resolution options
- Calculate raster dimensions (rows x columns)

### 5. Rasterize Polygons
- Create empty raster array with calculated dimensions
- Burn polygon geometries into raster
- Assign pixel values:
  - Option A: Binary (1 for high-value areas, 0 for background)
  - Option B: Use original DN values
  - Option C: Categorical (different values for DN ranges)

### 6. Create TIFF Output
- Write raster array to GeoTIFF format
- Embed coordinate reference system
- Set appropriate metadata:
  - NoData value
  - Compression (e.g., LZW)
  - Geotransform (pixel size and origin)
- Validate output file

### 7. Visualization Check
- Load created TIFF
- Display basic statistics
- Optionally create a preview image (PNG)
- Compare with expected result (reference screenshot)

## Output Requirements

### Primary Output
- **File**: `output/rasterized_polygons.tif`
- **Format**: GeoTIFF
- **Bands**: Single band
- **Data Type**: UInt8 or UInt16 (depending on value range)
- **Compression**: LZW recommended
- **CRS**: Same as input vector data

### Metadata/Log
- Processing parameters used
- Input feature count
- Output raster dimensions
- Pixel resolution
- Extent coordinates
- Processing time

### Optional Outputs
- Preview image (PNG) for quick visualization
- Histogram of pixel values
- Simple statistics report

## Technical Specifications

### Python Libraries Required
- `geopandas` - Vector data handling
- `rasterio` - Raster creation and TIFF writing
- `shapely` - Geometry operations
- `numpy` - Array operations
- `matplotlib` (optional) - Visualization

### Key Functions Needed
```
1. load_vector_data(filepath) -> GeoDataFrame
2. crop_to_bbox(gdf, bbox) -> GeoDataFrame
3. filter_by_threshold(gdf, dn_threshold) -> GeoDataFrame
4. calculate_raster_params(gdf, resolution) -> (bounds, shape, transform)
5. rasterize_polygons(gdf, shape, transform) -> array
6. write_geotiff(array, transform, crs, output_path)
7. create_preview(tiff_path, output_png_path)
```

## Configuration Parameters

### Adjustable Settings
- `crop_bbox`: Bounding box for spatial subset (minx, miny, maxx, maxy) - None for full extent
- `dn_threshold`: Minimum DN value to include (e.g., 250, 253, 254)
- `pixel_resolution`: Size in map units (e.g., 10, 50, 100)
- `output_value_type`: 'binary', 'original_dn', 'categorical'
- `nodata_value`: Background value (e.g., 0, 255, -9999)
- `compression`: 'lzw', 'deflate', 'none'

## Success Criteria
- TIFF file successfully created
- Output displays correctly in GIS software (QGIS, ArcGIS)
- Raster extent matches vector data extent
- High-value areas are clearly visible
- CRS metadata correctly embedded
- File size is reasonable

## Validation Steps
1. Open TIFF in QGIS/GIS viewer
2. Verify CRS matches input data
3. Check that polygon areas are rasterized correctly
4. Verify pixel values are as expected
5. Compare visual output with reference screenshot

## Notes for Proof of Concept
- Start with simple binary rasterization (high-value = 1, background = 0)
- Use moderate resolution (e.g., 100m) for faster processing
- Don't over-optimize initially - focus on working end-to-end pipeline
- Document any assumptions made
- Note any issues or artifacts for future refinement
- **IMPORTANT**: Work on a spatial subset first (small area) to iterate quickly

## Expected Deliverables

### 1. Python Script
- Filename: `scripts/vector_to_raster.py` (or similar)
- Configurable parameters at top of script
- Well-commented code
- Error handling for common issues
- Progress logging/print statements

### 2. Output Files
- `output/test_raster.tif` - The rasterized TIFF file
- `output/test_raster_preview.png` (optional) - Quick visualization
- `output/processing_log.txt` - Statistics and parameters used

### 3. Documentation
- Update `work-diary.md` with:
  - Parameters used
  - Issues encountered
  - Results and observations
  - Comparison with reference screenshot

### 4. Verification
- Visual check: Does output resemble `images/Screenshot 2026-01-30 at 15.56.09.png`?
- Technical check: Valid GeoTIFF with correct CRS
- Document any differences from expected output

## Quick Start for Agent
```bash
# 1. Check Python environment
python3 --version
pip list | grep -E 'geopandas|rasterio|shapely'

# 2. Install if needed
pip install geopandas rasterio shapely matplotlib

# 3. Explore the data first
# Read data/kjbjkbjk-2.json, check CRS, bounds, DN values

# 4. Create output directory
mkdir -p output

# 5. Implement the script in steps:
#    - Load data
#    - Filter null geometries
#    - Crop to small test area (POC)
#    - Rasterize
#    - Save TIFF

# 6. Test and iterate
```

## Reference Information
- **Corresponding Author**: Blazej Jan Barski (blazej-jan.barski@city.ac.uk)
- **Repository**: github.com:dsikar/baltic-json.git
- **Current Branch**: main

## Future Enhancements
- Multi-band output (different DN ranges in separate bands)
- Anti-aliasing for smoother edges
- Custom color mapping
- Integration with data cleaning pipeline
- Batch processing multiple files
- Automatic resolution calculation based on polygon density
