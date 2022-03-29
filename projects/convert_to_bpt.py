from sqlite3 import DatabaseError
from typing import List
import pandas
from helpers.static_getter import get_bpt_mapping
from helpers.utilities import read_csv
from operator import attrgetter
import numpy

class ConvertToBpt:
    
    def __init__(self, input_file: str) -> None:
        self.df: pandas.DataFrame = read_csv(input_file)
    
        self.bpt: pandas.DataFrame
        self.psgc: pandas.DataFrame
        
        self.bpt, self.psgc = get_bpt_mapping()
        
        self.run()
        
        
    def run(self) -> None:
        print()
    #     df: pandas.DataFrame; bpt: pandas.DataFrame; psgc: pandas.DataFrame
    #     df, bpt, psgc = attrgetter('df', 'bpt', 'psgc')(self)
        
    #     psgc_columns: List[str] = psgc.columns.values.tolist()
        
    #     # df['x_zip_code'] = df['x_zip_code'].apply(lambda x: str(int(float(x))) if x != '' else x)
        
    #     df['concat'] = df[psgc_columns].agg('_'.join, axis=1).replace({ '___': numpy.nan, 'ñ': 'Ñ'}).str.upper()
        
    #     df = df.merge(bpt, left_on='concat', right_on='BPT_DQ_CONCAT', how='left')
    #     df = df.merge(psgc, left_on='concat', right_on='PSGC_CONCAT', how='left')
        
    #     df['POSTAL_CODE'] = numpy.where(df['BPT_DQ_POSTAL_CODE'].isnull(), df['PSGC_POSTAL_CODE'], df['BPT_DQ_POSTAL_CODE'])
    #     df['AREA'] = numpy.where(df['BPT_DQ_AREA'].isnull(), df['PSGC_AREA'], df['BPT_DQ_AREA'])
    #     df['TOWN'] = numpy.where(df['BPT_DQ_TOWN'].isnull(), df['PSGC_TOWN'], df['BPT_DQ_TOWN'])
    #     df['PROVINCE'] = numpy.where(df['BPT_DQ_PROVINCE'].isnull(), df['PSGC_PROVINCE'], df['BPT_DQ_PROVINCE'])
    #     df['Match Status'] = numpy.where(df['BPT_DQ_Match Status'].isnull(), df['PSGC_Match Status'], df['BPT_DQ_Match Status'])
    #     df['Affected Field(s)'] = numpy.where(df['BPT_DQ_Affected Field(s)'].isnull(), df['PSGC_Affected Field(s)'], df['BPT_DQ_Affected Field(s)'])
    #     df['Value Comparison'] = numpy.where(df['BPT_DQ_Value Comparison'].isnull(), df['PSGC_Value Comparison'], df['BPT_DQ_Value Comparison'])

    #     df = df.loc[:,~df.columns.str.startswith('BPT_DQ_')]
    #     df = df.loc[:,~df.columns.str.startswith('PSGC_')]
    #     df = df.loc[:,~df.columns.str.startswith('b_')]
    #     df = df.loc[:,~df.columns.str.startswith('p_')]
        
    #     #######################################
        
    #     valid_match_status: List[str] = ['Mismatch in 1 field only', 'Mismatch in multiple fields only']

    #     df[psgc_columns[0]] = numpy.where(df['Match Status'].isin(valid_match_status) & df['Affected Field(s)'].str.contains('Postal'), 
    #                                     df['POSTAL_CODE'], df[psgc_columns[0]])

    #     df[psgc_columns[1]] = numpy.where(df['Match Status'].isin(valid_match_status) & df['Affected Field(s)'].str.contains('Area'), 
    #                                     df['AREA']df['concat'] = 
    # def concat(self, df: pandas.DataFrame) -> pandas.DataFrame:
    #     return df[psgc_columns].agg('_'.join, axis=1).replace({ '___': numpy.nan, 'ñ': 'Ñ'}).str.upper()
        
    # def is_match(self, x, psgc_columns) -> bool:
    #     if x['Match Status'] in ['Mismatch in 1 field only', 'Mismatch in multiple fields only']:
    #         return int(float(x[psgc_columns[0]])) == int(float(x['POSTAL_CODE'])) and x[psgc_columns[1]].upper() == x['AREA'].upper() and x[psgc_columns[2]].upper() == x['TOWN'].upper() and x[psgc_columns[3]].upper() == x['PROVINCE'].upper()
        
    #     return False

        # =AND(IF(OR(ISNUMBER(FIND(P2,"Mismatch in 1 field only")),ISNUMBER(FIND(P2,"Mismatch in multiple fields only"))),TRUE,FALSE),AND(EXACT(UPPER(C2),UPPER(L2)),EXACT(UPPER(J2),UPPER(M2)),EXACT(UPPER(G2),UPPER(N2)),EXACT(UPPER(H2),UPPER(O2))))
        # =AND(IF(OR(ISNUMBER(FIND(Q2,"Mismatch in 1 field only")),ISNUMBER(FIND(Q2,"Mismatch in multiple fields only"))),TRUE,FALSE),AND(EXACT(UPPER(D2),UPPER(M2)),EXACT(UPPER(K2),UPPER(N2)),EXACT(UPPER(H2),UPPER(O2)),EXACT(UPPER(I2),UPPER(P2))))
        # =AND(IF(OR(ISNUMBER(FIND(L2,"Mismatch in 1 field only")),ISNUMBER(FIND(L2,"Mismatch in multiple fields only"))),TRUE,FALSE),AND(EXACT(UPPER(C2),UPPER(H2)),EXACT(UPPER(F2),UPPER(I2)),EXACT(UPPER(D2),UPPER(J2)),EXACT(UPPER(E2),UPPER(K2))))
        
    