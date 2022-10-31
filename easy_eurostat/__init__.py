import os
import time
import gzip
import zipfile
import pandas as pd
import geopandas as gpd
import urllib.request

def file_age(filename):
    '''
    Return the age of the given file in hours
    :param str filename: The name of the fie
    :return: The age of the fie in hours (rounded to whole hours)
    :rtype: int
    
    '''
    if os.path.exists(filename):
        return int((time.time() - os.path.getmtime(filename)) / 3600)
    else:
        return -1

def download_url(url, filename, binary=False, unzip=False):
    '''
    Download the given URL and save under filename.
    If the filename contains a directory, it is assoumed the directory exists.
    
    :param str url: The URL to download
    :param str filename: The filename to save the file under
    '''
    if os.path.exists(filename) and file_age(filename) < 24:
        # Cached version exists and is less than a day old
        return
    try:
        with urllib.request.urlopen(url) as resp:
            if unzip:
                with gzip.GzipFile(fileobj=resp) as data:
                    file_content = data.read()
            else:
                file_content = resp.read()
            if not binary:
                file_content = file_content.decode('utf-8')
        with open(filename, 'wb' if binary else 'w') as f:
            f.write(file_content)
    except Exception as e:
        print(e)
        
        
def get_eurostat_dictionary(dictionary, inverse=False):
    '''
    Return a dictionary from Eurostat.
    :param str dictionary: The name of the dictionary to download
    :param bool inverse: If True, return value -> key mapping, defaults to False
    :return: A Python dictionary with the key -> value pair
    '''
    dictionary = dictionary.lower()
    url = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?sort=1&downfile=dic%2Fen%2F" +\
          dictionary + ".dic"
    filename = os.path.join("cache", dictionary + ".dic")
    download_url(url, filename)

    try:
        with open(filename) as f:
            d = {}
            for line in f:
                if len(line) > 1:
                    row = line.split('\t')
                    d[row[0]] = row[1].strip()
        if inverse:
            d = {v: k for k, v in d.items()}
        return d
    except:
        return {}


def get_eurostat_dataset(dataset, replace_codes=True, transpose=True, keep_codes=[]):
    '''
    Return a dataset from Eurostat.
    Downloads the dataset,replaces the code columns with their associated meaning (optional) and
    transposes the column for improved usability (optional). Depeniding on the usage of the data the
    transposed version is easier to use. E.g. for analysis over time the transposed is easier, for 
    comparing country values the original version is easier.
    It is possible to specify a list of codes not to transalte, eg for keeping country codes instead
    of translating to the fullname when merging with other datasets is required
    :param str dataset: The name of the dataset to download
    :param bool replace_codes: If True replaces codes with their value , defaults to True
    :param bool transpose: If True transpose the resulting table with the code  columns as indeces, defaults to True
    :param list keep_code: List of codes not to replace, defaults to []
    :return: A Python dictionary with the key -> value pair
    '''
    dataset = dataset.lower()
    filename = os.path.join("cache", dataset + ".tsv")
    url = "https://ec.europa.eu/eurostat/estat-navtree-portlet-prod/BulkDownloadListing?file=data/" + \
          dataset + ".tsv.gz"
    download_url(url, filename, unzip=True)
    
    df = pd.read_csv(filename, sep=",|\t| [^ ]?\t", na_values=":", engine="python")
    df.columns = [x.split('\\')[0].strip(' ') for x in df.columns]
    # Now get the dictionary columns
    with open(os.path.join("cache", dataset + ".tsv")) as f:
        first_line = f.readline()
    codes = first_line.split('\t')[0].split('\\')[0].split(',')
    # Replace codes with value
    if replace_codes:
        for c in codes:
            if not c in keep_codes:
                code_list = get_eurostat_dictionary(c)
                df[c] = df[c].replace(code_list)
    # Transpose the table
    if transpose:
        df = df.set_index(codes).transpose()
    return df

def get_eurostat_geodata(lvl=0):
    '''
    Return the geodata of the European countries
    The features are filterd on the NUTS level code. Level 0 contains the countries,
    level 1 the regions within countries, etc.
    :param int lvl: The NUTS level to download, defaults to 0
    '''
    url = "https://gisco-services.ec.europa.eu/distribution/v2/nuts/shp/NUTS_RG_20M_2021_3035.shp.zip"
    filename = os.path.join('cache', 'NUTS_RG_20M_2021_3035.shp.zip')
    download_url(url, filename, binary=True)

    borders = gpd.read_file(filename)  
    return borders[borders['LEVL_CODE'] == lvl]
