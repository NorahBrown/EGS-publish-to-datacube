import argparse
import requests
import os 
import zipfile
import boto3
import logging
from botocore.exceptions import ClientError
from osgeo import gdal
from bs4 import BeautifulSoup
from datetime import datetime
from rio_cogeo.cogeo import cog_validate

from get_zip_links import * 
from download_and_unzip import * 
from geotiff_to_cog import * 
from s3_operations import * 


# call Main function in command line 
def main(root_url, years, keyword, bucket_name, folder_path, zip_dir, proj_epsg, xRes, yRes):
    """
    Call every function to creat cog and upload to S3 bucket 
    """
    # Step 1: load log.txt content from S3 and create an empty list for lastRun content 
    filenames = list_files_in_s3(bucket_name, folder_path)
    if 'log.txt' in filenames:
        print('Log file exists, loading it from S3 bucket') 
        log_content = open_file_from_s3(bucket_name, folder_path, file_name='log.txt')
    else: 
        # Open the file in read and write mode ('r+')
        print('Log file does not exist, creating an empty string as the content of log.txt') 
        log_content = ' '
    lastRun = ' '
    count = 0 
    for year in years: 
        print(f'Start processing the COG for year {year}')
        # Step 2: get a list of the zip links for specific year  
        zip_links = get_zip_links(root_url, year, keyword)
        # Step 3: for each zip url link, check: 
        # 1) if the link has been translated 
        # 2) If not translated, pass the link to lastrun list 
        # 3) Get the full url link, and then download and unzip the file 
        # 4) Get the geotiff path in the unzipped folder 
        # 5) Convert the geotiff to vog 
        # 6) Upload the zip and cog to S3 bucekt 
        # 7) Update log_content 
        # 8) Exit loop, upload log_content to S3 bucket as log.txt 
        for link in zip_links: 
            print(f'Start processing {link}')
            if link not in log_content: 
                print(f'This zip has not been translated and proceed to translation')
                unzip_dir = download_and_unzip(link, zip_dir)
                #print(f'unzip_dir is: {unzip_dir}')        
                geotiff_filename, geotif_path =  geotiff_path(unzip_dir=unzip_dir, format='.tif', keyword = keyword)
                input_path = os.path.join(os.getcwd(), geotif_path[0])
                #print(geotiff_filename)
                #print(geotif_path)
        
                reproject_raster(input_path=input_path, dstSRS=proj_epsg, xRes=xRes, yRes=yRes)
                proj_path=input_path.replace('.tif', '_reprj.tif')
                output_path = input_path.replace('.tif', '_cog.tif')
        
                # Extract datetime from the file name 
                time_str = link.split('_')[-1].split('.')[0]
                date_str = link.split('_')[-2].split('.')[0]
                timestamp =date_str  +"_" + time_str
                datetime_obj = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
                formatted_datetime = datetime_obj.strftime('%Y:%m:%d %H:%M:%S')
                #print(formatted_datetime)

                is_valid = geotiff_to_cog(proj_path, output_path, datetime_value=formatted_datetime)
                #print_gdal_info(output_path, print_keys=True)
                #TODO upload cog to datacube S3 
                zip_file_path = os.path.join(os.getcwd(), unzip_dir)
                zip_file_path = zip_file_path + '.zip'
                  
                upload_file_to_s3(bucket_name, folder_path=folder_path+'zip/', local_file_path=zip_file_path, new_file_name=os.path.basename(zip_file_path))
                upload_file_to_s3(bucket_name, folder_path=folder_path+'cog/', local_file_path=output_path, new_file_name=os.path.basename(geotif_path[0]))
                    
                count += 1
                log_content = log_content + '\n' + link
                lastRun = lastRun + '\n' + is_valid
            else:
                print(f'{link} has been translated') 
        #Upload log.txt to S3 after running for each year 
        upload_fileContent_to_s3(bucket_name, file_key=folder_path + 'log.txt', file_content=log_content)
    # Upload the lastRun.txt to s3
    upload_fileContent_to_s3(bucket_name, file_key=folder_path + 'lastRun.txt', file_content=lastRun)
    return lastRun

# Set up argument parsing
if __name__ == "__main__":
    """
    root_url = 'https://data.eodms-sgdot.nrcan-rncan.gc.ca' 
    years = [year for year in range(2005, 2024)]
    keyword = 'RiverIce' 
    bucket_name = 'nrcan-egs-product-archive'
    folder_path='Datacube/RiverIce/'
    zip_dir = 'zip_test'
    proj_epsg = 'EPSG:3978'
    xRes=5
    yRes=5
    """
    parser = argparse.ArgumentParser(description='Process EGS-publish-to-datacube parameters.')

    parser.add_argument('root_url', type=str, help='Root URL')
    parser.add_argument('years', type=int, nargs='+', help='List of years')
    parser.add_argument('keyword', type=str, help='Keyword')
    parser.add_argument('bucket_name', type=str, help='Bucket name')
    parser.add_argument('folder_path', type=str, help='Folder path')
    parser.add_argument('zip_dir', type=str, help='Zip directory')
    parser.add_argument('proj_epsg', type=str, help='Projection EPSG code')
    parser.add_argument('xRes', type=float, help='Resolution in X')
    parser.add_argument('yRes', type=float, help='Resolution in Y')

    args = parser.parse_args()

    lastRun = main(args.root_url, args.years, args.keyword, args.bucket_name, args.folder_path, args.zip_dir, args.proj_epsg, args.xRes, args.yRes)
    print(f'The lastRun logging is,  \n{lastRun}')
"""    
# Run the scripts from the termial 
# Note that [years] should be a space-separated list of years (e.g., 2005 2006 2007).
python main.py [root_url] [years] [keyword] [bucket_name] [folder_path] [zip_dir] [proj_epsg] [xRes] [yRes]
"""
