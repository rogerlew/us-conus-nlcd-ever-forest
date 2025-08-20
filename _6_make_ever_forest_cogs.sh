#!/usr/bin/env bash
set -euo pipefail

# Base dir containing ever_forest rasters
BASE_DIR="ever_forest"

# Loop over all .tif files under ever_forest (including yearly subdirs)
find "$BASE_DIR" -type f -name "*.tif" | while read -r tif; do
    echo "Converting $tif → COG-compatible GeoTIFF (in place)..."
    
    gdal_translate \
        -of GTiff \
        -co TILED=YES \
        -co BLOCKXSIZE=512 \
        -co BLOCKYSIZE=512 \
        -co COMPRESS=DEFLATE \
        -co PREDICTOR=2 \
        -co BIGTIFF=IF_SAFER \
        -co NUM_THREADS=ALL_CPUS \
        "$tif" "$tif.tmp.tif"

    gdaladdo -r average "$tif.tmp.tif" 2 4 8 16 32 64

    mv -f "$tif.tmp.tif" "$tif"
done

echo "✅ All GeoTIFFs in $BASE_DIR are now COG-friendly."
