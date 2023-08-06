# PinPoint

[![PyPI](https://img.shields.io/pypi/v/pinpoint.svg)](https://pypi.org/project/PinPoint/)
[![PyPI - License](https://img.shields.io/pypi/l/pinpoint.svg)](https://bitbucket.org/nathan-diodan/pinpoint/src/master/LICENSE.txt)
[![Bitbucket issues](https://img.shields.io/bitbucket/issues/nathan-diodan/pinpoint.svg)](https://bitbucket.org/nathan-diodan/pinpoint/issues?status=new&status=open)
[![PyPI - Status](https://img.shields.io/pypi/status/pinpoint.svg)](https://pypi.org/project/PinPoint/)


PinPoint is a fast geo toolkit for academic affiliation strings.
It provides the following base functions:

* find a location (information about mapped city and country)
* calculate the apparent location and cooperation distance for a list of weighted affiliation strings

## Install
Install and update using pip

```
pip install pinpoint
```

## Usage

```python
from pinpoint import Locator
loc = Locator()
```

The first time ```Locator``` is initialized the databases needs to be created.
For this four files are downloaded from [GeoNames](http://www.geonames.org) [dump](http://download.geonames.org/export/dump/) (~ 150MB) and optimized:

* cities1000.zip
* admin1CodesASCII.txt
* countryInfo.txt
* alternateNames.zip

It is possible to rebuild the database at a later date:
```python
from pinpoint import Locator
loc = Locator(refresh=True)
```
The data will not be downloaded again from [GeoNames](http://www.geonames.org) if the cached files are younger than a week.
This is to avoid unnecessary load on the servers.
The databases and cached files are stored in the appropriate folders depending on your operating system.
If absolutely necessary you can empty them by hand.

```python
from pinpoint import Locator
print(Locator.resources_dir)
print(Locator.resources_cache_dir)
```

### Find a location

```python
test_string = "Department of Chemical and Biomolecular Engineering, Rice University, Houston, TX, United States"
country, region, city = loc.find(test_string)
```

This returns either a `dict()` or `None` for each the country, region, and city.
The following information is returned based on the data from [GeoNames](http://www.geonames.org):

* county
  * `'a2'` ISO 3166-1 alpha-2 counry code
  * `'a3'` ISO 3166-1 alpha-3 counry code
  * `'n3'` ISO 3166-1 numeric counry code
  * `'name'`
  * `'short_name_list'` short name variants
  * `'name_list'` name in different languages
  * `'capital'`
  * `'continent'`
  * `'area'` in square kilometer
  * `''population'`
  * `'geonameid'` unique id given by [GeoNames](http://www.geonames.org)
* region (just used for USA and Canada at the moment)
  * `'name'`
  * `'short_name_list'` short name variants
  * `'name_list'` name in different languages
  * `'region_code'`
  * `'a2'` ISO 3166-1 alpha-2 counry code
  * `'geonameid'` unique id given by [GeoNames](http://www.geonames.org)
* city
  * `'name'`
  * `'asciiname'`
  * `'name_list'` name in different languages
  * `'latitude'`
  * `'longitude'`
  * `'a2'` ISO 3166-1 alpha-2 counry code
  * `'admin1_code'`
  * `'elevation'` and `'dem'` are linked to the elevation in meter
  * `'timezone'`
  * `'geonameid'` unique id given by [GeoNames](http://www.geonames.org)

### Calculate the apparent location and cooperation distance

Based on a weighted list of affiliations an apparent location for a scientific document can be calculated.

```python
from pinpoint import Locator
loc = Locator()

weighted_affilations = (
    (2, "Dresden Center for Computational Material Science, Technische Universität Dresden, Dresden, Germany"),
    (1, "Department of Chemical and Biomolecular Engineering, Rice University, Houston, TX, United States"),
    (0.5, "Nanoscience and Nanotechnology Center, Institute of Scientific and Industrial Research (ISIR), Osaka University, 8-1 Mihogaoka, Ibaraki, Osaka, Japan"),
    (0.5, "Centro/Departamento de Física da Universidade do Minho, Campus de Gualtar, 4710-057 Braga, Portugal"),
    )

cooperation_distance, apparent_location = loc.calculate_str(weighted_affilations)
```

The cooperation distance is returned in kilometers.
If the coordinates are already known the calculation can be done directly, without the need to initialize the resources.

```python
Locator.calculate_coordinates(weighted_coordinates)
```

## Examples

Different examples can be found in the extra folder of the [source distribution](https://bitbucket.org/nathan-diodan/pinpoint/src/master/extras/README.md).

