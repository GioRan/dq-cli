import logging
import os
import traceback

import click
import pandas
from geopip import GeoPIP

from Commands.AddressCleansing.address_cleasning import AddressCleansing
from Commands.AddressCleansing.autofill import Autofill
from Commands.AddressCleansing.free_text_matching import FreeTextMatching
from Commands.AddressCleansing.geojson_lookup import GeoJSONLookup
from Commands.AddressCleansing.google_reverse_geocoding import GoogleReverseGeocoding
from Services.psgc_new import PSGC_NEW
from Services.psgc_old import PSGC_OLD
from Utilities.Utils import Utils as utils

project_folder = os.path.dirname(os.path.realpath(__file__))
cli_name = os.path.dirname(os.path.realpath(__file__)).split(os.sep)[-1]


@click.command(name=cli_name)
@click.option('--input', '-i',
              required=True,
              type=str)
@click.option('--bypass', '-b',
              is_flag=True,
              default=False,
              type=bool)
def cli(input: str, bypass: bool = False):
    address_cleansing = AddressCleansing(input, bypass)

    df = address_cleansing.df
    psgc_new = PSGC_NEW().df
    psgc_old = PSGC_OLD().df

    logging.info(f'Loading GeoJSON file, This will take time...')
    geopip_i = GeoPIP(geojson_dict=utils.load_json('./StaticFiles/PH_PSGC_WITH_AREA_V13.json'))

    autofill = Autofill()
    free_text_matching = FreeTextMatching(psgc_new)
    google_reverse_geocoding = GoogleReverseGeocoding()
    geojson_lookup = GeoJSONLookup(psgc_old)

    try:
        print(f'Running {autofill.__class__.__name__}...')
        df = utils.parallelize(autofill.apply_autofill, df)

        print(f'Running {free_text_matching.__class__.__name__}...')
        df['concat_address'] = df[['bldg_name', 'street_name', 'area_name', 'town', 'province']].agg(' '.join,
                                                                                                     axis=1)
        df = utils.parallelize(free_text_matching.apply_matching, df)

        print(f'Running {google_reverse_geocoding.__class__.__name__}...')
        df = utils.parallelize(google_reverse_geocoding.apply_reverse_geocoding, df)
        df = pandas.concat(df.to_list(), ignore_index=True)
        df = google_reverse_geocoding.prioritization(df)

        print(f'Running {geojson_lookup.__class__.__name__}...')
        df = utils.parallelize(geojson_lookup.apply_geojson_lookup, df, geopip=geopip_i)
        df = pandas.concat(df.to_list(), ignore_index=True)

        df = address_cleansing.map_columns(df, address_cleansing.address_type, address_cleansing.cfu, reverse=True)

        utils.save_to_csv(f'{address_cleansing.output_path}/{address_cleansing.filename}_', df)

    except Exception:
        print(traceback.format_exc())
        utils.save_to_csv(f'{address_cleansing.output_path}/{address_cleansing.filename}_', df)
