#!/bin/bash
base_dir="$(pwd)"
meta="$base_dir/metadata.json"

for year in {1985..2024}; do
    dir="$base_dir/$year"
    if [ -d "$dir" ]; then
        ln -sf "$meta" "$dir/metadata.json"
        echo "Linked metadata.json into $dir"
    fi
done
