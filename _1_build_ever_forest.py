#!/usr/bin/env python3
"""
build_ever_forest.py

Scan all yearly NLCD VRTs under a base directory and create a single
GeoTIFF marking pixels ever classified as forest (NLCD codes 41,42,43).
Non‐forest pixels get a NoData value of 250.
"""

import os
import argparse
from osgeo import gdal
import numpy as np

gdal.UseExceptions()

def main(inp_dir, out_path):

    if os.path.exists(out_path):
        os.remove(out_path)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # -------------------------------------------------------------------
    # 1) find only year-folders >1980 that contain a .vrt file
    years = sorted(
        yr for yr in os.listdir(inp_dir)
        if yr.isdigit() and int(yr) > 1980
           and os.path.isfile(os.path.join(inp_dir, yr, '.vrt'))
    )
    vrt_paths = [os.path.join(inp_dir, yr, '.vrt') for yr in years]
    if not vrt_paths:
        raise FileNotFoundError(f'No valid VRTs in {inp_dir} for years >1980')

    # -------------------------------------------------------------------
    # 2) open all datasets *and keep them alive* in src_dss
    src_dss = []
    for p in vrt_paths:
        ds = gdal.Open(p, gdal.GA_ReadOnly)
        if ds is None:
            raise RuntimeError(f'Could not open {p}')
        src_dss.append(ds)

    # pull out geo-info from the first one
    gt       = src_dss[0].GetGeoTransform()
    proj     = src_dss[0].GetProjection()
    xsize    = src_dss[0].RasterXSize
    ysize    = src_dss[0].RasterYSize

    # get the bands
    src_bands = [ds.GetRasterBand(1) for ds in src_dss]

    # -------------------------------------------------------------------
    # 3) create output
    drv    = gdal.GetDriverByName('GTiff')
    out_ds = drv.Create(out_path, xsize, ysize, 1, gdal.GDT_Byte,
                        options=['TILED=YES','COMPRESS=LZW'])
    out_ds.SetGeoTransform(gt)
    out_ds.SetProjection(proj)
    band_out = out_ds.GetRasterBand(1)
    nodata   = 250
    band_out.SetNoDataValue(nodata)

    forest_codes = {41, 42, 43}
    bx, by = band_out.GetBlockSize()
    bx, by = bx or 256, by or 256

    # -------------------------------------------------------------------
    # 4) tile through and write “ever forest”
    for y in range(0, ysize, by):
        print(y/ysize * 100)

        rows = min(by, ysize - y)
        for x in range(0, xsize, bx):
            cols = min(bx, xsize - x)

            # start with all NoData
            out_block = np.full((rows, cols), nodata, dtype=np.uint8)

            # for each year, overwrite forest pixels with that year's code
            for b in src_bands:
                arr = b.ReadAsArray(x, y, cols, rows)
                mask = np.isin(arr, list(forest_codes))
                out_block[mask] = arr[mask].astype(np.uint8)

            band_out.WriteArray(out_block, xoff=x, yoff=y)

    band_out.FlushCache()
    out_ds = None
    # keep src_dss alive until here
    src_dss.clear()


if __name__ == '__main__':
    main('./', 'ever_forest/ever_forest.tif')
