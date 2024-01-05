from osgeo import gdal
import math
import argparse
import os
"""
script adopted from Data_conversion/tools/create_thumbnail · master · datacube / prepare-ingest · GitLab (ssc-spc.gc.ca).
"""
parser = argparse.ArgumentParser(description="Define variable")
parser.add_argument("-c", "--cog_path", type=str, help="Path of the folder containing the input cogs", required=True)
args = parser.parse_args()

directory = args.cog_path
#directory = 'C:/Users/xcai/Documents/EGS_projects/RiverIce/cog/'

def create_thumbnail(raster):
    rds = gdal.Open(raster)
    height = rds.RasterYSize
    width = rds.RasterXSize
    new_height = math.ceil(600*height/width)
    if new_height > 600: 
        new_height = 600
    print(new_height)
    kwargs = {
    'height': 'new_height',
    'width': '600'
    }
    
    gdal.Translate(rasterOut,raster,**kwargs)

for file in os.listdir(directory):
    
    raster = os.path.join(directory,file)
    
    print (raster)
    
    #directoryOut = directory.replace('-cog','-thumbnail')
    rasterOut = os.path.join(directory,file)
    rasterOut = rasterOut.replace('.tif','.png')
    
    print (rasterOut)
    
    create_thumbnail(raster)
