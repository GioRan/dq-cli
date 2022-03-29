import os
from typing import List, Tuple
from helpers.utilities import read_csv
import pandas

def get_bpt() -> pandas.DataFrame:
    required_columns: List[str] = ['PostCode', 'Barangay/District', 'City', 'Province']
    
    return read_csv(os.getenv('BPT_FILE'), required_columns=required_columns)

def get_psgc() -> pandas.DataFrame:
    required_columns: List[str] = ['x_zip_code', 'x_barangay_name', 'x_municipality_name', 'x_province_name']
    
    return read_csv(os.getenv('PSGC_FILE'), required_columns=required_columns)

def get_bpt_mapping() -> Tuple[pandas.DataFrame, pandas.DataFrame]:
    columns_to_remove: List[str] = ['x_zip_code', 'x_barangay_name', 'x_municipality_name', 'x_province_name', 'PostCode', 'Barangay/District', 'City', 'Province']
    
    return read_csv(os.getenv('BPT_DQ_TO_BPT_MAPPING_FILE'), required_columns=columns_to_remove), read_csv(os.getenv('PSGG_TO_BPT_MAPPING_FILE'), required_columns=columns_to_remove)