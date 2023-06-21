from osgeo import gdal
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
    
    
# Usage
input_path ='.../RiverIce_CAN_NT_UpperMackenzieMillsLake_20210429_012858.tif'
output_path = '.../RiverIce_CAN_NT_UpperMackenzieMillsLake_20210429_012858_cog.tif'

reproject_raster(input_path, dstSRS='EPSG:3978', xRes=5, yRes=5)
proj_path=input_path.replace('.tif', '_reprj.tif')
print_gdal_info(proj_path, print_keys=True)
