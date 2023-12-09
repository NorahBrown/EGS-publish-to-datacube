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
