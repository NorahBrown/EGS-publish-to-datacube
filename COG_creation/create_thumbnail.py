from osgeo import gdal
import math
#import argparse
from pathlib import Path

"""
Script that creates a thumbnail for the raster file passed in parameter. Script adapted from Data_conversion/tools/create_thumbnail · master · datacube / prepare-ingest · GitLab (ssc-spc.gc.ca).

#directory = 'C:/Users/xcai/Documents/EGS_projects/RiverIce/cog/'
"""
def create_thumbnail(raster):

    rds = gdal.Open(raster)
    height = rds.RasterYSize
    width = rds.RasterXSize
    new_height = math.ceil(600*height/width)
    if new_height > 600: 
        new_height = 600
    kwargs = {
    'height': 'new_height',
    'width': '600'
    }
    
    infile = Path(raster)
    outfile = infile.with_stem(f'{infile.stem}_thumb')
    rasterOut = outfile.with_suffix('.png')

    try: 
       gdal.Translate(str(rasterOut),raster,**kwargs)
    except Exception as e:
        return False,rasterOut,e
    
    return True,rasterOut,None

