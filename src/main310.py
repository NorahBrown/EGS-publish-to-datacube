"""
Datacube pipeline COG and STAC creation and publication

Reprojects and cogifies an input tif
Publishes it to the datacube repo
Send create and publishe STAC command to datacube
"""
# Python standard library
import argparse
from datetime import datetime
from numbers import Number
from pathlib import Path
from typing import Union

# Custom packages
from rasterio.crs import CRS

# Datacube custom packages
from ccmeo_datacube_authentication.scripts import egs_publish_stac

# Local modules
from ..COG_creation.geotiff_to_cog import (reproject_raster,
                                           geotiff_to_cog)
from ..COG_creation.s3_operations import (upload_file_to_s3,
                                          upload_fileContent_to_s3)

def main(infile:Union[str,Path],
         res:Number=5,
         epsg:int=3978,
         level:str='stage',
         prefix:str='/store/water/river-ice-canada-archive'
         ):
    """
    Convert input geotiff to cog
    Upload the cog and sidecar(s) to S3 bucket
    Call ddb-api to create and publish STAC for new item
    """
    infile = Path(infile)
    bucket = f'datacube-{level}-data-public'
    proj_epsg = CRS.from_epsg(epsg)
    output_path = infile.with_stem(f'{infile.stem}_cog.tif')

    # Extract datetime from the file name 
    time_str = infile.stem.split('_')[-1]
    date_str = infile.stem.split('_')[-2]
    timestamp =date_str  +"_" + time_str
    datetime_obj = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
    formatted_datetime = datetime_obj.strftime('%Y:%m:%d %H:%M:%S')
    #print(formatted_datetime)

    # Reproject the infile
    proj_path = reproject_raster(input_path=infile, dstSRS=proj_epsg, xRes=res, yRes=res)


    is_valid = geotiff_to_cog(proj_path, output_path, datetime_value=formatted_datetime)
        
    upload_file_to_s3(bucket, folder_path=prefix, local_file_path=output_path, new_file_name=output_path.name)

    # TODO upload side cars
    # upload_fileContent_to_s3(bucket, file_key=prefix + 'is-active.txt', file_content=is_active_as_string)

    # Call ddb-api to create and publish STAC
    egs_publish_stac.main(text_filter=input.stem,level=level)

    return

def _handle_args():

    parser = argparse.ArgumentParser(description='Process tifs to datacube.')

    parser.add_argument('infile', type=str, help='The full path to tif to be converted.')
    parser.add_argument('resolution', type=int, default=5, help='The output spatial resolution in meters, default is 5')
    parser.add_argument('-c''--epsg_crs', type=int, default=3978, help="The EPSG number")
    parser.add_argument('-l''--level', type=str, default='stage', help='The datacube publication level')
    parser.add_argument('-p''prefix', type=str, default='/store/water/river-ice-canada-archive',help='The bucket prefix for the collection')

    args = parser.parse_args()

    main(infile=args.infile,
         res=args.resolution,
         epsg=args.epsg_crs,
         level=args.level,
         prefix=args.prefix)
    
if __name__ == '__main__':
    _handle_args()