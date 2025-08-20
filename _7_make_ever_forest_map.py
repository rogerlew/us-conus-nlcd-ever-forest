#!/usr/bin/env python3
"""
make_ever_forest_map_stadia_cartopy.py

Example:
  python make_ever_forest_map_stadia_cartopy.py \
    --input ever_forest/ever_forest.tif \
    --output ever_forest_map_stadia.png \
    --target-width 4500 \
    --zoom 5 \
    --labels
"""

import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from affine import Affine

import cartopy.crs as ccrs
from cartopy.io.img_tiles import StadiaMapsTiles

# Optional: load STADIA_API_KEY from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


def reproject_to_3857(src, target_width=None):
    """Reproject single-band raster to EPSG:3857 with nearest resampling.
       Optionally downsample to target_width (pixels)."""
    dst_crs = "EPSG:3857"
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds
    )
    if target_width and width > target_width:
        scale = target_width / width
        width = int(width * scale)
        height = int(height * scale)
        transform = transform * Affine.scale(1 / scale)

    arr = np.zeros((height, width), dtype=np.uint8)
    reproject(
        source=rasterio.band(src, 1),
        destination=arr,
        src_transform=src.transform,
        src_crs=src.crs,
        dst_transform=transform,
        dst_crs=dst_crs,
        resampling=Resampling.nearest,
        src_nodata=src.nodata,
        dst_nodata=0,
    )
    return arr, transform


def add_scalebar(ax, *, length_km=250, pad_px=40, height_px=10, text_pad=16):
    """Simple scale bar in EPSG:3857 coords (meters)."""
    # Axes extent in data (Web Mercator meters)
    xmin, xmax, ymin, ymax = ax.get_extent(crs=ax.projection)
    # Bar geometry near lower-left
    x0 = xmin + pad_px * (xmax - xmin) / ax.figure.bbox.width
    y0 = ymin + pad_px * (ymax - ymin) / ax.figure.bbox.height
    length_m = length_km * 1000.0

    ax.add_patch(plt.Rectangle(
        (x0, y0), length_m, height_px * (ymax - ymin) / ax.figure.bbox.height,
        transform=ax.projection, facecolor="black", edgecolor="black", zorder=100
    ))
    ax.text(
        x0, y0 - text_pad * (ymax - ymin) / ax.figure.bbox.height,
        f"{int(length_km)} km",
        fontsize=8, va="top", ha="left", transform=ax.projection
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="ever_forest/ever_forest.tif")
    ap.add_argument("--output", required=True, help="Output PNG")
    ap.add_argument("--target-width", type=int, default=4500,
                    help="Downsample target width in pixels for plotting")
    ap.add_argument("--zoom", type=int, default=5,
                    help="Stadia tile zoom (4–7 is typical for CONUS)")
    ap.add_argument("--labels", action="store_true",
                    help="Overlay 'stamen_terrain_labels' on top")
    ap.add_argument("--alpha", type=float, default=1.0, help="Forest overlay alpha")
    args = ap.parse_args()

    api_key = os.getenv("STADIA_API_KEY")
    if not api_key:
        raise SystemExit("STADIA_API_KEY not found (set in environment or .env)")

    # Read + warp once
    with rasterio.open(args.input) as src:
        arr3857, t3857 = reproject_to_3857(src, args.target_width)
        xmin = t3857.c
        ymax = t3857.f
        xmax = xmin + t3857.a * arr3857.shape[1]
        ymin = ymax + t3857.e * arr3857.shape[0]
        extent_3857 = [xmin, xmax, ymin, ymax]

    # Forest palette: 0 transparent, 1/2/3 = 41/42/43
    cmap = ListedColormap([
        (0, 0, 0, 0),                 # 0 - transparent (non-forest/NoData)
        (104/255, 171/255, 95/255, 1),# 1 - 41 Deciduous
        (28/255, 95/255, 44/255, 1),  # 2 - 42 Evergreen
        (181/255, 197/255, 143/255,1) # 3 - 43 Mixed
    ])

    # Baselayer via Cartopy + Stadia Maps tiles
    terrain = StadiaMapsTiles(style="alidade_smooth", apikey=api_key)
    proj = terrain.crs  # Web Mercator

    fig = plt.figure(figsize=(14, 9), dpi=200)
    ax = plt.axes(projection=proj)
    ax.set_extent(extent_3857, crs=proj)

    # Draw basemap
    ax.add_image(terrain, args.zoom, interpolation="bilinear", zorder=0)

    # Optional labels overlay
    if args.labels:
        labels = StadiaMapsTiles(style="stamen_terrain_labels", api_key=api_key)
        ax.add_image(labels, args.zoom, interpolation="bilinear", zorder=1)


    plot_arr = np.zeros_like(arr3857, dtype=np.uint8) # Start with a transparent background (value 0)
    plot_arr[arr3857 == 41] = 1 # Map Deciduous
    plot_arr[arr3857 == 42] = 2 # Map Evergreen
    plot_arr[arr3857 == 43] = 3 # Map Mixed

    # Forest overlay
    ax.imshow(
        plot_arr,
        origin="upper",
        extent=extent_3857,
        cmap=cmap,
        interpolation="nearest",
        vmin=0, vmax=3,
        alpha=args.alpha,
        zorder=5,
    )

    # Title + data line (no on-figure provider branding)
    ax.set_title("Ever Forest (NLCD classes 41/42/43 across all years)",
                 fontsize=16, weight="bold", pad=12)
    ax.text(0.01, 0.98,
            "Data: NLCD (USGS/USDA/partners). Derived 'Ever Forest' (41/42/43).",
            transform=ax.transAxes, va="top", ha="left", fontsize=8)

    # Legend
    import matplotlib.patches as mpatches
    patches = [
        mpatches.Patch(color=cmap(1), label="41 – Deciduous Forest"),
        mpatches.Patch(color=cmap(2), label="42 – Evergreen Forest"),
        mpatches.Patch(color=cmap(3), label="43 – Mixed Forest"),
    ]
    leg = ax.legend(handles=patches, loc="lower right",
                    frameon=True, framealpha=0.9, fontsize=8)

    # Scale bar
    add_scalebar(ax, length_km=250)

    ax.set_axis_off()
    fig.savefig(args.output, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
