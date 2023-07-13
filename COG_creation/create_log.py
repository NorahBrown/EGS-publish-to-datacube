# Creating log files for existing cogs on the EGS S3 bucket 
import boto3 
from bs4 import BeautifulSoup
import requests
import json 

# Get the url link of all the River Ice instance 
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
                #print(f'Folder contains keyword {keyword},  continue to search in the first level subdirectory {subdir1}') 
                response = requests.get(subdir1)
                soup = BeautifulSoup(response.content, 'html.parser')
                # Extracting second subdirectory: /public/EGS/2016/RiverIce
                for link in soup.find_all("a"): 
                    subdir1_href = link.get('href')
                    subdir2 = root_url + subdir1_href
                    if keyword in subdir1_href and not subdir1_href.endswith(".zip"): 
                        #print(f'Folder contains keyword {keyword} but not the zip file,  continue to search in second level subdirectory {subdir2}') 
                        response = requests.get(subdir2)
                        soup = BeautifulSoup(response.content, 'html.parser')
                        # Extracting thrid subdirectory: /public/EGS/2016/RiverIce/CAN
                        for link in soup.find_all("a"): 
                            subdir2_href = link.get('href')
                            subdir3 = root_url + subdir2_href
                            if keyword in subdir2_href and not subdir2_href.endswith(".zip"): 
                                #print(f'Folder contains keyword {keyword} but not the zip file,  continue to search in third level subdirectory {subdir3}') 
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

# List all cog files in the S3 bucket 
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

# Upload files to S3 
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


# Usage 1: cross check zip_links and cog_list
bucket_name = 'nrcan-egs-product-archive'
root_url = 'https://data.eodms-sgdot.nrcan-rncan.gc.ca'
years = [year for year in range(2005, 2024)]   
keyword = 'RiverIce' 
zip_links = []
for year in years: 
    links = get_zip_links(root_url, year, keyword)
    zip_links.extend(links)
print(len(zip_links))

"""
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
"""
# Usage 2 - put the zip url as json in S3 bucket
for link in zip_links: 
    data = {
    'River Ice product url': link
    }
    json_object = json.dumps(data, indent=4)
    filename =link.split('/')[-1]
    filename = filename.replace('.zip', '.json')
    upload_fileContent_to_s3(bucket_name, file_key='Datacube/RiverIce/json/' + filename, file_content=json_object)
