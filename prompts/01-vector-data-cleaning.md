# Vector Data Cleaning Task

## Overview
Clean GeoJSON vector data that was derived from raster data. The input file contains polygon features with Digital Number (DN) properties from the original raster source.

## Input Data
- **File**: `data/kjbjkbjk-2.json`
- **Format**: GeoJSON FeatureCollection
- **Size**: ~20MB
- **Geometry Type**: Polygon
- **Properties**: DN (Digital Number values from raster)
- **Coordinate System**: Projected (appears to be UTM or similar)

## Cleaning Operations Required

### 1. Remove Invalid Geometries
- Remove features with `null` geometries
- Remove features with invalid polygon structures (unclosed rings, self-intersections)
- Validate coordinate arrays are properly formatted

### 2. Handle NoData Values
- Identify DN values that represent "no data" (commonly 0, 255, or specific values)
- Option to remove or flag these features
- Document which DN values are considered valid data

### 3. Remove Artifacts
- Remove very small polygons (likely rasterization artifacts)
  - Define minimum area threshold
- Remove sliver polygons (very thin polygons from pixel edges)
  - Define minimum width/area ratio
- Remove duplicate geometries

### 4. Topology Cleaning
- Simplify excessive vertices while maintaining shape
- Fix small gaps or overlaps between adjacent polygons
- Ensure polygon validity (right-hand rule, proper winding order)

### 5. Attribute Validation
- Ensure DN values are within expected range
- Remove features with missing or invalid DN values
- Validate data types

## Output Requirements
- Clean GeoJSON file with same structure
- Validation report showing:
  - Number of features removed by category
  - Statistics on DN value distribution
  - Area statistics (min, max, mean, total)
  - List of any warnings or issues
- Preserve original coordinate system

## Configuration Parameters
Parameters that may need adjustment:
- Minimum polygon area (m² or units²)
- Sliver ratio threshold
- NoData DN values to exclude
- Simplification tolerance
- Coordinate precision

## Success Criteria
- All geometries are valid
- No null or empty geometries
- File size reduced by removing invalid/artifact features
- All remaining features have valid DN values
- Clean data is ready for further analysis

## Notes
- Preserve features that represent legitimate small areas (not artifacts)
- Document any assumptions made during cleaning
- Ensure cleaning process is reproducible
