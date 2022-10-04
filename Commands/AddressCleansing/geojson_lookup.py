import ast
import logging
import statistics
from collections import ChainMap
import re

import numpy
import pandas
from rapidfuzz import fuzz
from geopip import GeoPIP


class GeoJSONLookup:

    def __init__(self, psgc: pandas.DataFrame):
        self.psgc = psgc
        self.api = 'http://localhost:'
        self.port = 4000
        self.endpoint = '/getPSGCByLongLat'

    def apply_geojson_lookup(self, row: pandas.Series, **kwargs) -> pandas.DataFrame:
        geopip: GeoPIP = kwargs.get('geopip')

        try:
            if row['Cleansing Status'] == 'Cleansed': return pandas.DataFrame([dict(row)])

            raw_address: str = row['concat_address']
            formatted_address: str = row['formatted_address']
            geometry: dict = row['geometry']

            if pandas.isna(geometry) is False:
                # address_components: list = ast.literal_eval(row['address_components'])
                geojson: dict = geopip.search(geometry['location']['lng'], geometry['location']['lat'])

                if geojson is not None:
                    location_type: str = geometry['location_type']
                    formatted_geojson: dict = self.lookup_postal_by_ids(self.format_geojson(geojson))
                    geojson_score: dict = self.attach_geojson_score_percentage(self.init_address_x_geogjson(raw_address, geojson))

                    return \
                        pandas.DataFrame([{
                            **self.attach_geojson_fields(row, formatted_geojson, geojson_score),
                            **{'location_type': location_type},
                            **formatted_geojson,
                            # **self.extract_x_field_from_gmaps(address_components),
                            **self.init_address_score(raw_address, formatted_address),
                            # **self.init_address_x_gmaps(raw_address, address_components),
                            **geojson_score,
                        }])
                else:
                    return pandas.DataFrame([row])
            else:
                return pandas.DataFrame([row])
        except Exception as e:
            logging.error(e)
            logging.error(**row)

    def attach_geojson_fields(self, row: pandas.Series, geojson: dict, geojson_score: dict) -> pandas.Series:
        if 'geojson_PROVINCE' not in geojson or 'geojson_CITY_TOWN' not in geojson or 'geojson_BARANGAY' not in geojson or 'geojson_ZIP' not in geojson or \
                geojson_score['Cleansing Status'] == 'Fallouts':
            return row

        row['postal_cd_NEW'] = geojson['geojson_ZIP']
        row['area_name_NEW'] = geojson['geojson_BARANGAY']
        row['town_NEW'] = geojson['geojson_CITY_TOWN']
        row['province_NEW'] = geojson['geojson_PROVINCE']

        return row

    def init_address_score(self, raw_address: str, formatted_address: str) -> dict:
        score_per_delimited = [fuzz.partial_ratio(ra.upper(), formatted_address) for ra in raw_address.split(' ')]

        return \
            {
                'score_address (whole base level)': fuzz.WRatio(raw_address, formatted_address),
                'score_address (delimited level)': "{:.2f}".format(statistics.mean(score_per_delimited))
            }

    def init_address_x_gmaps(self, raw_address: str, address_components: list) -> dict:
        score_list: list = [{f'{self.format_gmaps_component_type(nt)}_short_score': fuzz.partial_ratio(
            ac['short_name'].upper(), raw_address),
                             f'{self.format_gmaps_component_type(nt)}_long_score': fuzz.partial_ratio(
                                 ac['long_name'].upper(), raw_address)} for ac in address_components for nt in
                            ['postal_code', 'route', 'locality', 'administrative_area_level_2',
                             'administrative_area_level_3', 'administrative_area_level_5', 'neighborhood'] if
                            nt in ac['types']]

        return dict(ChainMap(*score_list))

    def init_address_x_geogjson(self, raw_address: str, geojson: dict) -> dict:
        score_list: list = [{f"geojson_score[{k}]": fuzz.partial_ratio(self.format_geojson_x_fields(k, v),
                                                                       self.replace_word(raw_address))} for k, v in
                            geojson.items() if k in ['BARANGAY', 'CITY_TOWN', 'PROVINCE']]

        return dict(ChainMap(*score_list))

    def extract_x_field_from_gmaps(self, address_components) -> dict:
        res_list = [{f'{self.format_gmaps_component_type(nt)}_short': ac['short_name'],
                     f'{self.format_gmaps_component_type(nt)}_long': ac['long_name']} for ac in address_components
                    for nt in ['postal_code', 'route', 'locality', 'administrative_area_level_2',
                               'administrative_area_level_3', 'administrative_area_level_5', 'neighborhood'] if
                    nt in ac['types']]
        return dict(ChainMap(*res_list))

    def format_geojson_x_fields(self, prop: str, value: str):
        if prop == 'BARANGAY':
            return re.sub(r'\s\(.*\)', '', value.upper()).replace(" POB.", " ").replace("BARANGAY ", "")
        if prop == 'CITY_TOWN':
            return re.sub(r'\s\(.*\)', '', value.upper().replace("CITY OF ", "").replace(" CITY", ""))
        if prop == 'PROVINCE':
            return re.sub(r'\s\(.*\)', '',
                          value.upper().replace("NCR, CITY OF MANILA, FIRST DISTRICT (NOT A PROVINCE)",
                                                "MANILA FIRST DISTRICT").replace("NCR, ", "").replace(
                              " (NOT A PROVINCE)", ""))

    def format_gmaps_component_type(self, type: str) -> str:
        _t = ''

        if type in ['postal_code']: _t = 'gmaps_postal_code'
        if type in ['route']: _t = 'gmaps_street'
        if type in ['administrative_area_level_2']: _t = 'gmaps_province'
        if type in ['administrative_area_level_3', 'locality']: _t = 'gmaps_town'
        if type in ['administrative_area_level_5', 'neighborhood']: _t = 'gmaps_area'

        return _t

    def format_geojson(self, geojson: dict):
        res_list = [{f'geojson_{k}': v} for k, v in geojson.items()]
        return dict(ChainMap(*res_list))

    def lookup_postal_by_ids(self, geojson: dict) -> dict:
        if 'geojson_PROVINCE_C' not in geojson or 'geojson_CITY_CODE' not in geojson or 'geojson_BRGY_CODE' not in geojson:
            return {**geojson, **{'geojson_ZIP': ''}}

        concat_ids: str = f"{geojson['geojson_PROVINCE_C'].replace('PH', '').lstrip('0')}_{geojson['geojson_CITY_CODE'].replace('PH', '').lstrip('0')}_{geojson['geojson_BRGY_CODE'].replace('PH', '').lstrip('0')}"
        postal_lookup_match: pandas.DataFrame = self.psgc[self.psgc['x_zip_code_lookup_base'] == concat_ids]
        postal: str = ''

        if len(postal_lookup_match) == 1:
            postal = list(postal_lookup_match['x_zip_code'])[0]

        return {**geojson, **{'geojson_ZIP': postal}}

    def attach_geojson_score_percentage(self, geojson_score: dict) -> dict:
        script_tagging: str = 'Google API'

        if 'geojson_score[PROVINCE]' not in geojson_score or 'geojson_score[CITY_TOWN]' not in geojson_score or 'geojson_score[BARANGAY]' not in geojson_score:
            return {**geojson_score, **{'geojson_all_score': '0 %', 'Script Tagging': script_tagging,
                                        'Cleansing Status': 'Fallouts'}}

        province_score, city_score, barangay_score = geojson_score['geojson_score[PROVINCE]'], geojson_score[
            'geojson_score[CITY_TOWN]'], geojson_score['geojson_score[BARANGAY]']
        province_score, city_score, barangay_score = float(province_score), float(city_score), float(barangay_score)

        all_score: float = (province_score + city_score + barangay_score) / 3

        if all_score >= 71:
            cleansing_status: str = 'Cleansed'
        else:
            cleansing_status: str = 'Fallouts'

        return {**geojson_score, **{'geojson_all_score': f'{all_score} %', 'Script Tagging': script_tagging,
                                    'Cleansing Status': cleansing_status}}

    def replace_word(self, text):
        reps = {
            r'\bGEN.\b': 'GENERAL ',
            r'\bGEN\b': 'GENERAL ',
            r'\bBGY.\b': ' ',
            r'\bBGY\b': ' ',
            r'\bBRGY.\b': ' ',
            r'\bBRGY\b': ' ',
            r'\bVILLAGE\b': ' ',
            r'\b(POB.)\b': 'POBLACION ',
            r'\bPOB.\b': 'POBLACION ',
            r'\bSTA.\b': 'SANTA ',
            r'\bSTA\b': 'SANTA ',
            r'\bSTO.\b': 'SANTO ',
            r'\bSTO\b': 'SANTO ',
            r'\bMANILA\b': 'MANILA FIRST DISTRICT SECOND DISTRICT THIRD DISTRICT FOURTH DISTRICT ',
            r'\bNCR\b': 'NCR FIRST DISTRICT SECOND DISTRICT THIRD DISTRICT FOURTH DISTRICT ',
            r'\bBAGONG LIPUNAN NG CO\b': 'BAGONG LIPUNAN NG CRAME ',
        }

        for i, j in reps.items():
            text = re.sub(i, j, text.replace('.', ' '))
            text = re.sub(r'\s+', ' ', text)

        return text.strip()

