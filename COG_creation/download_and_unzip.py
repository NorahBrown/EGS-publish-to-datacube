import requests
import os 
import zipfile

def download_and_unzip(zip_url, zip_dir): 
    """
    Given a URL link, download the zip file, unzip to a local folder with the same filename 
    :param zip_url: a full url path to the .zip fi;e 
    :param zip_dir: a folder name to save the zip downloads, a path will be created locally use the zip_dir
    """
    # Make temporary directory to save the zip downloads  
    if not os.path.exists(zip_dir): 
        os.makedirs(zip_dir, exist_ok=True)
        print("Directory created successfully!")
    else:     
        print("Directory already exists.")
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

def geotiff_path(unzip_dir, format, keyword): 

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
        if keyword in item and item.endswith(format):
            count += 1 
            geotif_path = os.path.join(unzip_dir, item)
            geotiff_paths.append(geotif_path)
            geotiff_filenames.append(item)
    #print('{} {} are found in this folder.'.format(count, format))
    return (geotiff_filenames, geotiff_paths)

# Usage 
zip_url = 'https://data.eodms-sgdot.nrcan-rncan.gc.ca/public/EGS/2016/RiverIce/CAN/ON/RiverIce_CAN_ON_Attawapiskat_20160420_114518.zip'
zip_dir = 'zip_test'
unzip_dir = download_and_unzip(zip_url, zip_dir)
print('unzip_dir is: {}'.format(unzip_dir))

geotiff_filenames, geotif_paths =  geotiff_path(unzip_dir=unzip_dir, format='.tif', keyword='RiverIce')
print(geotiff_filenames)
print(geotif_paths)

