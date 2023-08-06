import os
import traceback

import googlemaps
from properly_util_python.helper_utils import isfloat, COLUMN_NAME_MAPPING, string_to_float, date_string_to_iso_string

import pygeohash as geohash

def clean_data_general(data: dict):
    data = clean_dict_keys(data)
    for k, v in data.items():

        if isinstance(data[k], str):
            data[k] = string_to_float(data[k])

    return data


def clean_data_very_clean(data: dict, *args, **kwargs):
    print('clean_data_very_clean')
    if not kwargs.get('skip_keys_clean'):
        data = clean_dict_keys(data)

    remove_keys = []
    for k, v in data.items():

        if k in ['daySold', ]:
            data[k] = date_string_to_iso_string(data[k])
        if isinstance(data[k], str):
            data[k] = string_to_float(data[k])

        # remove numerical columns
        # todo what do the numerical columns represent
        if isfloat(k):
            remove_keys.append(k)

    for k in remove_keys:
        print('removing key', k)
        del data[k]

    data = categorical_to_one_hot(data)
    data = add_google_metadata(data)

    return data


def split_dates(data: dict):
    # @sandra
    """
    take a data
    :param data: ={'date':'2017-09-28'}
    :return: data: ={'date':'2017-09-28','year':2017,'month':09,'day':28}
    """
    pass


def add_google_metadata(house):
    # todo remove and change google maps key

    try:
        gmaps = googlemaps.Client(key=os.environ.get('GOOGLE_MAPS_KEY', ))

        geocode_result = gmaps.geocode(house['address'])

        if len(geocode_result) < 1:
            house['googlePlaceId'] = 'DL'
            return house

        geocode_result = geocode_result[0]

        house['addressShort'] = house['address']
        house['address'] = geocode_result['formatted_address']

        # use precise lat long if the current ones are not precise e.g. long: -114 vs -114.41231
        if not house.get('latitude') or not house.get('longitude'):
            house['latitude'] = geocode_result['geometry']['location']['lat']
            house['longitude'] = geocode_result['geometry']['location']['lng']

        elif '.' not in str(house['latitude']) or '.' not in str(house['longitude']):
            house['latitudeGoogle'] = geocode_result['geometry']['location']['lat']
            house['longitudeGoogle'] = geocode_result['geometry']['location']['lng']
            house['latitudeOld'] = house['latitude']
            house['longitudeOld'] = house['longitude']

            house['latitude'] = house['latitudeGoogle']
            house['longitude'] = house['longitudeGoogle']

        house = geohash_lat_long(house)

        house['googlePlaceId'] = geocode_result['place_id']

        streetview_image = 'https://maps.googleapis.com/maps/api/streetview?size=900x500&pitch=-0.76' \
                           '&location={0},{1}' \
                           '&key=AIzaSyD4NQrin9CG8KYt8gAOYRbojTcDwph3klw'.format(house['latitude'], house['longitude'])
        house['imageUrls'] = [streetview_image]

    except Exception as e:
        print('Exception e:', e)
        print('traceback:', traceback.format_exc())
        house['googleMetadataError'] = str(e)

    return house


def geohash_lat_long(house):
    try:
        geohash_result = geohash.encode(house['latitude'], house['longitude'])

        geohash_key = 'geoHash' + str(len(geohash_result))

        house[geohash_key] = geohash_result

        geohash_key = 'geoHash' + str(len(geohash_result[:5]))

        house[geohash_key] = geohash_result[:5]

    except Exception as e:
        print('geohash_lat_long Exception:', e)
        house['geoHashError'] = str(e)

    return house


def categorical_to_one_hot(data):
    data['isFullyFinishedBasement'] = None
    data['isPartlyFinishedBasement'] = None
    data['isSuiteBasement'] = None
    try:
        if 'Partly Finished' in data.get('basementDevelopment', ''):
            data['isPartlyFinishedBasement'] = 1
            data['isFullyFinishedBasement'] = 0
            data['isSuiteBasement'] = 1

        elif 'Fully Finished' in data.get('basementDevelopment', ''):
            data['isPartlyFinishedBasement'] = 0
            data['isFullyFinishedBasement'] = 1
            data['isSuiteBasement'] = 0

        elif 'Suite' in data.get('basementDevelopment', ''):
            data['isPartlyFinishedBasement'] = 0
            data['isFullyFinishedBasement'] = 0
            data['isSuiteBasement'] = 1
    except Exception as e:
        print('categorical_to_one_hot Exceotion', e)
        print('traceback', traceback.format_exc())
        data['categoricalToOneHotError'] = str(e)
    return data


def clean_dict_keys(data: dict):
    clean_dict = {clean_column_name(k): data[k] for k in data.keys()}

    return clean_dict


def clean_column_name(name: str):
    if name in COLUMN_NAME_MAPPING.keys():
        return COLUMN_NAME_MAPPING[name]

    if isfloat(name):
        return name

    if is_clean_name(name):
        name = name[0].lower() + name[1:]
        return name

    output = ''.join(x for x in name.title() if x.isalnum())

    output = output[0].lower() + output[1:]
    return output


def is_clean_name(name: str):
    return ' ' not in name and all(x.isalnum() for x in name)
