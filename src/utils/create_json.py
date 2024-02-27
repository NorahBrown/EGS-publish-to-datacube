"""
Datacube pipeline COG and STAC creation and publication

Method to create a Json file associate to each item in the Datacube

"""
import json

def create_json(filename,ftp_url):
    # Data to be written
    dictionary = {
	    "River Ice product url": ftp_url,
    }

    # Serializing json
    json_object = json.dumps(dictionary, indent=4)

    try:
    # Writing to sample.json
        with open(filename, "w") as outfile:
            outfile.write(json_object)
    except Exception as e:
        return False,e
    
    return True, None     
