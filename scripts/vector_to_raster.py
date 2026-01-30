#!/usr/bin/env python3
"""
Vector to Raster Conversion Script

Converts GeoJSON vector polygon data to raster TIFF format.
Part of the Baltic vector data cleaning and conversion project.

Usage:
    python scripts/vector_to_raster.py

Author: Baltic data processing project
Date: 2026-01-30
"""

import sys
import time
from pathlib import Path
from datetime import datetime

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import rasterize
from rasterio.transform import from_bounds
import matplotlib.pyplot as plt
from shapely.geometry import box

# ============================================================================
# CONFIGURATION PARAMETERS
# ============================================================================

# Input/Output Paths
INPUT_FILE = 'data/kjbjkbjk-2.json'
OUTPUT_DIR = 'output'

# Spatial Extent
# POC: Use crop_bbox for small test area (50km x 20km subset)
# Production: Set crop_bbox = None for full extent
# CROP_BBOX = (2500000, 9830000, 2550000, 9850000)  # (minx, miny, maxx, maxy)
CROP_BBOX = None  # Full extent processing

# Data Filtering
DN_THRESHOLD = 253  # Minimum DN value to include (253, 254, 255)

# Raster Parameters
# PIXEL_RESOLUTION = 100  # Pixel size in map units (meters)
PIXEL_RESOLUTION = 50  # Higher resolution for full extent

# Output Configuration
OUTPUT_VALUE_TYPE = 'original_dn'  # Options: 'binary', 'original_dn', 'categorical'
NODATA_VALUE = 0  # Background value
COMPRESSION = 'lzw'  # Options: 'lzw', 'deflate', 'none'

# Coordinate Reference System
# EPSG:32631 = UTM Zone 31N (covers Scotland and NE England)
CRS = 'EPSG:32631'

# Output Files
if CROP_BBOX is None:
    OUTPUT_TIFF = f'{OUTPUT_DIR}/full_extent_raster.tif'
    OUTPUT_PNG = f'{OUTPUT_DIR}/full_extent_preview.png'
else:
    OUTPUT_TIFF = f'{OUTPUT_DIR}/test_raster.tif'
    OUTPUT_PNG = f'{OUTPUT_DIR}/test_raster_preview.png'
OUTPUT_LOG = f'{OUTPUT_DIR}/processing_log.txt'

# ============================================================================
# CORE FUNCTIONS
# ============================================================================

def load_vector_data(filepath, crs):
    """
    Load GeoJSON vector data and set CRS.

    Args:
        filepath (str): Path to GeoJSON file
        crs (str): Coordinate reference system (e.g., 'EPSG:32631')

    Returns:
        GeoDataFrame: Loaded vector data
    """
    print(f"\n[1/7] Loading vector data from {filepath}...")
    start_time = time.time()

    gdf = gpd.read_file(filepath)

    # Set CRS if not already set
    if gdf.crs is None:
        print(f"  Setting CRS to {crs}")
        gdf = gdf.set_crs(crs)
    else:
        print(f"  CRS: {gdf.crs}")

    elapsed = time.time() - start_time
    print(f"  Loaded {len(gdf)} features in {elapsed:.2f} seconds")

    return gdf


def validate_and_report(gdf, stage_name):
    """
    Print validation statistics for current GeoDataFrame.

    Args:
        gdf (GeoDataFrame): Data to validate
        stage_name (str): Name of current processing stage

    Returns:
        dict: Statistics dictionary
    """
    print(f"\n  Validation: {stage_name}")
    print(f"  - Feature count: {len(gdf)}")

    if len(gdf) > 0:
        # Geometry statistics
        null_count = gdf.geometry.isna().sum()
        print(f"  - Null geometries: {null_count}")

        # DN value statistics
        if 'DN' in gdf.columns:
            dn_min = gdf['DN'].min()
            dn_max = gdf['DN'].max()
            dn_mean = gdf['DN'].mean()
            print(f"  - DN range: {dn_min} - {dn_max} (mean: {dn_mean:.2f})")

        # Spatial extent
        if not gdf.empty and gdf.geometry.notna().any():
            minx, miny, maxx, maxy = gdf.total_bounds
            print(f"  - Extent: ({minx:.0f}, {miny:.0f}) to ({maxx:.0f}, {maxy:.0f})")
            width = maxx - minx
            height = maxy - miny
            print(f"  - Dimensions: {width:.0f}m x {height:.0f}m")

    stats = {
        'feature_count': len(gdf),
        'null_geometries': null_count if len(gdf) > 0 else 0,
        'bounds': gdf.total_bounds.tolist() if len(gdf) > 0 and gdf.geometry.notna().any() else None
    }

    return stats


def filter_null_geometries(gdf):
    """
    Remove features with null geometries.

    Args:
        gdf (GeoDataFrame): Input data

    Returns:
        GeoDataFrame: Filtered data
    """
    print("\n[2/7] Filtering null geometries...")
    initial_count = len(gdf)

    # Remove null geometries
    gdf = gdf[gdf.geometry.notna()].copy()

    removed_count = initial_count - len(gdf)
    print(f"  Removed {removed_count} null geometries")
    print(f"  Remaining features: {len(gdf)}")

    return gdf


def crop_to_bbox(gdf, bbox):
    """
    Crop GeoDataFrame to bounding box.

    Args:
        gdf (GeoDataFrame): Input data
        bbox (tuple or None): (minx, miny, maxx, maxy) or None for full extent

    Returns:
        GeoDataFrame: Cropped data
    """
    print("\n[3/7] Spatial cropping...")

    if bbox is None:
        print("  Using full extent (no cropping)")
        return gdf

    minx, miny, maxx, maxy = bbox
    print(f"  Cropping to bbox: ({minx}, {miny}) to ({maxx}, {maxy})")

    initial_count = len(gdf)

    # Use spatial indexing for efficient cropping
    gdf = gdf.cx[minx:maxx, miny:maxy].copy()

    remaining_count = len(gdf)
    removed_count = initial_count - remaining_count
    print(f"  Removed {removed_count} features outside bbox")
    print(f"  Remaining features: {remaining_count}")

    return gdf


def filter_by_dn_threshold(gdf, threshold):
    """
    Filter features by DN value threshold.

    Args:
        gdf (GeoDataFrame): Input data
        threshold (int): Minimum DN value to keep

    Returns:
        GeoDataFrame: Filtered data
    """
    print(f"\n[4/7] Filtering by DN threshold >= {threshold}...")
    initial_count = len(gdf)

    # Filter by DN threshold
    gdf = gdf[gdf['DN'] >= threshold].copy()

    remaining_count = len(gdf)
    removed_count = initial_count - remaining_count
    print(f"  Removed {removed_count} features below threshold")
    print(f"  Remaining features: {remaining_count}")

    return gdf


def calculate_raster_params(gdf, resolution):
    """
    Calculate raster parameters from GeoDataFrame.

    Args:
        gdf (GeoDataFrame): Input data
        resolution (float): Pixel size in map units

    Returns:
        tuple: (bounds, shape, transform)
    """
    print(f"\n[5/7] Calculating raster parameters (resolution: {resolution}m)...")

    # Get bounds
    minx, miny, maxx, maxy = gdf.total_bounds
    bounds = (minx, miny, maxx, maxy)
    print(f"  Extent: ({minx:.0f}, {miny:.0f}) to ({maxx:.0f}, {maxy:.0f})")

    # Calculate dimensions
    width = maxx - minx
    height = maxy - miny
    cols = int(np.ceil(width / resolution))
    rows = int(np.ceil(height / resolution))
    shape = (rows, cols)

    print(f"  Map dimensions: {width:.0f}m x {height:.0f}m")
    print(f"  Raster dimensions: {cols} cols x {rows} rows")
    print(f"  Total pixels: {cols * rows:,}")

    # Check for unreasonably large rasters
    if cols * rows > 100_000_000:
        print(f"  WARNING: Large raster ({cols * rows:,} pixels). Consider increasing resolution.")

    # Create affine transform
    transform = from_bounds(minx, miny, maxx, maxy, cols, rows)
    print(f"  Transform: {transform}")

    return bounds, shape, transform


def rasterize_polygons(gdf, transform, shape, value_type):
    """
    Rasterize polygon geometries to array.

    Args:
        gdf (GeoDataFrame): Input data
        transform (Affine): Raster transform
        shape (tuple): (rows, cols)
        value_type (str): 'binary', 'original_dn', or 'categorical'

    Returns:
        numpy.ndarray: Rasterized array
    """
    print(f"\n[6/7] Rasterizing polygons (value_type: {value_type})...")
    start_time = time.time()

    # Prepare geometry-value pairs based on value_type
    if value_type == 'binary':
        # All features get value 1
        shapes = ((geom, 1) for geom in gdf.geometry)
    elif value_type == 'original_dn':
        # Use original DN values
        shapes = ((geom, int(dn)) for geom, dn in zip(gdf.geometry, gdf['DN']))
    elif value_type == 'categorical':
        # Map DN ranges to categories
        # Category 1: DN 253, Category 2: DN 254, Category 3: DN 255
        def dn_to_category(dn):
            if dn == 253:
                return 1
            elif dn == 254:
                return 2
            elif dn == 255:
                return 3
            else:
                return 0
        shapes = ((geom, dn_to_category(dn)) for geom, dn in zip(gdf.geometry, gdf['DN']))
    else:
        raise ValueError(f"Unknown value_type: {value_type}")

    # Rasterize
    raster_array = rasterize(
        shapes=shapes,
        out_shape=shape,
        transform=transform,
        fill=0,
        dtype=np.uint8,
        all_touched=False
    )

    elapsed = time.time() - start_time

    # Statistics
    non_zero_count = np.count_nonzero(raster_array)
    total_pixels = raster_array.size
    percentage = (non_zero_count / total_pixels) * 100

    print(f"  Rasterization complete in {elapsed:.2f} seconds")
    print(f"  Non-zero pixels: {non_zero_count:,} ({percentage:.2f}%)")
    print(f"  Value range: {raster_array.min()} - {raster_array.max()}")

    return raster_array


def write_geotiff(array, transform, crs, output_path, nodata_value, compression):
    """
    Write raster array to GeoTIFF file.

    Args:
        array (numpy.ndarray): Raster data
        transform (Affine): Raster transform
        crs (str): Coordinate reference system
        output_path (str): Output file path
        nodata_value (int): NoData value
        compression (str): Compression type
    """
    print(f"\n[7/7] Writing GeoTIFF to {output_path}...")
    start_time = time.time()

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Define profile
    profile = {
        'driver': 'GTiff',
        'dtype': array.dtype,
        'count': 1,
        'width': array.shape[1],
        'height': array.shape[0],
        'transform': transform,
        'crs': crs,
        'nodata': nodata_value,
        'compress': compression,
        'tiled': True,
        'blockxsize': 256,
        'blockysize': 256
    }

    # Write file
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(array, 1)

        # Add metadata
        dst.update_tags(
            AREA_OR_POINT='Area',
            CREATED=datetime.now().isoformat(),
            SOURCE='Baltic vector data processing'
        )

    # Get file size
    file_size = Path(output_path).stat().st_size / (1024 * 1024)  # MB
    elapsed = time.time() - start_time

    print(f"  File written in {elapsed:.2f} seconds")
    print(f"  File size: {file_size:.2f} MB")

    # Verify file can be opened
    with rasterio.open(output_path) as src:
        print(f"  Verified: {src.count} band(s), {src.width}x{src.height} pixels")
        print(f"  CRS: {src.crs}")


def create_preview_png(tiff_path, output_png_path):
    """
    Create PNG preview of raster.

    Args:
        tiff_path (str): Path to input TIFF
        output_png_path (str): Path to output PNG
    """
    print(f"\nCreating preview image: {output_png_path}")

    # Read raster
    with rasterio.open(tiff_path) as src:
        array = src.read(1)

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot
    im = ax.imshow(array, cmap='gray', interpolation='nearest')
    ax.set_title(f'Raster Preview\n{Path(tiff_path).name}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Column')
    ax.set_ylabel('Row')

    # Add colorbar
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label('Pixel Value', rotation=270, labelpad=20)

    # Add statistics text
    non_zero = np.count_nonzero(array)
    total = array.size
    stats_text = f'Shape: {array.shape}\nNon-zero pixels: {non_zero:,} ({100*non_zero/total:.2f}%)\nValue range: {array.min()}-{array.max()}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    # Save
    plt.tight_layout()
    plt.savefig(output_png_path, dpi=150, bbox_inches='tight')
    plt.close()

    print(f"  Preview saved successfully")


def write_processing_report(params, stats, log_path):
    """
    Write processing report to log file.

    Args:
        params (dict): Processing parameters
        stats (dict): Processing statistics
        log_path (str): Output log file path
    """
    print(f"\nWriting processing report: {log_path}")

    # Ensure output directory exists
    Path(log_path).parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("VECTOR TO RASTER CONVERSION PROCESSING REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Processing Date: {datetime.now().isoformat()}\n\n")

        f.write("CONFIGURATION PARAMETERS\n")
        f.write("-" * 80 + "\n")
        for key, value in params.items():
            f.write(f"{key:25s}: {value}\n")
        f.write("\n")

        f.write("PROCESSING STATISTICS\n")
        f.write("-" * 80 + "\n")
        for stage, stage_stats in stats.items():
            f.write(f"\n{stage}:\n")
            for key, value in stage_stats.items():
                f.write(f"  {key:20s}: {value}\n")

        f.write("\n" + "=" * 80 + "\n")

    print("  Report written successfully")


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """Main processing pipeline."""
    print("=" * 80)
    print("VECTOR TO RASTER CONVERSION")
    print("=" * 80)

    overall_start_time = time.time()

    # Track statistics
    stats = {}

    # Parameters dictionary for reporting
    params = {
        'INPUT_FILE': INPUT_FILE,
        'CROP_BBOX': CROP_BBOX,
        'DN_THRESHOLD': DN_THRESHOLD,
        'PIXEL_RESOLUTION': PIXEL_RESOLUTION,
        'OUTPUT_VALUE_TYPE': OUTPUT_VALUE_TYPE,
        'NODATA_VALUE': NODATA_VALUE,
        'COMPRESSION': COMPRESSION,
        'CRS': CRS,
        'OUTPUT_TIFF': OUTPUT_TIFF
    }

    try:
        # 1. Load data
        gdf = load_vector_data(INPUT_FILE, CRS)
        stats['1_loaded'] = validate_and_report(gdf, "After loading")

        # 2. Filter null geometries
        gdf = filter_null_geometries(gdf)
        stats['2_filtered_nulls'] = validate_and_report(gdf, "After filtering nulls")

        # 3. Spatial crop
        gdf = crop_to_bbox(gdf, CROP_BBOX)
        stats['3_cropped'] = validate_and_report(gdf, "After cropping")

        # Check if any features remain
        if len(gdf) == 0:
            print("\nERROR: No features remaining after cropping!")
            print("  Check that CROP_BBOX intersects with the data extent.")
            sys.exit(1)

        # 4. Filter by DN threshold
        gdf = filter_by_dn_threshold(gdf, DN_THRESHOLD)
        stats['4_filtered_dn'] = validate_and_report(gdf, "After DN filtering")

        # Check if any features remain
        if len(gdf) == 0:
            print(f"\nERROR: No features remaining after filtering DN >= {DN_THRESHOLD}!")
            print("  Try lowering the DN_THRESHOLD value.")
            sys.exit(1)

        # 5. Calculate raster parameters
        bounds, shape, transform = calculate_raster_params(gdf, PIXEL_RESOLUTION)
        stats['5_raster_params'] = {
            'bounds': bounds,
            'shape': shape,
            'resolution': PIXEL_RESOLUTION
        }

        # 6. Rasterize polygons
        raster_array = rasterize_polygons(gdf, transform, shape, OUTPUT_VALUE_TYPE)
        stats['6_rasterized'] = {
            'non_zero_pixels': int(np.count_nonzero(raster_array)),
            'total_pixels': int(raster_array.size),
            'min_value': int(raster_array.min()),
            'max_value': int(raster_array.max())
        }

        # 7. Write GeoTIFF
        write_geotiff(raster_array, transform, CRS, OUTPUT_TIFF, NODATA_VALUE, COMPRESSION)

        # 8. Create preview
        create_preview_png(OUTPUT_TIFF, OUTPUT_PNG)

        # 9. Write processing report
        overall_elapsed = time.time() - overall_start_time
        params['PROCESSING_TIME'] = f"{overall_elapsed:.2f} seconds"
        write_processing_report(params, stats, OUTPUT_LOG)

        # Summary
        print("\n" + "=" * 80)
        print("PROCESSING COMPLETE")
        print("=" * 80)
        print(f"Total processing time: {overall_elapsed:.2f} seconds")
        print(f"\nOutput files:")
        print(f"  - Raster TIFF: {OUTPUT_TIFF}")
        print(f"  - Preview PNG: {OUTPUT_PNG}")
        print(f"  - Processing log: {OUTPUT_LOG}")
        print("\nNext steps:")
        print("  1. Open the TIFF in QGIS/GIS viewer to verify")
        print("  2. Compare with reference screenshot")
        print("  3. Run 'gdalinfo' to check metadata")
        if CROP_BBOX is not None:
            print("  4. Set CROP_BBOX = None and PIXEL_RESOLUTION = 50 for full extent")
        print("=" * 80)

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
