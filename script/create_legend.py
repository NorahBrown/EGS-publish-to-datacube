"""
Create a legend file for an item and copy in the S3 bucket of the Datacube

Code Summary
------------
 - Extract name of the item
 - Copy the original legend file to the final S3 bucket 

 Example
 -------
    Env variables
    -------------

    # AWS credentials
    AWS_ACCESS_KEY_ID=XXX
    AWS_SECRET_ACCESS_KEY=XXX
    AWS_SESSION_TOKEN=XXX

    CLI
    ---
    # python createLegend.py <image.tif>
    python createLegend.py COG_creation/Test/tiff/RiverIce_CAN_ON_Moose_20160503_232950.tif 


"""
# Python standard library
import argparse
from pathlib import Path
import sys
from typing import Union


# Custom packages
from rasterio.crs import CRS

# Datacube custom packages
from nrcan_ssl.ssl_utils import nrcan_ca_patch, SSLUtils


# Ensure pythonpath has repo root for local module imports
root = Path(__file__).parents[1]
if str(root.absolute()) not in sys.path:
    sys.path.insert(0,str(root.absolute()))

# Local modules

from src.utils.s3_operations import (copy_file)

def main(infile:Union[str,Path],
         level:str='stage',
         prefix:str='store/water/river-ice-canada-archive/'
         ):
    """
    Extract name of the item
    Copy the original legend file to the final S3 bucket

    """
    infile = Path(infile)
    bucket = f'datacube-{level}-data-public'
   

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

    print('Le fichier '+ legend_file_png + ' a été créé avec succès. ')

def _handle_args():

    parser = argparse.ArgumentParser(description='Process tifs create legend.',formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('infile', type=str, help='The full path to tif to be converted.')
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
         level=args.level,
         prefix=args.prefix)
    
if __name__ == '__main__':
    _handle_args()