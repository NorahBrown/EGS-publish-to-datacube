# Python standard library
import os 
from pathlib import Path
import sys
from typing import Union

# Custom packages
import boto3

from nrcan_ssl.ssl_utils import nrcan_ca_patch, SSLUtils
    # ...
ssl_utils = SSLUtils()
ssl_utils.set_nrcan_ssl()


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
    except Exception as e:
        print(e)
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
    except Exception as e: 
        error_msg += e
    return error_msg

def upload_fileContent_to_s3(bucket_name:str, file_key:str, file_content:str,extra_args:dict=None):
    """
    Given the text content, upload the content to S3 as a text file 
    :param bucket name: name of the bucket 
    :param file_key: S3 folder_path + 'log.txt'
    :param: file_content: text body
    :param extra_args: extra_args see boto3 s3 upload_file ExtraArgs
    """
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name, file_key)

    try: 
        if extra_args:
            obj.put(Body=file_content,**extra_args)
        else:
            obj.put
    # TODO pass back more informative information
    except Exception as e:
        return False,e
    return True,None

def upload_file_to_s3(bucket_name:str, folder_path:str, local_file_path:Union[str,Path], new_file_name:str,extra_args:dict=None):
    """Upload a file to S3 bucket 
    :param bucket: Bucket name
    :param folder_path: S3 folder prefix 
    :param local_file_path: local full path for the file to be uploaded 
    :param new_file_name: new file name when uploaded to S3
    :param extra_args: extra_args see boto3 s3 upload_file ExtraArgs
    :return: True, None or False, error 
    """
    #s3_client = boto3.client('s3', verify=False)
    s3_client = boto3.client('s3')

    # Concatenate the folder path and file name 
    s3_key = folder_path + new_file_name
    try: 
        # Add public read ACL 
        s3_client.upload_file(local_file_path, bucket_name, s3_key, ExtraArgs=extra_args)
    # TODO pass back more information
    except Exception as e:
        return False, e

    return True, None

def download_file_from_s3(bucket_name, folder_path, local_dir, format):
    """
    :param format: string, file extension '.tif'
    """
    # Create a Boto3 S3 client
    s3_client = boto3.client('s3')
    # List objects in the S3 bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix = folder_path)
    # Iterate over the objects in the bucket
    for obj in response['Contents']:
        # Get the file key (path) of each object
        file_key = obj['Key']
        # Check if the file is a .tif file
        if file_key.endswith(format):
            # Create the local directory if it doesn't exist
            os.makedirs(local_dir, exist_ok=True)
            # Specify the local file path for downloading
            local_file_path = os.path.join(local_dir, file_key.split('/')[-1])
            print(local_file_path)
            # Download the file from S3
            s3_client.download_file(bucket_name, file_key, local_file_path)
        
            print(f"Downloaded: {file_key}")

    print(f"All {format} files downloaded.")

def list_files_with_extension(directory, extension):
    filenames = []
    for file in os.listdir(directory):
        if file.endswith(extension):
            filenames.append(file)
    return filenames


ssl_utils.unset_nrcan_ssl()
"""
# Test 
#bucket_name = 'nrcan-egs-product-archive'
#folder_path='Datacube/RiverIce/json/'
bucket_name = 'datacube-stage-data-public'
folder_path='store/water/river-ice-canada-archive/'

download_file_from_s3(bucket_name, folder_path, local_dir='C:/Users/xcai/Documents/EGS_projects/RiverIce/cog/', format='.json')
upload_file_to_s3(bucket_name, folder_path, local_file_path, new_file_name)


# Test 2 
directory = 'C:/Users/xcai/Documents/EGS_projects/RiverIce/assets'
extension = '.png'

filenames = list_files_with_extension(directory, extension)
print(len(filenames))
for filename in filenames: 
    print(filename)
    upload_file_to_s3(bucket_name, folder_path, local_file_path=directory+'/'+filename, new_file_name=filename)
"""