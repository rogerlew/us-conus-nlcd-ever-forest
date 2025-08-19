#!/usr/bin/env bash

# Configurable range
START_YEAR=1985
END_YEAR=2024

# Base URL
BASE_URL="https://www.mrlc.gov/downloads/sciweb1/shared/mrlc/data-bundles"

# Loop over years
for YEAR in $(seq $START_YEAR $END_YEAR); do
    echo "=== Processing $YEAR ==="
    YEAR_DIR="$YEAR"
    ZIP_FILE="Annual_NLCD_LndCov_${YEAR}_CU_C1V1.zip"
    TIF_FILE="Annual_NLCD_LndCov_${YEAR}_CU_C1V1.tif"

    # Make year directory if missing
    mkdir -p "$YEAR_DIR"
    cd "$YEAR_DIR" || exit 1

    # Download if not already present
    if [ ! -f "$ZIP_FILE" ] && [ ! -f "$TIF_FILE" ]; then
        echo "Downloading $ZIP_FILE ..."
        wget -q "${BASE_URL}/${ZIP_FILE}" -O "$ZIP_FILE"
    else
        echo "$ZIP_FILE or $TIF_FILE already exists, skipping download"
    fi

    # Unzip if needed
    if [ -f "$ZIP_FILE" ]; then
        echo "Unzipping $ZIP_FILE ..."
        unzip -o "$ZIP_FILE" >/dev/null
    fi

    # Build VRT if TIFF exists
    if [ -f "$TIF_FILE" ]; then
        echo "Building VRT for $TIF_FILE ..."
        gdalbuildvrt -overwrite .vrt "$TIF_FILE"
    else
        echo "ERROR: Missing $TIF_FILE for $YEAR"
    fi

    # Cleanup ZIP
    if [ -f "$ZIP_FILE" ]; then
        rm -f "$ZIP_FILE"
    fi

    cd ..
done

echo "=== Done ==="
