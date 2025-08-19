#!/usr/bin/env python3
"""
build_yearly_ever_forest.py

For each year-folder (>1980) under --nlcd-base, combine your ever_forest COG
mask with the annual NLCD TIFF so that ever-forest pixels (41,42,43) come
from the mask, and all others from that year's map.  Outputs Cloud-Optimized
GeoTIFFs with internal overviews and a hard-coded palette.
"""

import os
import argparse
from osgeo import gdal
import numpy as np

gdal.UseExceptions()

def main(nlcd_base, ever_path, out_dir):
    gdal.UseExceptions()

    # forest codes & nodata
    forest = {41, 42, 43}
    nodata = 250

    # prepare output folder
    os.makedirs(out_dir, exist_ok=True)

    # open ever-forest COG once
    ds_ever = gdal.Open(ever_path, gdal.GA_ReadOnly)
    be = ds_ever.GetRasterBand(1)
    gt    = ds_ever.GetGeoTransform()
    proj  = ds_ever.GetProjection()
    xsize = ds_ever.RasterXSize
    ysize = ds_ever.RasterYSize

    # build a minimal palette: forest colors + transparent everywhere else
    ct = gdal.ColorTable()
    for i in range(256):
        ct.SetColorEntry(i, (0,0,0,0))

    # Hard-code NLCD palette entries
    ct.SetColorEntry(11, ( 70, 107, 159, 255))
    ct.SetColorEntry(12, (209, 222, 248, 255))
    ct.SetColorEntry(21, (222, 197, 197, 255))
    ct.SetColorEntry(22, (217, 146, 130, 255))
    ct.SetColorEntry(23, (235,   0,   0, 255))
    ct.SetColorEntry(24, (171,   0,   0, 255))
    ct.SetColorEntry(31, (179, 172, 159, 255))
    ct.SetColorEntry(41, (104, 171,  95, 255))
    ct.SetColorEntry(42, ( 28,  95,  44, 255))
    ct.SetColorEntry(43, (181, 197, 143, 255))
    ct.SetColorEntry(52, (204, 184, 121, 255))
    ct.SetColorEntry(71, (223, 223, 194, 255))
    ct.SetColorEntry(82, (171, 108,  40, 255))
    ct.SetColorEntry(90, (184, 217, 235, 255))
    ct.SetColorEntry(95, (108, 159, 184, 255))
    ct.SetColorEntry(nodata, (0,0,0,0))

    # grab all year-dirs >1980
    years = sorted(
        d for d in os.listdir(nlcd_base)
        if d.isdigit() and int(d)>1980
           and os.path.isfile(os.path.join(nlcd_base,d,
               f'Annual_NLCD_LndCov_{d}_CU_C1V1.tif'))
    )

    for yr in years:
        in_year = os.path.join(nlcd_base, yr,
            f'Annual_NLCD_LndCov_{yr}_CU_C1V1.tif')

        if not os.path.exists(os.path.join(out_dir, str(yr))):
            os.makedirs(os.path.join(out_dir, str(yr)))

        out_tif = os.path.join(out_dir, f'{yr}/ever_forest_{yr}.tif')

        # create a new COG
        drv = gdal.GetDriverByName('GTiff')
        out_ds = drv.Create(
            out_tif, xsize, ysize, 1, gdal.GDT_Byte,
            options=[
                'COMPRESS=LZW',
                'PREDICTOR=2',
                'BIGTIFF=YES',
                'TILED=YES',
            ]
        )
        out_ds.SetGeoTransform(gt)
        out_ds.SetProjection(proj)
        bo = out_ds.GetRasterBand(1)
        bo.SetNoDataValue(nodata)
        bo.SetColorTable(ct)

        # open that year's band
        ds_year = gdal.Open(in_year, gdal.GA_ReadOnly)
        by = ds_year.GetRasterBand(1)

        # tile through
        bx, bys = bo.GetBlockSize()
        bx, bys = bx or 512, bys or 512

        for y in range(0, ysize, bys):
            rows = min(bys, ysize - y)
            for x in range(0, xsize, bx):
                cols = min(bx, xsize - x)
                a = be.ReadAsArray(x, y, cols, rows)
                b = by.ReadAsArray(x, y, cols, rows)
                mask = np.isin(a, list(forest))
                out = np.where(mask, a, b).astype(np.uint8)
                bo.WriteArray(out, xoff=x, yoff=y)

        bo.FlushCache()
        out_ds = None
        ds_year = None
        print(f'→ wrote {out_tif}')

if __name__ == '__main__':
    nlcd_base = './'
    ever = 'ever_forest/ever_forest.tif'
    out_dir = 'ever_forest/'
    main(nlcd_base, ever, out_dir)
