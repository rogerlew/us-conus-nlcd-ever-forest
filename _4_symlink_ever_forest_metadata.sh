#!/bin/bash
base_dir="$(pwd)"
meta="$base_dir/ever_forest_metadata.json"

for year in {1985..2024}; do
    dir="$base_dir/ever_forest/$year"
    if [ -d "$dir" ]; then
        ln -sf "$meta" "$dir/metadata.json"
        echo "Linked metadata.json into $dir"
    fi
done
