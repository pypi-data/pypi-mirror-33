from pathlib import Path

import appdirs

app_name = 'PinPoint'
app_author = 'science.eckert'
base_dir = Path(__file__).absolute().parent
resources_dir = Path(appdirs.user_data_dir(app_name, app_author))
resources_cache_dir = Path(appdirs.user_cache_dir(app_name, app_author))
keep_downloaded_resources = True
refresh_time = 60*60*24*7*4  # one week in seconds
city_resolution = 1000

"""
Skip problematic cities.

7260219: University, Florida, US
"""
skip_city = ['7260219']

"""
Cities with special mapping.

US princeton: Princeton without state information is mapped to the home town of Princeton University (5102922)
FI aalto: Map to Aalto University in Helsinki
"""
special_city = [('US', 'princeton', '5102922'),
                ('FI', 'aalto', '658225')]

"""
Cities that are not included (because they are too small for example) but are home to an important research facility.
"""
extra_cities = {
    'SA': {
        '409682': {
            'latitude': 22.28272,
            'longitude': 39.11245,
            'geonameid': '409682',
            'name': 'Thuwal',
            'asciiname': 'Thuwal',
            'timezone': 'Asia/Riyadh',
            'a2': 'SA',
            'admin1_code': '14',
            'elevation': 3,
            'population': 0,
            'dem': 3,
            'post_code': [],
            'name_list': ['Tūwal', ]},
    },
    'JP': {
        '1852831': {'latitude': 35.00268,
                    'longitude': 134.35896,
                    'geonameid': '1852831',
                    'name': 'Sayō',
                    'asciiname': 'Sayo',
                    'timezone': 'Asia/Tokyo',
                    'a2': 'JP',
                    'admin1_code': '13',
                    'elevation': None,
                    'population': 0,
                    'dem': None,
                    'post_code': [],
                    'name_list': ['佐用']}
    }
}

"""
Special string to match Counties

Scotland, England, Wales, Northern Ireland mapped to the United Kingdom
"""
special_country = [('GB', 'Scotland'),
                   ('GB', 'England'),
                   ('GB', 'Wales'),
                   ('GB', 'Northern Ireland'),
                   ('AE', 'Arab Emirates'),
                   ('BY', 'Byelarus')]

"""
Countries that are often referred but are not autonomous.

Hong Kong, Macao: listed as China
"""
country_include = {'HK': 'CN',
                   'MO': 'CN'}

alternate_name_language_quick = {'en', 'abbr'}  # abbr abbreviation
alternate_name_language = {'en', 'de', 'es', 'fr', 'pt', 'it',
                           'zh', 'hi', 'bn', 'ru', 'ja'}.difference(alternate_name_language_quick)

geo_name_city_header = ('geonameid',
                        'name',
                        'asciiname',
                        'alternatenames',
                        'latitude',
                        'longitude',
                        'feature_class',
                        'feature_code',
                        'a2',
                        'cc2',
                        'admin1_code',
                        'admin2_code',
                        'admin3_code',
                        'admin4_code',
                        'population',
                        'elevation',
                        'dem',
                        'timezone',
                        'modification_date')

geo_names_country_header = ('a2',
                            'a3',
                            'n3',
                            'fips',
                            'name',
                            'capital',
                            'area',
                            'population',
                            'continent',
                            'tld',
                            'currency_code',
                            'currency_name',
                            'phone',
                            'postal_code_format',
                            'postal_code_regex',
                            'languages',
                            'geonameid',
                            'neighbours',
                            'equivalent_fips_code')
