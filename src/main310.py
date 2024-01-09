"""
Datacube pipeline COG and STAC creation and publication

Code Summary
------------
 - Reprojects and cogifies an input tif
 - Publishes COG to the datacube repo
 - Publishes ancilliary (sidecar) files to the datacube repo (in progress)
 - Sends create and publish STAC command to datacube ddb-api

 Example
 -------
    Env variables
    -------------
    # ddb-api authentication
    DDB_AUTH_USER=XXX
    DDB_AUTH_PASSWORD=XXX

    # AWS credentials
    AWS_ACCESS_KEY_ID=XXX
    AWS_SECRET_ACCESS_KEY=XXX
    AWS_SESSION_TOKEN=XXX

    CLI
    ---
    # python main310.py <image.tif> -l stage
    python main310.py COG_creation/Test/tiff/RiverIce_CAN_ON_Moose_20160503_232950.tif -l stage

    Container
    ---------
    See Containerfile.gdal-python

"""
# Python standard library
import argparse
from datetime import datetime
from numbers import Number
from pathlib import Path
import sys
from typing import Union
<<<<<<< HEAD
import osgeo
=======
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5

# Custom packages
from rasterio.crs import CRS

# Datacube custom packages
from ccmeo_datacube_create_stac.scripts import egs_publish_stac
<<<<<<< HEAD
from nrcan_ssl.ssl_utils import nrcan_ca_patch, SSLUtils
# import create_thumbnail
=======
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5

# Ensure pythonpath has repo root for local module imports
root = Path(__file__).parents[1]
if str(root.absolute()) not in sys.path:
    sys.path.insert(0,str(root.absolute()))

# Local modules
from COG_creation.geotiff_to_cog import (reproject_raster,
                                           geotiff_to_cog)
from COG_creation.s3_operations import (upload_file_to_s3,
                                          upload_fileContent_to_s3)
<<<<<<< HEAD
from COG_creation.create_thumbnail import (create_thumbnail)
=======
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5

def main(infile:Union[str,Path],
         res:Number=5,
         epsg:int=3978,
         method:str='near',
         level:str='stage',
<<<<<<< HEAD
         prefix:str='store/water/river-ice-canada-archive/'
=======
         prefix:str='/store/water/river-ice-canada-archive'
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5
         ):
    """
    Convert input geotiff to cog
    Upload the cog and sidecar(s) to S3 bucket
    Call ddb-api to create and publish STAC for new item
    """
    infile = Path(infile)
    bucket = f'datacube-{level}-data-public'
    proj_epsg = CRS.from_epsg(epsg)
    output_path = infile.with_stem(f'{infile.stem}_cog')
    success = False
    published_cog = False
<<<<<<< HEAD
    thumbnail_creation = False 
=======
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5
    published_stac = False

    # Set the datacube AWS cannonical ID for s3 object permissions
    if level == 'prod':
        dc_aws_id = 'id="b51b8d25062b67c1898da5e3b21415897431ff8c969c1cc16f76d54a189cb08c"'
    else:
        # Default to stage
        dc_aws_id = 'id="1146f3529acf9b3cbfc11dbddcd9b4424910c150b022e78558272d726525a30f"'
    # Set the acl headers for datacube full control and public read
    
    acl = extra_args = {
        'GrantRead': 'uri="http://acs.amazonaws.com/groups/global/AllUsers"', 
        'GrantFullControl': dc_aws_id,}


    # Extract datetime from the file name <other>_<date>_<time>.tif
    parts = infile.stem.split('_')
    timestamp =f'{parts[-2]}T{parts[-1]}'

    # Reformat to TIFFTAG_DATETIME format
    datetime_obj = datetime.strptime(timestamp, '%Y%m%dT%H%M%S')
    formatted_datetime = datetime_obj.strftime('%Y:%m:%d %H:%M:%S')

    # Reproject the infile
    proj_path = reproject_raster(
        input_path=infile,
        dstSRS=str(proj_epsg),
        xRes=res,
        yRes=res,
        resampleAlg=method)

    # Create COG and check if COG is valid
    valid_cog = geotiff_to_cog(str(proj_path), str(output_path), datetime_value=formatted_datetime)

    if not valid_cog:
        return {'sucess':success,
                'message':'COG is invalid',
                'input':input,
                'cog':output_path,
                "valid_cog":valid_cog,
                'published_cog':False,
                'published_stac':False}
<<<<<<< HEAD
    
    # Create a thumbnail and check the result
    thumbnail_creation, output_thumb, ct_err = create_thumbnail(str(infile))
    if not thumbnail_creation:
        return {'sucess':success,
                'message':'Thunmbnail has not been created',
                'creationThumbnail error': ct_err}
        
    """     
    # Create a metadata json file and check the result
    json_creation, output_thumb, ct_err = create_thumbnail(str(infile))
    if not json_creation:
        return {'sucess':success,
                'message':'Thunmbnail has not been created',
                'creationThumbnail error': ct_err} 
    """
    
    published_thumb, pt_err = upload_file_to_s3(
        bucket,
        folder_path=prefix,
        local_file_path=output_thumb,
        new_file_name=output_thumb.name,
        extra_args=acl)
    if not published_thumb:
        return {'succes':published_thumb,
                'message':'Thunmbnail has not been published',
                'published thumbnail error': pt_err}

    published_cog, pc_err = upload_file_to_s3(
        bucket,
        folder_path=prefix,
        local_file_path=output_path,
        new_file_name=output_path.name,
        extra_args=acl)
    if published_cog:
        pass
=======
        
    published_cog,pc_err = upload_file_to_s3(bucket, folder_path=prefix, local_file_path=output_path, new_file_name=output_path.name)
    if published_cog:

>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5
        # TODO upload side cars
        # upload_fileContent_to_s3(bucket, file_key=prefix + 'is-active.txt', file_content=is_active_as_string)

        # Call ddb-api to create and publish STAC
<<<<<<< HEAD
        published_stac = egs_publish_stac.main(text_filter=infile.stem,level=level)
        # TODO extract link to STAC API item
        print(published_stac)
        success = published_stac['success']

=======
        published_stac = egs_publish_stac.main(text_filter=input.stem,level=level)
        success = published_stac['success']
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5
    result = {'sucess':success,
              'message':'Published COG and STAC',
              'infile':str(infile.absolute()),
              'cog':str(output_path.absolute()),
              "valid_cog":valid_cog,
              'published_cog_success':published_cog,
              'published_cog_error':str(pc_err),
              'published_stac':published_stac}
    print(result)

    #TODO Clean up / delete local files

    return result

def _handle_args():

<<<<<<< HEAD
    parser = argparse.ArgumentParser(description='Process tifs to datacube.',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('infile', type=str, help='The full path to tif to be converted.')
    parser.add_argument(
        '-r','--resolution',
        type=int,
        default=5,
        #help="The output spatial resolution in meters. default: %(default)s"
        help="The output spatial resolution in meters."
=======
    parser = argparse.ArgumentParser(description='Process tifs to datacube.')

    parser.add_argument('infile', type=str, help='The full path to tif to be converted.')
    parser.add_argument(
        'resolution',
        type=int,
        default=5,
        help='The output spatial resolution in meters, default is 5'
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5
        )
    parser.add_argument(
        '-c','--epsg_crs',
        type=int,
        default=3978,
<<<<<<< HEAD
        help="The EPSG number. Ex: 4326."
=======
        help="The EPSG number"
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5
        )
    parser.add_argument(
        '-m','--resampling_method',
        type=str,
        default='near',
        choices=[
            'near','bilinear','cubic','cubicspline',
            'lanczos','average','rms','mode','max',
            'min','med','q1','q3','sum'
            ],
<<<<<<< HEAD
        help="The GDAL warp resampling method."
=======
        help="The GDAL warp resampling method"
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5
        )
    parser.add_argument(
        '-l','--level',
        type=str,
        default='stage',
        choices=['prod','stage','dev'],
<<<<<<< HEAD
        help="The datacube publication level."
=======
        help='The datacube publication level'
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5
        )
    parser.add_argument(
        '-p','--prefix',
        type=str,
<<<<<<< HEAD
        default='store/water/river-ice-canada-archive/',
        help="The bucket prefix for the collection."
        )
=======
        default='/store/water/river-ice-canada-archive',
        help='The bucket prefix for the collection')
>>>>>>> 127c567a1fdfca97e47879fafadd1c1776eb04b5

    args = parser.parse_args()

    main(infile=args.infile,
         res=args.resolution,
         epsg=args.epsg_crs,
         method=args.resampling_method,
         level=args.level,
         prefix=args.prefix)
    
if __name__ == '__main__':
    _handle_args()