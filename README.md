# EGS-publish-to-datacube | datacube/pipeline/egs
Data publication pipeline that generates COGs, creates STAC metadata, and publishes to the CCMEO datacube
## The python 3.10 datacube pipeline 
 - The source data is no longer zipped files.
 - The new source data will be from the data production pipeline currently in development.
 - The data production pipeline will be the input to this new data publication pipeline.
## Creating your conda environment
The conda env can be created directly from the yml file.  
 ```shell
 conda env create -f egs_env.yml
 ```
## Running the code command line
### Setting environment variables
 - set the AWS security credentials
 - set the ddb authentication env variables
 ```shell
 (SET|export) DDB_AUTH_USER=<username>
 (SET|export) DDB_AUTH_PASSWORD=<password>
 ```
 ### Create COG, publish to datacube, create and publish STAC md
 ```shell
 # To list help
 python {path-to}/src/main310.py -h

 # To cogify, publish and create stac
 python {path-to}/src/main310.py {filename} {resoltion}
 ```

 ## Running the code in a container
 See the full instruction in the Containerfile top level [comments](/Containerfile.gdal-python)
 ### Files required for the image build
  - .git-credentials: holds the username and access token for git.geoproc
 ### Files Required for container run
  - .env : holds the AWS and DDB authentication
 ### Example files
 #### .git-credentials
 ```shell
 https://{git.geoproc-user-name}:{git-geproc-access-token}@git.geoproc.geogc.ca
 ```
 ### .env
 ```shell
 # ddb-api authentication
 DDB_AUTH_USER={ddb-user}
 DDB_AUTH_PASSWORD={ddb-password}

 # AWS credentials
 AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}
 AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}
 AWS_SESSION_TOKEN={AWS_SESSION_TOKEN}
 ```
 ## Python 3.10 code management
  - all new python 3.10 code is under the src directory

 ## Original Python 3.6 code managment
  - The original 3.6 README.md has been renamed [README36.md](README36.md)
  - the COG_creation directory: holds the python 3.6 code
  - if reusable in 3.10 it will be used, if not a 3.10 version will be created.
  - minor modifications will be done as required
  - an alignment with pep8 is being considered for all code being used by 3.10 version