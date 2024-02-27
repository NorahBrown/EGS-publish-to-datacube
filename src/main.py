"""
Datacube pipeline COG and STAC creation and publication

Code Summary
------------
 - Reprojects and cogifies an input tif
 - Publishes COG to the datacube repo
 - Publishes ancilliary (thumbnail, legend, url package(json)) files to the datacube repo
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
    # usage: main.py [-h] [-r RESOLUTION] [-c EPSG_CRS] [-m {near,bilinear,cubic,cubicspline,lanczos,average,rms,mode,max,min,med,q1,q3,sum}] [-l {prod,stage,dev}] [-p PREFIX] infile
    # python main.py <image.tif> -l stage
    python main.py tests/data/RiverIce_CAN_ON_Moose_20160503_232950.tif -l stage -r 30 - m mode

    Container
    ---------
    See Containerfile

"""
# Python standard library
import argparse
from datetime import datetime
from numbers import Number
from pathlib import Path
import sys
from typing import Union
import osgeo

# Custom packages
from rasterio.crs import CRS

# Datacube custom packages
from ccmeo_datacube_create_stac.scripts import egs_publish_stac

# Local modules
src_root = Path(__file__)
if str(src_root) not in sys.path:
    sys.path.insert(0,str(src_root))
from utils.geotiff_to_cog import (reproject_raster, geotiff_to_cog)
from utils.s3_operations import (upload_file_to_s3, copy_file)
from utils.create_thumbnail import create_thumbnail
from utils.create_json import create_json

def main(infile:Union[str,Path],
         res:Number=5,
         epsg:int=3978,
         method:str='near',
         level:str='stage',
         prefix:str='store/water/river-ice-canada-archive/'
         ):
    """
    Convert input geotiff to cog
    Upload the cog and sidecar(s) to S3 bucket
    Call ddb-api to create and publish STAC for new item
    """
    infile = Path(infile)
    bucket = f'datacube-{level}-data-public'
    proj_epsg = CRS.from_epsg(epsg)
    output_path = infile.with_stem(f'{infile.stem}')
    ftp_path="https://data.eodms-sgdot.nrcan-rncan.gc.ca/public/EGS"
    

    success = False
    published_cog = False
    thumbnail_creation = False 
    json_creation = False 
    published_stac = False
    published_thumb = False
    published_json = False

    # Set the datacube AWS cannonical ID for s3 object permissions
    if level == 'prod':
        dc_aws_id = 'id="b51b8d25062b67c1898da5e3b21415897431ff8c969c1cc16f76d54a189cb08c"'
    else:
        # Default to stage
        dc_aws_id = 'id="1146f3529acf9b3cbfc11dbddcd9b4424910c150b022e78558272d726525a30f"'
        # Only for testing 
        # ftp_path="https://data.eodms-sgdot.nrcan-rncan.gc.ca/public/EGS/outgoing/EGSDevProducts"

    # Set the acl headers for datacube full control and public read
    
    acl = extra_args = {
        'GrantRead': 'uri="http://acs.amazonaws.com/groups/global/AllUsers"', 
        'GrantFullControl': dc_aws_id,}


    # Extract datetime from the file name <other>_<date>_<time>.tif
    parts = infile.stem.split('_')
    timestamp =f'{parts[-2]}T{parts[-1]}'

    # Extract value for creating FTP path
    product = parts[0]
    country = parts[1]
    province = parts[2]
    year = (parts[-2])[0:4]
    ftp_url = f'{ftp_path}/{year}/{product}/{country}/{province}/{infile.stem}.zip'
    json_file=f'{infile.parent}\{infile.stem}.json'


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
    
    # Create a thumbnail and check the result
    thumbnail_creation, outfile_thumb, ct_err = create_thumbnail(str(infile))
    if not thumbnail_creation:
        return {'sucess':success,
                'message':'Thumbnail has not been created',
                'creationThumbnail error': ct_err}
        
    
    published_thumb, pt_err = upload_file_to_s3(
        bucket,
        folder_path=prefix,
        local_file_path=outfile_thumb,
        new_file_name=outfile_thumb.name,
        extra_args=acl)
    if not published_thumb:
        return {'succes':published_thumb,
                'message':'Thumbnail has not been published',
                'published thumbnail error': pt_err}


    # Create a metadata JSON file and check the result
    json_creation, jc_err = create_json(json_file,ftp_url)
    if not json_creation:
        result = {'succes':json_creation,
                'message':'JSON file has not been created',
                'Create thumbnail error': jc_err}

        return result
    json_file= Path(json_file)

    published_json, pj_err = upload_file_to_s3(
        bucket,
        folder_path=prefix,
        local_file_path=json_file,
        new_file_name=json_file.name,
        extra_args=acl)

    if not published_json:
        message = 'The JSON file has not been published'
        if __name__ == '__main__':
            # Pass back command line error
            return 1, message
        else:
            # Return module import error
            return {'succes':published_json,
                    'message':message,
                    'published thumbnail error': pj_err}
        
    """
    # Create a SVG legend file and check the result
    legend_file_svg_ori=f'riverice_legend.svg'
    legend_file_svg=f'{infile.stem}_legend.svg'

    legend_creation_svg = copy_file(bucket,
                                prefix,
                                legend_file_svg_ori,
                                bucket_name_dest=bucket,
                                prefix_dest=prefix,
                                filename_dest=legend_file_svg,
                                kwarg=acl)
    if not legend_creation_svg:
        message ="The SVG legend file has NOT been created"
        if __name__ == '__main__':
            # Pass back command line error
            return 1, message
        else:
            # Return module import error
            return {'succes':legend_creation_svg,
                    'message':message}

    """     
    # Create a PNG legend file and check the result
    legend_file_png_ori=f'riverice_legend.png'
    legend_file_png=f'{infile.stem}_legend.png'
    legend_creation_png = copy_file(bucket,
                                    prefix,
                                    legend_file_png_ori,
                                    bucket_name_dest=bucket,
                                    prefix_dest=prefix,
                                    filename_dest=legend_file_png,
                                    kwarg=acl)

    if not legend_creation_png:
        message ="The PNG legend file has NOT been created"
        if __name__ == '__main__':
            # Pass back command line error
            return 1, message
        else:
            # Return module import error
            return {'succes':legend_creation_png,
                    'message':message
                    }

    published_cog, pc_err = upload_file_to_s3(
        bucket,
        folder_path=prefix,
        local_file_path=output_path,
        new_file_name=output_path.name,
        extra_args=acl)

    if published_cog:

        # TODO upload side cars
        # upload_fileContent_to_s3(bucket, file_key=prefix + 'is-active.txt', file_content=is_active_as_string)

        # Call ddb-api to create and publish STAC
        published_stac = egs_publish_stac.main(text_filter=infile.stem,level=level)
        # TODO extract link to STAC API item
        print(published_stac)
        success = published_stac['success']
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

    parser = argparse.ArgumentParser(description='Process tifs to datacube.',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('infile', type=str, help='The full path to tif to be converted.')
    parser.add_argument(
        '-r','--resolution',
        type=int,
        default=5,
        #help="The output spatial resolution in meters. default: %(default)s"
        help="The output spatial resolution in meters."
        )
    parser.add_argument(
        '-c','--epsg_crs',
        type=int,
        default=3978,
        help="The EPSG number. Ex: 4326."
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
        help="The GDAL warp resampling method."
        )
    parser.add_argument(
        '-l','--level',
        type=str,
        default='stage',
        choices=['prod','stage','dev'],
        help="The datacube publication level."
        )
    parser.add_argument(
        '-p','--prefix',
        type=str,
        default='store/water/river-ice-canada-archive/',
        help='The bucket prefix for the collection')

    args = parser.parse_args()

    main(infile=args.infile,
         res=args.resolution,
         epsg=args.epsg_crs,
         method=args.resampling_method,
         level=args.level,
         prefix=args.prefix)
    
if __name__ == '__main__':
    _handle_args()