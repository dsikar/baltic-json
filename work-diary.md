# Work Diary - Baltic Vector Data Cleaning Project

## 2026-01-30

### Initial Project Setup
**Time**: 15:50 UTC

#### Tasks Completed:
1. **Data Inspection**
   - Examined raw GeoJSON file: `data/kjbjkbjk-2.json` (~20MB)
   - Identified data structure: FeatureCollection with Polygon geometries
   - Properties: DN (Digital Number) values from raster source
   - Coordinate system: Projected coordinates (appears to be UTM or similar)

2. **Data Quality Assessment**
   - Identified multiple features with null geometries requiring cleanup
   - Observed DN values ranging from 0 to 255
   - Noted potential NoData values: 0, 253, 254, 255
   - Found mix of valid polygons and invalid/empty geometries

3. **Documentation Created**
   - **Prompt Definition**: Created `prompts/01-vector-data-cleaning.md`
     - Defined comprehensive cleaning workflow
     - Specified input data characteristics
     - Listed cleaning operations: invalid geometry removal, NoData handling, artifact removal, topology cleaning, attribute validation
     - Documented configurable parameters and success criteria

   - **README**: Created project README with:
     - Project overview and structure
     - Data description
     - Workflow summary
     - Contact information (Blazej Jan Barski as corresponding author)
     - Status indicators

   - **Git Configuration**: Created `.gitignore`
     - Excluded data directory from version control
     - Added note: "Do not contact author for data access"
     - Standard Python, Jupyter, IDE, and OS ignores

#### Next Steps:
- Refine cleaning parameters based on Baltic region context
- Determine specific DN values representing valid data vs. NoData
- Develop data cleaning script
- Implement validation reporting
- Test on sample data subset

#### Questions to Resolve:
- What is the specific context of this Baltic data? (Ocean depth, land cover, etc.)
- Which DN values represent NoData?
- What are acceptable minimum area thresholds?
- Should adjacent polygons with same DN be merged?

---

### Vector-to-Raster Conversion Workflow Development
**Time**: 16:00 UTC

#### Context Clarification:
1. **Geographic Area Corrected**
   - Data actually covers Scotland and NE England (not Baltic Sea despite repo name)
   - Reference visualization examined: `images/Screenshot 2026-01-30 at 15.56.09.png`
   - Shows high-value DN areas (black polygons) representing threshold-exceeded regions

2. **Goal Understanding**
   - Convert vector polygons with DN values to raster TIFF format
   - This is an intermediate step toward final contour generation
   - Proof of concept approach: work on small spatial subset first

#### Documentation Created:
1. **Vector-to-Raster Prompt**: Created `prompts/02-vector-to-raster-conversion.md`
   - Comprehensive 7-step POC workflow
   - Includes spatial subsetting for efficient testing
   - Documents input data structure with JSON examples
   - Technical specifications: libraries, functions, parameters
   - Quick start guide for implementation
   - Expected deliverables and success criteria
   - Added extensive context for independent agent execution

2. **Reference Image Added**: `images/Screenshot 2026-01-30 at 15.56.09.png`
   - Visual target for validation
   - Shows expected output: Scotland/NE England with high-value areas highlighted

3. **README Updated**
   - Expanded to document both cleaning and conversion workflows
   - Corrected geographic area
   - Updated project structure
   - Added rasterio and numpy to requirements
   - Status updated to POC phase

---

### Complete Pipeline Definition
**Time**: 16:15 UTC

#### End Goal Clarified:
The complete processing pipeline consists of **three stages**:

```
Stage 1: Vector Cleaning → Stage 2: Rasterization → Stage 3: Contour Generation
   (GeoJSON polygons)         (TIFF raster)           (GeoJSON contours)
```

**Final Output**: Contour lines (isolines) representing areas of equal DN value

#### Contour Specifications:
- **DN Value Range**: 0-255
- **Contour Interval**: 25 DN units
- **Number of Classes**: 10
- **Contour Levels**: 25, 50, 75, 100, 125, 150, 175, 200, 225, 250
- **Classification**:
  - Class 1: 0-25
  - Class 2: 25-50
  - Class 3: 50-75
  - Class 4: 75-100
  - Class 5: 100-125
  - Class 6: 125-150
  - Class 7: 150-175
  - Class 8: 175-200
  - Class 9: 200-225
  - Class 10: 225-255

#### Documentation Created:
1. **Contour Generation Prompt**: Created `prompts/03-contour-generation.md`
   - Defines final stage of processing pipeline
   - 7-step workflow for generating contour lines from raster
   - Specifies 10-class classification scheme
   - Multiple implementation options (GDAL, matplotlib, scikit-image)
   - Contour styling and visualization guidelines
   - Includes GDAL command-line alternative
   - Technical specifications and deliverables

2. **README Updated**
   - Added complete 3-stage pipeline overview
   - Visual pipeline diagram
   - Added prompt 03 to project structure
   - Updated workflow section with contour generation details

#### Current Status:
- **Stage 1**: Planned (cleaning workflow defined)
- **Stage 2**: Ready for implementation (POC rasterization workflow)
- **Stage 3**: Planned (contour generation workflow defined)

#### Next Actions:
- Execute Stage 2 POC: Vector-to-raster conversion on spatial subset
- Validate raster output against reference visualization
- Proceed to Stage 3: Contour generation once raster is validated

---

### Quantization and Data Preservation Updates
**Time**: 16:30 UTC

#### Key Refinements:
1. **Quantization of DN Values**
   - DN values must be quantized to bucket centers before rasterization
   - 10 buckets with intervals of 25: (0-25, 25-50, ..., 225-255)
   - Bucket centers: 12.5, 37.5, 62.5, 87.5, 112.5, 137.5, 162.5, 187.5, 212.5, 240.0
   - Example: DN=37 → quantized to 37.5, DN=189 → quantized to 187.5
   - Purpose: Standardize values for consistent contour generation

2. **Preserve Vector Data at Each Stage**
   - Spatial subset must be saved as GeoJSON: `output/subset_extract.json`
   - Preserves vector format for the extracted region
   - Allows validation and alternative processing paths
   - Contains original DN values before quantization

3. **Updated Workflow (Stage 2)**
   - Now 8 steps (was 7)
   - Added explicit quantization step (Step 3)
   - Spatial subset saved as .json file (Step 2)
   - TIFF uses Float32 to store decimal bucket centers

#### Documentation Updated:
- **Prompt 02**: Added quantization logic with code example
- **Prompt 02**: Updated to save subset as GeoJSON (required, not optional)
- **Prompt 02**: Output now includes both .json and .tif files
- **Prompt 02**: Updated data type to Float32 for decimal values
- **Prompt 02**: Added quantization function to key functions list
- **README**: Updated Stage 2 workflow to highlight quantization
- **README**: Now shows 8-step process with quantization as key feature

#### Technical Details:
```python
# Quantization mapping
0-24   → 12.5
25-49  → 37.5
50-74  → 62.5
75-99  → 87.5
100-124 → 112.5
125-149 → 137.5
150-174 → 162.5
175-199 → 187.5
200-224 → 212.5
225-255 → 240.0
```
