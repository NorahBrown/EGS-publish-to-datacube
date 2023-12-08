# EGS-publish-to-datacube
Pipeline to generate COGs, create STAC metadata, and publish to CCMEO datacube
## The python 3.10 datacube pipeline 
 - The source data is not zipped files, but will eventually be included in the new data production pipeline.
 # Creating your conda environment
 `conda env create -f egs_env.yml``

 - the COG_creation directory: holds the python 3.6 code
if reusable in 3.10 it will be used, if not a 3.10 version will be created.

# ORIGINAL README CONTENT used to COGIFY full archive up to 2022
## Run the COG creation scripts  
### Create the python environment  
Note, VPN needs to be turned off for this step to aovid SSLCertVerificationError. 
We will create an Python environment to install the egs_env.yml, and install two additional Python packages BeautifulSoup and rio-cogeo 
```bash
cd path/to/egs_env.yml
conda env create -f egs_env.yml
conda activate py36
conda install rio-cogeo
conda install beautifulsoup4
conda list 
```

### Run the main.py file in terminal 
```bash
python main.py "https://data.eodms-sgdot.nrcan-rncan.gc.ca" "2005 2006 2007" "RiverIce" "nrcan-egs-product-archive" "Datacube/RiverIce/" "zip_test" "EPSG:3978" 5 5
```
