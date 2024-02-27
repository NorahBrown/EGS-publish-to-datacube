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
 python {path-to}/src/main.py -h

 # To cogify, publish and create stac
 python {path-to}/src/main.py {filename} {resoltion}
 ```

 ## Running the code in a container
 See the full instruction in the Containerfile top level [comments](/Containerfile.gdal-python)
 
 ### Files Required for container run
  - .env : holds the AWS and DDB authentication
 ### Example file
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
