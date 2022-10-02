import os
from datetime import datetime

import pandas

from Utilities.Utils import Utils as utils


class Constants:
    address_type_list = ['Installation', 'Billing', 'Company']
    concern_type_list = ['EG', 'SG']
    installation_and_billing_columns = ['addr_id', 'cust_ac_no', 'CFU', 'rm_flr_no', 'bldg_name', 'hse_num',
                                        'street_name', 'area_name', 'town', 'province', 'postal_cd']

    address_columns = {
        'Installation': {
            'EG': installation_and_billing_columns,
            'SG': installation_and_billing_columns
        },
        'Billing': {
            'EG': installation_and_billing_columns,
            'SG': installation_and_billing_columns
        },
        'Company': {
            'EG': ['ID', 'SG_STREET__C', 'SG_ZIP__C', 'SG_CITY__C', 'EGFS1_PROVINCE__C', 'BARANGAY__C'],
            'SG': ['ID', 'BUILDING_NAME_BLDG_NO__C', 'SG_STREET__C', 'SG_ZIP__C', 'SG_CITY__C',
                   'SGFS1_PROVINCE__C', 'FLOOR_ROOM_NUMBER__C', 'BARANGAY__C']
        }
    }

    column_mapping = {
        'Company': {
            'EG': {
                'ID': 'addr_id',
                'SG_STREET__C': 'street_name',
                'SG_ZIP__C': 'postal_cd',
                'SG_CITY__C': 'town',
                'EGFS1_PROVINCE__C': 'province',
                'BARANGAY__C': 'area_name'
            },
            'SG': {
                'ID': 'addr_id',
                'BUILDING_NAME_BLDG_NO__C': 'bldg_name',
                'SG_STREET__C': 'street_name',
                'SG_ZIP__C': 'postal_cd',
                'SG_CITY__C': 'town',
                'SGFS1_PROVINCE__C': 'province',
                'BARANGAY__C': 'area_name',
                'FLOOR_ROOM_NUMBER__C': 'rm_flr_no'
            }
        }
    }

    required_columns = ['rm_flr_no', 'bldg_name', 'hse_num', 'street_name', 'area_name', 'town', 'province',
                        'postal_cd', 'Cleansing Status', 'Script Tagging', 'scenario', 'postal_cd_NEW',
                        'area_name_NEW', 'town_NEW', 'province_NEW', 'concat_address']


class AddressCleansing(Constants):

    def __init__(self, input: str, bypass: bool = False):
        """
       __init__ - check file path, initialize required columns, add columns, map columns

       :param input: input file path
       :type input: str
       :param bypass: bypass file checks
       :type bypass: bool
       """

        file_path = utils.check_file(input)

        self.output_path = os.path.dirname(os.path.realpath(file_path))
        self.filename = os.path.splitext(file_path.split(os.sep)[-1])[0]

        if not bypass:
            self.validate_filename(self.filename)

        self.address_type = self.filename.split('_')[0]
        self.cfu = self.filename.split('_')[1]

        if bypass:
            columns = self.installation_and_billing_columns
        else:
            columns = self.address_columns[self.address_type][self.cfu]

        df: pandas.DataFrame = utils.read_csv(file_path, required_columns=columns)
        df = self.map_columns(df, self.address_type, self.cfu)
        self.df = self.add_required_columns(df)

    def add_required_columns(self, df: pandas.DataFrame) -> pandas.DataFrame:
        """
        __add_required_columns (private) - add columns if not existing based on self.__required_columns

        :param df: DataFrame
        :type df: pandas.DataFrame
        :return: pandas.DataFrame
        :rtype: pandas.DataFrame
        """
        for c in self.required_columns:
            if c not in df.columns:
                df[c] = ''

        return df

    def map_columns(self, df: pandas.DataFrame, address_type: str, cfu: str, reverse: bool = False) -> \
            pandas.DataFrame:
        """
        __map_columns (private) - map columns based on self.__column_mapping

        :param df: DataFrame
        :type df: pandas.DataFrame
        :param address_type: from filename
        :type address_type: str
        :param cfu: from filename
        :type cfu: str
        :param reverse: reverse column mapping, uses values instead of keys
        :type reverse: bool
        :return: pandas.DataFrame
        :rtype: pandas.DataFrame
        """
        if address_type not in self.column_mapping: return df

        if reverse:
            reversed_mapping = dict((v, k) for k, v in self.column_mapping[address_type][cfu].items())
            return df.rename(columns=reversed_mapping)

        return df.rename(columns=self.column_mapping[address_type][cfu])

    def validate_filename(self, filename: str) -> None:
        """
        __validate_filename (private) - validate filename based on format (addressType_CFU_Delta_Date -> e.g.
        Installation_EG_Delta_Aug2022), can be bypassed

        :param filename: from file_path
        :type filename: str
        :return: None
        :rtype: None
        """
        f_split = filename.split('_')

        if len(f_split) != 4:
            raise ValueError(f'Invalid filename -> {filename}, must be in format (e.g. Installation_EG_Delta_Aug2022)')

        if f_split[0] not in self.address_type_list:
            raise ValueError(f'Invalid position in filename -> {f_split[0]}, must be in {self.address_type_list} '
                             f'format')

        if f_split[1] not in self.concern_type_list:
            raise ValueError(f'Invalid position in filename -> {f_split[1]}, must be in {self.concern_type_list} '
                             f'format')

        if f_split[2] != 'Delta':
            raise ValueError(f'Invalid position in filename -> {f_split[2]}, should be Delta')

        date_given = None
        date_today = None

        try:
            date_given = datetime.strptime(f_split[3], '%b%Y')
            date_today = datetime.strptime(datetime.today().strftime('%b%Y'), '%b%Y')
        except:
            raise ValueError(f'Invalid format -> {f_split[3]}, must be Aug2022 format')

        if date_today.year != date_given.year:
            raise ValueError(f'Invalid position in filename -> {f_split[3]}, year should be year today')
        if (date_today.month - 1) != date_given.month:
            raise ValueError(f'Invalid position in filename -> {f_split[3]}, month should be the previous month')
