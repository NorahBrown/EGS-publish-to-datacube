# Creating log files for existing cogs on the EGS S3 bucket 
import boto3 
from bs4 import BeautifulSoup
import requests
import json 

from get_zip_links import * 
from s3_operations import list_files_in_s3,upload_fileContent_to_s3

# Test 1: cross check zip_links and cog_list
bucket_name = 'nrcan-egs-product-archive'
root_url = 'https://data.eodms-sgdot.nrcan-rncan.gc.ca'
years = [year for year in range(2005, 2024)]   
keyword = 'RiverIce' 
zip_links = []
for year in years: 
    links = get_zip_links(root_url, year, keyword)
    zip_links.extend(links)
print(len(zip_links))


# Test2: 
log_content = ' '
cog_list =  list_files_in_s3(bucket_name, folder_path= 'Datacube/RiverIce/cog')
for link in zip_links: 
    filename =link.split('/')[-1]
    filename = filename.replace('.zip', '.tif')
    if filename in cog_list: 
        print(f'{link} is in the cog_list')
        log_content = log_content + '\n' + link
        
print(len(log_content))
upload_fileContent_to_s3(bucket_name, file_key='Datacube/RiverIce/' + 'log.txt', file_content=log_content)

# Test3  - put the zip url as json in S3 bucket
for link in zip_links: 
    data = {
    'River Ice product url': link
    }
    json_object = json.dumps(data, indent=4)
    filename =link.split('/')[-1]
    filename = filename.replace('.zip', '.json')
    upload_fileContent_to_s3(bucket_name, file_key='Datacube/RiverIce/json/' + filename, file_content=json_object)
