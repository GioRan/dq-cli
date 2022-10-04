import logging

import pandas
import warnings
import httpx
import ast

import numpy

from Utilities.config import props

class GoogleReverseGeocoding:

    def __init__(self):
        self.api_endpoint: str = 'https://maps.googleapis.com/maps/api/geocode'
        self.api_output_format: str = 'json'
        self.api_request_filter: str = 'country:PH'
        self.api_key = props['gmaps']['api_key']

    def apply_reverse_geocoding(self, row: pandas.Series) -> pandas.DataFrame:
        if row['Cleansing Status'] == 'Cleansed' or row['concat_address'].strip() == '': return pandas.DataFrame([dict(row)])

        return pandas.DataFrame(self.format_gmaps_response(row, self.gmaps_request(row['concat_address'])))

    def gmaps_request(self, address: str) -> dict:
        params = {
            'address': address,
            'components': self.api_request_filter,
            'key': self.api_key
        }

        headers = {
            'Accept': 'application/json'
        }

        warnings.filterwarnings("ignore")

        try:
            return httpx.get(f'{self.api_endpoint}/{self.api_output_format}', headers=headers, params=params,
                             verify=False, timeout=None).json()
        except Exception as e:
            logging.error(e)
            return self.gmaps_request(address)

    def format_gmaps_response(self, row: pandas.Series, response: dict) -> list:

        if len(response['results']) == 0:
            return [dict(row, **{'with_maps_result': False})]

        return [dict(r, **row, **{'with_maps_result': True}) for r in response['results']]

    def prioritization(self, df: pandas.DataFrame) -> pandas.DataFrame:
        df['longitude'] = df['geometry'].apply(
                            lambda x: x['location']['lng']
                            if isinstance(x, dict)
                            else ast.literal_eval(x)['location']['lng']
                            if isinstance(x, str) and x != numpy.nan and x != ''
                            else numpy.nan)

        df['latitude'] = df['geometry'].apply(
                            lambda x: x['location']['lat']
                            if isinstance(x, dict)
                            else ast.literal_eval(x)['location']['lat']
                            if isinstance(x, str) and x != numpy.nan and x != ''
                            else numpy.nan)

        df['location_type'] = df['geometry'].apply(
                                lambda x: x['location_type']
                                if isinstance(x, dict)
                                else ast.literal_eval(x)['location_type']
                                if isinstance(x, str) and x != numpy.nan and x != ''
                                else numpy.nan)

        df['location_priority'] = df['location_type'].apply(
                                    lambda x: 1
                                    if x == 'ROOFTOP'
                                    else 2
                                    if x == 'RANGE_INTERPOLATED'
                                    else 3
                                    if x == 'GEOMETRIC_CENTER'
                                    else 4
                                    if x == 'APPROXIMATE'
                                    else 5)

        df.sort_values(by=['location_priority'], inplace=True)
        df.drop_duplicates(subset=['addr_id', 'concat_address'], keep='first', inplace=True)
        df.sort_values(by=['addr_id'], inplace=True)

        df.drop(['location_priority'], axis=1, inplace=True)

        return df