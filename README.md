# EGS-publish-to-datacube
Pipeline to generate COGs, create STAC metadata, and publish to CCMEO datacube
## The python 3.10 datacube pipeline 
 - The source data is not zipped files, but will eventually be included in the new data production pipeline.
## Creating your conda environment
The conda env can be created directly from the yml file.  
 ```shell
 conda env create -f egs_env.yml
 ```
 ## Python 3.10 code management
  - all new python 3.10 code is under the src directory
 ## Original Python 3.6 code managment
  - The original 3.6 README.md has been renamed [README36.md](README36.md)
  - the COG_creation directory: holds the python 3.6 code
  - if reusable in 3.10 it will be used, if not a 3.10 version will be created.
  - minor modifications will be done as required
  - an alignment with pep8 is being considered for all code being used by 3.10 version
