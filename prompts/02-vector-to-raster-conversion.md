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
Convert GeoJSON vector polygon data to a raster TIFF image with quantized DN values. This proof of concept:
1. Takes vector polygons with DN (Digital Number) values (0-255)
2. Extracts a spatial subset and saves as GeoJSON
3. **Quantizes DN values to 10 bucket centers** (12.5, 37.5, 62.5, ..., 240.0)
4. Rasterizes quantized polygons into a TIFF image
5. Produces output ready for contour generation

**Key Feature**: DN values are quantized to bucket centers (intervals of 25), preparing data for 10-class contour generation.

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
- **IMPORTANT**: Save subset as GeoJSON file: `output/subset_extract.json`
  - This preserves the vector data for this region
  - Can be used for validation or further processing

### 3. Quantize DN Values
**Key Processing Step**: Quantize DN values to bucket centers for 10-class classification.

- **Bucket Centers** (intervals of 25):
  - Bucket 1 (0-25): center = 12.5
  - Bucket 2 (25-50): center = 37.5
  - Bucket 3 (50-75): center = 62.5
  - Bucket 4 (75-100): center = 87.5
  - Bucket 5 (100-125): center = 112.5
  - Bucket 6 (125-150): center = 137.5
  - Bucket 7 (150-175): center = 162.5
  - Bucket 8 (175-200): center = 187.5
  - Bucket 9 (200-225): center = 212.5
  - Bucket 10 (225-255): center = 240.0

- **Quantization Logic**:
  ```python
  # Map each DN value to nearest bucket center
  bucket_centers = [12.5, 37.5, 62.5, 87.5, 112.5, 137.5, 162.5, 187.5, 212.5, 240.0]

  def quantize_dn(dn_value):
      if dn_value < 25: return 12.5
      elif dn_value < 50: return 37.5
      elif dn_value < 75: return 62.5
      elif dn_value < 100: return 87.5
      elif dn_value < 125: return 112.5
      elif dn_value < 150: return 137.5
      elif dn_value < 175: return 162.5
      elif dn_value < 200: return 187.5
      elif dn_value < 225: return 212.5
      else: return 240.0
  ```

- Apply quantization to all polygon DN values
- Update DN property in GeoDataFrame with quantized values

### 4. Data Filtering (Optional for POC)
- Filter polygons by DN value threshold (before or after quantization)
- Remove null/invalid geometries
- Remove very small artifacts if needed
- Keep only high-value areas for visualization

### 5. Determine Raster Parameters
- Calculate bounding box (extent) of all geometries
- Determine appropriate pixel resolution
  - Based on area size and desired detail level
  - Consider: 10m, 50m, 100m resolution options
- Calculate raster dimensions (rows x columns)

### 6. Rasterize Polygons
- Create empty raster array with calculated dimensions
- Burn polygon geometries into raster
- **Assign pixel values using quantized DN values**:
  - Use the quantized bucket center values (12.5, 37.5, 62.5, ..., 240.0)
  - Each pixel gets the quantized DN value from its polygon
  - Background/NoData pixels = 0 or appropriate NoData value

### 7. Create TIFF Output
- Write raster array to GeoTIFF format
- Embed coordinate reference system
- Set appropriate metadata:
  - NoData value
  - Compression (e.g., LZW)
  - Geotransform (pixel size and origin)
- Validate output file

### 8. Visualization Check
- Load created TIFF
- Display basic statistics
- Optionally create a preview image (PNG)
- Compare with expected result (reference screenshot)

## Output Requirements

### Primary Outputs

#### 1. Spatial Subset (Vector)
- **File**: `output/subset_extract.json`
- **Format**: GeoJSON FeatureCollection
- **Purpose**: Preserves vector data for the extracted spatial region
- **Properties**: Original DN values before quantization
- **CRS**: Same as input vector data

#### 2. Rasterized Output
- **File**: `output/rasterized_polygons.tif`
- **Format**: GeoTIFF
- **Bands**: Single band
- **Data Type**: Float32 (to store quantized values like 12.5, 37.5, etc.)
- **Pixel Values**: Quantized bucket centers (12.5, 37.5, 62.5, ..., 240.0)
- **Compression**: LZW recommended
- **CRS**: Same as input vector data

### Metadata/Log
- Processing parameters used
- Input feature count and subset feature count
- Original DN value range and quantized values used
- Output raster dimensions
- Pixel resolution
- Extent coordinates
- Quantization bucket centers applied
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
```python
1. load_vector_data(filepath) -> GeoDataFrame
2. crop_to_bbox(gdf, bbox) -> GeoDataFrame
3. save_subset_json(gdf, output_path) -> None
4. quantize_dn_values(gdf) -> GeoDataFrame
   # Maps DN values to bucket centers [12.5, 37.5, 62.5, ..., 240.0]
5. filter_by_threshold(gdf, dn_threshold) -> GeoDataFrame
6. calculate_raster_params(gdf, resolution) -> (bounds, shape, transform)
7. rasterize_polygons(gdf, shape, transform) -> array
   # Uses quantized DN values for pixel values
8. write_geotiff(array, transform, crs, output_path)
9. create_preview(tiff_path, output_png_path)
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
- **CRITICAL**: Quantize DN values to bucket centers before rasterization
- Save spatial subset as GeoJSON (`output/subset_extract.json`)
- Use Float32 data type for TIFF to store decimal bucket centers (12.5, 37.5, etc.)
- Use moderate resolution (e.g., 100m) for faster processing
- Don't over-optimize initially - focus on working end-to-end pipeline
- Document quantization mapping (original DN → bucket center)
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
- `output/subset_extract.json` - Spatial subset in GeoJSON format (vector data preserved)
- `output/test_raster.tif` - The rasterized TIFF file with quantized DN values
- `output/test_raster_preview.png` (optional) - Quick visualization
- `output/processing_log.txt` - Statistics, quantization details, and parameters used

### 3. Documentation
- Update `work-diary.md` with:
  - Spatial subset bounds and feature count
  - Quantization applied (original DN range → bucket centers)
  - Parameters used (resolution, bbox, etc.)
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
