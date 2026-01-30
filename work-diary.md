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
