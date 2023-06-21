import requests
import os 
import zipfile
from osgeo import gdal
from bs4 import BeautifulSoup
import boto3
import logging
from botocore.exceptions import ClientError
from datetime import datetime

#TODO Change the Function to recursively retrieve the ZIP file links
def get_zip_links(root_url, year, keyword): 
    """
    Given root url, a year, and search keyword, returning all the urls contain the zip files  
    Beautifulsoup documentation: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    :param root_url: EODMS ESG ftp root url https://data.eodms-sgdot.nrcan-rncan.gc.ca/public/EGS
    :param year: year for the EGS product 
    :param keyworf: type of EGS product, can be RiverIce or Flood. 
    """
    count = 0 
    zip_links = []
    url = f'{root_url}/public/EGS/{year}/'

    # Send a GET request to the URL
    response = requests.get(url)
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extracting all the URLs found in the url page 
    href_list = [link.get('href') for link in soup.find_all('a')]
    href_str = " ".join(href_list)
    if keyword in href_str: 
        # Extracting first subdirectory: /public/EGS/2016
        for href in href_list:
            if keyword in href:
                subdir1 = root_url + href
                print(f'Folder contains keyword {keyword},  continue to search in the first level subdirectory {subdir1}') 
                response = requests.get(subdir1)
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extracting second subdirectory: /public/EGS/2016/RiverIce
                for link in soup.find_all("a"): 
                    subdir1_href = link.get('href')
                    subdir2 = root_url + subdir1_href
                    if keyword in subdir1_href and not subdir1_href.endswith(".zip"): 
                        print(f'Folder contains keyword {keyword} but not the zip file,  continue to search in second level subdirectory {subdir2}') 
                        response = requests.get(subdir2)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Extracting thrid subdirectory: /public/EGS/2016/RiverIce/CAN
                        for link in soup.find_all("a"): 
                            subdir2_href = link.get('href')
                            subdir3 = root_url + subdir2_href
                            if keyword in subdir2_href and not subdir2_href.endswith(".zip"): 
                                print(f'Folder contains keyword {keyword} but not the zip file,  continue to search in third level subdirectory {subdir3}') 
                                response = requests.get(subdir3)
                                soup = BeautifulSoup(response.content, 'html.parser')
                                # Extracting forth(normally the last for EGS strcuture) subdirectory: /public/EGS/2016/RiverIce/CAN/Prov
                                for link in soup.find_all("a"): 
                                    subdir3_href = link.get('href')
                                    subdir4 = root_url + subdir3_href
                                    # Append only the zip files 
                                    if keyword in subdir3_href and subdir3_href.endswith(".zip"): 
                                        zip_links.append(subdir4)
                                        count += 1 
                            elif keyword in subdir2_href and subdir2_href.endswith(".zip"):
                                zip_links.append(subdir3)
                                count += 1
                    elif keyword in subdir1_href and subdir1_href.endswith(".zip"): 
                        zip_links.append(subdir2)
                        count += 1
                    else: 
                        pass 
            else:
                pass       
    else: 
        print(f'Year {year} does not have {keyword} instance recorded, stop searching and return zero links')
    # Check if keywords exist in the url subdirectory. Continue search only when the keyword exist, else exist  
    print(f'There are {count} {keyword} instance recorded in {url}')
    return zip_links


def download_and_unzip(zip_url, zip_dir): 
    """
    Given a URL link, download the zip file, unzip to a local folder with the same filename 
    :param zip_url: a full url path to the .zip fi;e 
    :param zip_dir: a folder name to save the zip downloads, a path will be created locally use the zip_dir
    """
    # Make temporary directory to save the zip downloads  
    os.makedirs(zip_dir, exist_ok=True)
    # Download the zip file 
    filename = os.path.join(zip_url.split('/')[-1])
    zip_file_path = os.path.join(zip_dir, filename)
    response = requests.get(zip_url)
    # try-except 
    with open(zip_file_path, 'wb') as file:
        file.write(response.content)

    # Unzip 
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        unzip_dir = os.path.join(zip_dir, filename[:-4]) 
        os.makedirs(unzip_dir, exist_ok=True)
        zip_ref.extractall(unzip_dir)
    return unzip_dir

def geotiff_path(unzip_dir, format): 

    """
    Given the path of unzippped files, return the Geotiff filename and file_path 
    :param unzip_dir: the local path for the unzipped folder
    :param format: file format for the search, in this case is .tif
    """
    geotiff_filenames = []
    geotiff_paths = []
    count = 0 
    for item in os.listdir(unzip_dir): 
        #print('filename is {}' .format(item))
        if item.endswith(format):
            count += 1 
            geotif_path = os.path.join(unzip_dir, item)
            geotiff_paths.append(geotif_path)
            geotiff_filenames.append(item)
    print('{} {} are found in this folder.'.format(count, format))
    return (geotiff_filenames, geotiff_paths)


def print_gdal_info(file_path, print_keys=True):
    """"
    Print gdal.Info giventhe file_path 
    """
    # Use gdal.Info() to obtain raster information 
    info = gdal.Info(file_path, format='json')
    if print_keys: 
        print("Raster Information Keys:")
        for key, value in info.items():
            print(f"------------------------------------------------------ \n {key}: {value}")
    else: 
        print('gdal info: ')
        print(info) 
    return info
    

def reproject_raster(input_path, dstSRS, xRes, yRes): 
    """"
    Reproject geotiff or cog to a desinination projection, with a specific xRes and yRes
    :param input_path: file path
    :param dstSRS: desination projection in EPSG:xxxx
    :param xRes and yRes: resolution 
    """
    reProj_path = input_path.replace('.tif', '_reprj.tif')
    # Open input Geotiff, reproject, resize, and close the Geotiff  
    warp_options = gdal.WarpOptions(
        format='GTiff', 
        dstSRS = dstSRS, 
        xRes=xRes, 
        yRes=yRes
    )
    ds = gdal.Warp(destNameOrDestDS=reProj_path, srcDSOrSrcDSTab=input_path, options=warp_options)
    
    # Close the data 
    ds = None 
    
 
def geotiff_to_cog(input_path, output_path, datetime_value):
    """
    Translate geotiff to COG using using gdal.translate, and add TIFFTAG_DATETIME
    :param input_path: str, Geotiff path include file name  
    :param output_path: str, COG path include file name 
    :param datetime_value: date in format '2021:05:03 01:29:09'
    """
    # Set the COG options, see creation options here: https://gdal.org/drivers/raster/cog.html#raster-cog
    translate_options = gdal.TranslateOptions(
        # Default option: internal overview, block size 512 x 512
        format='COG', 
        creationOptions=['COMPRESS=LZW',
                         'BLOCKSIZE = 512', 
                         'BLOCKSIZE = 512'
                         ],
        )    
    # Translate the TIFF to COG
    ds = gdal.Translate(output_path, input_path, options=translate_options)    
    
    # Add TIFFTAG_DATATIME 
    try: 
        if ds is not None: 
            ds.SetMetadataItem("TIFFTAG_DATETIME", datetime_value)
    except Exception as e: 
        print(f"gdal.Translate returns a None object created an error when setting TIFFTAG_DATETIME for {input_path}: {str(e)}")
    
    # Close the data
    ds = None 


def list_files_in_s3(bucket_name, folder_path):
    """ List a filenames in a S3 bucket or a S3 folder  
    Note: if there are too many records (>999) to pricessm we may need to paginate 
    :param bucket_name: string, name of the bucket 
    :param folder_path: string, prefix, can be empty 
    :return a list of filenames within the bucket 
    """
    s3_client = boto3.client('s3')
    response = s3_client.list_objects_v2(Bucket = bucket_name, Prefix = folder_path)
    filename_list = []
    count = 0 
   # print(response)
    for obj in response.get('Contents', []):
        if obj['Key'] != folder_path:  # Exclude the folder itself from the results
            filename = obj['Key'].split('/')[-1] 
            if filename: # Exclude the folder inside the folder_path 
                filename_list.append(filename)
                count += 1 
    print(f"{count} files are included in the bucket {bucket_name} in folder {folder_path}")
    return filename_list

def open_file_from_s3(bucket_name, folder_path, file_name):
    """Open a S3 file from bucket, folder_path and filename and return the body as a string
    :param bucket: Bucket name
    :param filename: Specific file name to open
    :return: body of the file as a string
    """
    try: 
        s3_client = boto3.client('s3')
        s3_key = folder_path + file_name
        # Download the file from S3
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        file_content = response['Body'].read().decode('utf-8')
        return file_content
    except ClientError as e:
        logging.error(e)
        return False 

def delete_file_s3(bucket_name, folder_path, filename):
    """Delete a S3 file from bucket, folder_path and filename and return the body as a string
    :param bucket: Bucket name
    :param filename: Specific file name to open
    :param 
    :return: body of the file as a string
    """
    s3_client = boto3.client('s3')
    s3_key = folder_path + filename 
    error_msg = None 
    try: 
        s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
        print(f"Filenames: {filename} deleted sucessfully from bucket {bucket_name} in folder {folder_path}")
    except ClientError as e: 
        logging.error(e)
        error_msg += e
    return error_msg

def upload_fileContent_to_s3(bucket_name, file_key, file_content):
    """
    Given the text content, upload the content to S3 as a text file 
    :param bucket name: name of the bucket 
    :param file_key: S3 folder_path + 'log.txt'
    :param: file_content: text body 
    """
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name, file_key)
    try: 
        obj.put(Body=file_content)
    except ClientError as e:
        logging.error(e)
        return False 
    return True

def upload_file_to_s3(bucket_name, folder_path, local_file_path, new_file_name):
    """Upload a file to S3 bucket 
    :param bucket: Bucket name
    :param folder_path: S3 folder prefix 
    :param local_file_path: flocal full path for the file to be uploaded 
    :param new_file_name: new file name when uploaded to S3
    :return: True or False 
    """
    s3_client = boto3.client('s3')       
    # Concatenate the folder path and file name 
    s3_key = folder_path + new_file_name
    try: 
        s3_client.upload_file(local_file_path, bucket_name, s3_key)
    except ClientError as e:
        logging.error(e)
        return False 
    return True 

#Main function for river ice cog generate pipeline 
def riverice_cog_pipeline(root_url, year, keyword, bucket_name, folder_path, zip_dir, proj_epsg, xRes, yRes):
    # Step 1: get a list of the zip links for specific year  
    zip_links = get_zip_links(root_url, year, keyword)
    # Step 2: Load log.txt content from the S3 
    filenames = list_files_in_s3(bucket_name, folder_path)
    if 'log.txt' in filenames:
        print('Log file exists, loading it from S3 bucket') 
        log_content = open_file_from_s3(bucket_name, folder_path, file_name='log.txt')
    else: 
        # Open the file in read and write mode ('r+')
        print('Log file does not exist, creating a empty string as the content of log.txt') 
        log_content = ' '
    # Step 3: Loop through link in the zip_links, and check 
    # 1) if the link has been translated 
    # 2) If not translated, pass the link to lastrun list 
    # 3) Get the full url link, and then download and unzip the file 
    # 4) Get the geotiff path in the unzipped folder 
    # 5) Convert the geotiff to vog 
    # 6) Upload the zip and cog to S3 bucekt 
    # 7) Update log_content 
    # 8) Exit loop, upload log_content to S3 bucket as log.txt 
    lastRun = []
    count = 0 
    #print(zip_links)
    for link in zip_links: 
        print(link)
        print(type(link))
        if link not in log_content: 
            print(f'{link} has not been translated, continue to next step')
            unzip_dir = download_and_unzip(link, zip_dir)
            print(f'unzip_dir is: {unzip_dir}')
        
            geotiff_filename, geotif_path =  geotiff_path(unzip_dir=unzip_dir, format='.tif')
            input_path = os.path.join(os.getcwd(), geotif_path[0])
            #print(geotiff_filename)
            #print(geotif_path)
        
            reproject_raster(input_path=input_path, dstSRS=proj_epsg, xRes=xRes, yRes=yRes)
            proj_path=input_path.replace('.tif', '_reprj.tif')
            output_path = input_path.replace('.tif', '_cog.tif')
        
            # Extract datetime from the file name 
            # Extract the timestamp from the string
            time_str = link.split('_')[-1].split('.')[0]
            date_str = link.split('_')[-2].split('.')[0]
            timestamp =date_str  +"_" + time_str
            datetime_obj = datetime.strptime(timestamp, '%Y%m%d_%H%M%S')
            formatted_datetime = datetime_obj.strftime('%Y:%m:%d %H:%M:%S')
            print(formatted_datetime)

            geotiff_to_cog(proj_path, output_path, datetime_value=formatted_datetime)
            #print_gdal_info(output_path, print_keys=True)
            #TODO upload cog to datacube S3 
            zip_file_path = os.path.join(os.getcwd(), unzip_dir)
            zip_file_path = zip_file_path + '.zip'
            print(zip_file_path)
            upload_file_to_s3(bucket_name, folder_path=folder_path+'zip/', local_file_path=zip_file_path, new_file_name=os.path.basename(zip_file_path))
            upload_file_to_s3(bucket_name, folder_path=folder_path+'cog/', local_file_path=output_path, new_file_name=os.path.basename(geotif_path[0]))
            count += 1
            log_content = log_content + '\n' + link
        else:
            print(f'{link} has been translated') 
    # Upload the log.txt to s3
    file_key = folder_path + 'log.txt'
    upload_fileContent_to_s3(bucket_name, file_key, file_content=log_content)
    return log_content



# Translate and upload EGS RiiverIce cog to S3 bucket 
root_url = 'https://data.eodms-sgdot.nrcan-rncan.gc.ca'
yrs = [2005, 2008, 2011] + [year for year in range(2013, 2024)] 
keyword = 'RiverIce' 
bucket_name = 'nrcan-egs-product-archive'
folder_path='Datacube/RiverIce/'
#TODO need to create os.path.join to provide the full path for the folder 
zip_dir = 'zip_test'
proj_epsg = 'EPSG:3978'
xRes=5
yRes=5
for year in yrs:
   log_content = riverice_cog_pipeline(root_url, year, keyword, bucket_name, folder_path, zip_dir, proj_epsg, xRes, yRes)
   #print (f'For year {year}, the logs re \n {log_content}')

