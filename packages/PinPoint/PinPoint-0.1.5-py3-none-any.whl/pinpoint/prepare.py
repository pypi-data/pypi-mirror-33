import csv
import gzip
import io
import re
import sys
import time
import urllib.request
from collections import OrderedDict
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import nvector as nv
from scipy import spatial

from . import config

try:
    import ujson as json
except ImportError:
    import json

csv.field_size_limit(131072*10)


def save_resource(data_dict, path):
    """
    Save a dictionary in json format in a compressed gzip file. 
    
    Args:
        data_dict (dict):  data to be saved
        path (pathlib.Path or str): file path (should contain gzip file extension, or it will be added)
    """
    path = Path(path)
    if path.suffix != '.gzip':
        path = path.with_suffix(path.suffix + '.gzip')
    with gzip.open(path, 'wt') as outfile:
        json.dump(data_dict, outfile, indent=4)


def load_resource(path):
    """
    Load a dictionary from a gzip compressed json file.
    
    Args:
        path (pathlib.Path or str): file path (should contain gzip file extension) 

    Returns (dict): loaded data dictionary
    """

    with gzip.open(path, 'r') as infile:
        data = json.load(infile)
    return data


def download_resource(url, path):
    """
    Saves missing web resource to file.
    
    Downloads the file again, if older than config.refresh_time.
    
    Args:
        url (str): URL to web resource
        path (pathlib.Path): file path (should contain file extension) 
    """

    if path.is_file():
        if (time.time() - path.stat().st_mtime) > config.refresh_time:
            path.unlink()
            print(f"PinPoint: download {url} to {path}", file=sys.stderr)
            urllib.request.urlretrieve(url, filename=path)
    else:
        print(f"PinPoint: download {url} to {path}", file=sys.stderr)
        urllib.request.urlretrieve(url, filename=path)


def city_to_point(city):
    point = nv.GeoPoint(latitude=city['latitude'], longitude=city['longitude'], degrees=True)
    return np.reshape(point.to_nvector().normal, 3)


def add_postal_codes(data):
    """

    Args:
        data (dict): data dictionary

    Returns (dict): modified data dictionary

    """

    post_code_file = config.resources_cache_dir / 'postal_codes.zip'
    post_code_url = 'http://download.geonames.org/export/zip/allCountries.zip'
    download_resource(post_code_url, post_code_file)
    post_code_vectors = dict()
    with ZipFile(str(post_code_file)) as post_code_zip:
        with io.TextIOWrapper(post_code_zip.open('allCountries.txt', 'r'), encoding='utf-8') as post_code_raw:
            for line in post_code_raw:
                row = line.split('\t')
                a2 = row[0].strip()
                post_code = row[1].strip()
                try:
                    latitude = float(row[9].strip())
                    longitude = float(row[10].strip())
                except ValueError:
                    continue
                vector = np.reshape(nv.GeoPoint(latitude=latitude,
                                                longitude=longitude,
                                                degrees=True).to_nvector().normal, 3)
                try:
                    post_code_vectors[a2].append((post_code, vector))
                except KeyError:
                    post_code_vectors[a2] = [(post_code, vector)]
                if a2 in ['JP']:
                    post_code = re.sub("\D+", "", post_code)
                    try:
                        post_code_vectors[a2].append((post_code, vector))
                    except KeyError:
                        post_code_vectors[a2] = [(post_code, vector)]

    # South Korea extra post codes
    # https://en.wikipedia.org/wiki/List_of_postal_codes_in_South_Korea
    kr_path = Path(config.base_dir / 'data/post_code_kr.txt')
    for line in kr_path.read_text(encoding='utf-8').splitlines():
        row = line.split('\t')
        latitude, longitude = row[2].split(', ')
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            continue
        vector = np.reshape(nv.GeoPoint(latitude=latitude, longitude=longitude, degrees=True).to_nvector().normal, 3)
        if ', ' in row[0]:
            post_range = row[0].split(', ')
        else:
            post_range = (row[0], row[0])
        for post_code_int in range(int(post_range[0])*100, int(post_range[1])*100+100):
            try:
                post_code_vectors['KR'].append((str(post_code_int), vector))
            except KeyError:
                post_code_vectors['KR'] = [(str(post_code_int), vector)]

    # Taiwan extra post codes
    # https://en.wikipedia.org/wiki/Postal_codes_in_Taiwan
    tw_path = Path(config.base_dir / 'data/post_code_tw.txt')
    for line in tw_path.read_text(encoding='utf-8').splitlines():
        row = line.split('\t')
        try:
            latitude = float(row[2])
            longitude = float(row[3])
            post_code = int(row[0])
        except (ValueError, IndexError):
            print(line)
            continue
        vector = np.reshape(nv.GeoPoint(latitude=latitude, longitude=longitude, degrees=True).to_nvector().normal, 3)
        for post_code_int in range(post_code*100, post_code*100+100):
            try:
                post_code_vectors['TW'].append((str(post_code_int), vector))
            except KeyError:
                post_code_vectors['TW'] = [(str(post_code_int), vector)]

    # China extra post codes
    # https://en.wikipedia.org/wiki/List_of_postal_codes_in_China
    cn_path = Path(config.base_dir / 'data/post_code_cn.json')
    china_post_code = json.load(cn_path.open('r'))
    for (post_code, name, latitude, longitude) in china_post_code:
        vector = np.reshape(nv.GeoPoint(latitude=latitude, longitude=longitude, degrees=True).to_nvector().normal, 3)
        for post_code_int in range(0, 100):
            try:
                post_code_vectors['CN'].append((f"{post_code}{post_code_int:02}", vector))
            except KeyError:
                post_code_vectors['CN'] = [(f"{post_code}{post_code_int:02}", vector)]

    for a2 in post_code_vectors:
        print(f"working on {a2} with {len(post_code_vectors[a2])} post codes", file=sys.stderr)
        geonameid_list = list(data[a2].keys())
        vector_list = np.array(list(map(city_to_point, data[a2].values())))

        search_tree = spatial.KDTree(vector_list)
        for post_code, vector in post_code_vectors[a2]:
            result = search_tree.query(vector)
            geonameid = geonameid_list[result[1]]
            data[a2][geonameid]['post_code'].append(post_code)

    return data


def add_alternate_names(data, geonameid_key, geonameid_sub=True):
    """
    
    Args:
        data (dict): data dictonary (need keys: name_list=[], short_name_list=[])
        geonameid_key (dict): map geonameid to data key
        geonameid_sub (bool): set to False for countries

    Returns (dict): modified data dictionary

    """

    alternate_name_file = config.resources_cache_dir / 'alternate_names_raw.zip'
    alternate_name_url = 'http://download.geonames.org/export/dump/alternateNames.zip'
    download_resource(alternate_name_url, alternate_name_file)

    with ZipFile(str(alternate_name_file)) as alternate_name_zip:
        with io.TextIOWrapper(alternate_name_zip.open('alternateNames.txt', 'r'),
                              encoding='utf-8') as alternate_name_raw:
            if geonameid_sub:  # if outside of loop for better performance
                for line in alternate_name_raw:
                    row = line.split('\t')
                    if row[1] not in geonameid_key:
                        continue
                    else:
                        if row[2] in config.alternate_name_language:
                            data[geonameid_key[row[1]]][row[1]]['name_list'].append(row[3])
                        elif row[2] in config.alternate_name_language_quick:
                            data[geonameid_key[row[1]]][row[1]]['short_name_list'].append(row[3])
            else:
                for line in alternate_name_raw:
                    row = line.split('\t')
                    if row[1] not in geonameid_key:
                        continue
                    else:
                        if row[2] in config.alternate_name_language:
                            data[geonameid_key[row[1]]]['name_list'].append(row[3])
                        elif row[2] in config.alternate_name_language_quick:
                            data[geonameid_key[row[1]]]['short_name_list'].append(row[3])

    for a2 in data:
        if geonameid_sub:
            for geonameid in data[a2]:
                data[a2][geonameid]['name_list'] = list(set(data[a2][geonameid]['name_list']))
                data[a2][geonameid]['short_name_list'] = list(set(data[a2][geonameid]['short_name_list']))
        else:
            data[a2]['name_list'] = list(set(data[a2]['name_list']))
            data[a2]['short_name_list'] = list(set(data[a2]['short_name_list']))

    return data


def create_lookup():
    """
    Generate lookup tables to optimize location speed.
     
     Read country, city, and region data from the config.resources_dir 
     to generate the following lookup tables:
        country_full, country_alternate
        region_full, region_alternate
        city_quick, city_full, city_alternate
        city_region_quick, city_region_full, city_region_alternate,
        city_post_code, city_region_post_code
    
    The lookup tables are saved as compressed json file in config.resources_dir.
    When loading the lookup tables special care should be taken to ensure to 
    use of collections.OrderedDict() or python > 3.6.
    """

    country_data = load_resource(config.resources_dir / 'country_data.gzip')
    city_data = load_resource(config.resources_dir / f'city_data_{config.city_resolution}.gzip')
    region_data = load_resource(config.resources_dir / f'region_data.gzip')

    lookup = dict()

    # Create lookup for counties
    lookup['country_full'] = OrderedDict()
    lookup['country_alternate'] = OrderedDict()
    for a2, extra_name in config.special_country:
        country_data[a2]['short_name_list'].append(extra_name)

    for a2, country in sorted(country_data.items(), key=lambda x: x[1]['population'], reverse=True):
        for name in country['short_name_list']:
            lookup['country_full'][name.lower()] = a2
        for name in country['name_list']:
            lookup['country_alternate'][name.lower()] = a2

    # Create lookup for cities
    for lookup_parameter in ('city_quick', 'city_full', 'city_alternate', 'city_post_code'):
        lookup[lookup_parameter] = dict()
        for a2 in city_data:
            lookup[lookup_parameter][a2] = OrderedDict()

    for lookup_parameter in ('city_region_quick', 'city_region_full', 'city_region_alternate', 'city_region_post_code'):
        lookup[lookup_parameter] = dict()
        for a2 in city_data:
            lookup[lookup_parameter][a2] = dict()
            if a2 in region_data:
                for region in region_data[a2].values():
                    lookup[lookup_parameter][a2][region['region_code']] = OrderedDict()

    for a2 in city_data:
        if a2 in region_data:
            for geonamid, city in sorted(city_data[a2].items(), key=lambda x: x[1]['population']):
                if geonamid in config.skip_city:
                    continue
                for parameter in ('name', 'asciiname'):
                    if not city[parameter]:
                        continue
                    if city['population'] > 50000:
                        lookup['city_quick'][a2][city[parameter].lower()] = geonamid
                        if city['admin1_code'] in lookup['city_region_quick'][a2]:
                            lookup['city_region_quick'][a2][city['admin1_code']][city[parameter].lower()] = geonamid
                    else:
                        lookup['city_full'][a2][city[parameter].lower()] = geonamid
                        if city['admin1_code'] in lookup['city_region_quick'][a2]:
                            lookup['city_region_full'][a2][city['admin1_code']][city[parameter].lower()] = geonamid
                for post_code in city['post_code']:
                    lookup['city_post_code'][a2][post_code] = geonamid
                    if city['admin1_code'] in lookup['city_region_quick'][a2]:
                        lookup['city_region_post_code'][a2][city['admin1_code']][post_code] = geonamid

                for name in city['name_list']:
                    lookup['city_alternate'][a2][name.lower()] = geonamid
                    if city['admin1_code'] in lookup['city_region_quick'][a2]:
                        lookup['city_region_alternate'][a2][city['admin1_code']][name.lower()] = geonamid
        else:
            for geonamid, city in sorted(city_data[a2].items(), key=lambda x: x[1]['population']):
                if geonamid in config.skip_city:
                    continue
                for parameter in ('name', 'asciiname'):
                    if not city[parameter]:
                        continue
                    if city['population'] > 50000:
                        lookup['city_quick'][a2][city[parameter].lower()] = geonamid
                    else:
                        lookup['city_full'][a2][city[parameter].lower()] = geonamid
                for post_code in city['post_code']:
                    lookup['city_post_code'][a2][post_code] = geonamid
                for name in city['name_list']:
                    lookup['city_alternate'][a2][name.lower()] = geonamid

    for a2, name, geonamid in config.special_city:
        lookup['city_quick'][a2][name] = geonamid

    # Create lookup for regions
    for lookup_parameter in ('region_full', 'region_alternate'):
        lookup[lookup_parameter] = dict()
        for a2 in region_data:
            lookup[lookup_parameter][a2] = OrderedDict()

    for a2 in region_data:
        for geonamid, region in region_data[a2].items():
            for name in region['short_name_list']:
                lookup['region_full'][a2][name.lower()] = geonamid
            for name in region['name_list']:
                lookup['region_alternate'][a2][name.lower()] = geonamid

    # largest cities first
    for key in ['city_quick', 'city_full', 'city_post_code', 'city_alternate']:
        for a2 in lookup[key]:
            lookup[key][a2] = OrderedDict(reversed(lookup[key][a2].items()))
    for key in ['city_region_quick', 'city_region_full', 'city_region_post_code', 'city_region_alternate']:
        for a2 in lookup[key]:
            for region in lookup[key][a2]:
                lookup[key][a2][region] = OrderedDict(reversed(lookup[key][a2][region].items()))
    save_resource(lookup, config.resources_dir / 'lookup.gzip')


def create_city_database():
    """
    Build a database of cities based on the geonames city database.

    Downloads the database file, processes it and saves it as compressed json file in config.resources_dir.
    http://www.geonames.org
    http://download.geonames.org/export/dump/
    """

    city_raw_file = config.resources_cache_dir / f'city_raw_{config.city_resolution}.zip'
    city_raw_url = f'http://download.geonames.org/export/dump/cities{config.city_resolution}.zip'
    download_resource(city_raw_url, city_raw_file)

    city_data = dict()
    city_a2_lookup = dict()
    with ZipFile(str(city_raw_file)) as city_raw_zip:
        with io.TextIOWrapper(city_raw_zip.open(f'cities{config.city_resolution}.txt', 'r'),
                              encoding='utf-8') as city_raw:
            for i, row in enumerate(city_raw):
                row = row.split('\t')
                city_entry = dict()
                try:
                    city_entry['latitude'] = float(row[config.geo_name_city_header.index('latitude')])
                    city_entry['longitude'] = float(row[config.geo_name_city_header.index('longitude')])
                except ValueError:
                    continue

                for parameter in ('geonameid', 'name', 'asciiname', 'timezone', 'a2', 'admin1_code'):
                    value = row[config.geo_name_city_header.index(parameter)].strip()
                    if value:
                        city_entry[parameter] = value
                    else:
                        city_entry[parameter] = None

                for parameter in ('elevation', 'population', 'dem'):
                    try:
                        city_entry[parameter] = int(row[config.geo_name_city_header.index(parameter)])
                    except ValueError:
                        city_entry[parameter] = None

                city_entry['post_code'] = []

                name_list = row[config.geo_name_city_header.index('alternatenames')].split(',')
                name_list.append(row[config.geo_name_city_header.index('name')])
                name_list.append(row[config.geo_name_city_header.index('asciiname')])
                name_list = set(name_list)
                name_list.discard('')
                city_entry['name_list'] = list(name_list)

                city_a2_lookup[city_entry['geonameid']] = city_entry['a2']
                try:
                    city_data[city_entry['a2']][city_entry['geonameid']] = city_entry
                except KeyError:
                    city_data[city_entry['a2']] = {city_entry['geonameid']: city_entry}

                if city_entry['a2'] in config.country_include:
                        try:
                            city_data[config.country_include[city_entry['a2']]][city_entry['geonameid']] = city_entry
                        except KeyError:
                            city_data[config.country_include[city_entry['a2']]] = {city_entry['geonameid']: city_entry}

    for a2 in config.extra_cities:
        for geonameid in config.extra_cities[a2]:
            city_data[a2][geonameid] = config.extra_cities[a2][geonameid]
    city_data = add_postal_codes(city_data)

    save_resource(city_data, config.resources_dir / f'city_data_{config.city_resolution}.gzip')


def create_region_database():
    """
    Build a database of high-level regions based on the geonames city database.
    
    Downloads the database file, processes it and saves it as compressed json file in config.resources_dir.
    At the moment limit to USA.
    http://www.geonames.org
    http://download.geonames.org/export/dump/admin1CodesASCII.txt
    """

    region_raw_url = 'http://download.geonames.org/export/dump/admin1CodesASCII.txt'
    region_raw_file = config.resources_cache_dir / 'region_raw.txt'
    download_resource(region_raw_url, region_raw_file)

    region_data = dict()
    country_geonameid_a2 = dict()
    with open(region_raw_file, 'r', encoding='utf-8') as region_raw:
        for row in region_raw:
            if True:
                entry = dict(name_list=[], short_name_list=[])
                row = row.strip().split('\t')
                a2, region_code = row[0].split('.')
                entry['a2'] = a2
                entry['region_code'] = region_code.strip()
                entry['geonameid'] = row[3]
                entry['name'] = row[1].strip()
                if not region_code.isdigit():
                    entry['short_name_list'].append(region_code)

                try:
                    region_data[a2][entry['geonameid']] = entry
                except KeyError:
                    region_data[a2] = {entry['geonameid']: entry}
                country_geonameid_a2[entry['geonameid']] = a2

    region_data = add_alternate_names(region_data, country_geonameid_a2)
    save_resource(region_data, config.resources_dir / 'region_data.gzip')


def create_country_database():
    """
    Build a database of all countries based on the geonames database.
    
    Downloads the database file, processes it and saves it as compressed json file in the resource folder.
    Add alternate names for common languages defined in config.alternate_name_language and
    config.alternate_name_language_quick.

    http://www.geonames.org
    http://download.geonames.org/export/dump/countryInfo.txt
    http://download.geonames.org/export/dump/alternateNames.zip
    """

    country_raw_file = config.resources_cache_dir / 'country_raw.txt'
    country_raw_url = 'http://download.geonames.org/export/dump/countryInfo.txt'
    download_resource(country_raw_url, country_raw_file)

    country_data = dict()
    country_geonameid_a2 = dict()
    with open(country_raw_file, 'r') as country_raw:
        reader = csv.DictReader((row for row in country_raw if not row.startswith('#')), dialect='excel-tab',
                                fieldnames=config.geo_names_country_header)

        for row in reader:
            country_entry = dict(name_list=[], short_name_list=[])

            for parameter in ('a2', 'a3', 'n3', 'capital', 'continent', 'geonameid', 'name'):
                value = row[parameter].strip()
                if value:
                    country_entry[parameter] = value
                else:
                    country_entry[parameter] = None

            for parameter in ('area', 'population'):
                try:
                    country_entry[parameter] = int(row[parameter])
                except ValueError:
                    country_entry[parameter] = None

            country_data[country_entry['a2']] = country_entry
            country_geonameid_a2[country_entry['geonameid']] = country_entry['a2']

    country_data = add_alternate_names(country_data, country_geonameid_a2, geonameid_sub=False)
    save_resource(country_data, config.resources_dir / 'country_data.gzip')


def create_resources(refresh=False):
    """
    Checks if resources are available and create them if necessary.

    The following resources are included:
        city_data
        country_data
        region_data
        lookup
    """

    config.resources_dir.mkdir(exist_ok=True)
    config.resources_cache_dir.mkdir(exist_ok=True)

    for resource_file, create in ((f'city_data_{config.city_resolution}.gzip', create_city_database),
                                  ('country_data.gzip', create_country_database),
                                  ('region_data.gzip', create_region_database),
                                  ('lookup.gzip', create_lookup)):
        resource_file = config.resources_dir / resource_file
        if not resource_file.is_file() or refresh:
            print(f"PinPoint: recreate resource file {resource_file}", file=sys.stderr)
            create()

    if not config.keep_downloaded_resources:
        for temp_files in config.resources_cache_dir.iterdir():
            try:
                temp_files.unlink()
            except:
                print(f"PinPoint: could not remove {temp_files}", file=sys.stderr)


if __name__ == '__main__':
    create_resources()
