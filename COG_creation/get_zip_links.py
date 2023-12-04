from bs4 import BeautifulSoup
import requests
#TODO Change the Function to recursively retrieve the ZIP file links
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

"""
#Test
root_url = 'https://data.eodms-sgdot.nrcan-rncan.gc.ca'
year = 2018  
keyword = 'RiverIce' 
zip_links = get_zip_links(root_url, year=2020, keyword='Flood')
print(zip_links)
"""