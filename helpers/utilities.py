import pandas
import numpy
import string
import os

def read_csv(input_dir, required_columns=None, nrows=None, encoding='utf-8', converters=None, capitalize=False, columns_to_remove=[], cast_to_string=False) -> pandas.DataFrame:
    print(f'source df: {input_dir}')

    csv = pandas.read_csv(input_dir, header=0, index_col=False, usecols=required_columns, nrows=nrows, encoding=encoding, low_memory=False, converters=converters) \
        .replace(numpy.nan, '', regex=True).replace('\t', '', regex=True) \
        .apply(lambda x: x.astype(str).str.upper() if capitalize else x) \
        .apply(lambda x: x.astype(str) if cast_to_string else x) \
        .apply(lambda x: x.str.strip() if cast_to_string or capitalize else x)

    csv = csv.drop(columns_to_remove, axis=1)

    print(f'df length: {len(csv)}')

    return csv

def convert_to_pascal(text: str) -> str:
    return string.capwords(text.replace('_', ' ')).replace(' ', '')

def check_file_exist(file_path: str) -> bool:
    return os.path.exists(os.path.abspath(file_path))