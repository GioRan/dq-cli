import os
import re

import pandas

from Utilities.Utils import Utils as utils


class Constants:
    req_cols = ['Street No./Name', 'Barangay/District', 'City', 'Province', 'PostCode']


class TopErrors(Constants):

    def __init__(self, input: str = None):
        self.cwd = os.path.dirname(os.path.realpath(__file__))

        if input is None:
            input = f'{self.cwd}/Resource'

        self.folder_path = utils.check_folder(input)
        self.dfs = utils.read_all_excel(self.folder_path, concat=False)

    def tag_errors(self, row: pandas.Series) -> pandas.Series:
        """
        Tag errors if any on column Top Errors(s), if no errors found tag default errors

        :param row: each row of DataFrame
        :type row: pandas.Series
        :return: pandas.Series
        :rtype: pandas.Series
        """
        r_fields = self.req_cols
        err_field = 'Top Error(s)'
        errs = []
        street_pattern = "[a-zA-Z0-9.,\-'\"# ]"
        area_pattern = "[a-zA-Z0-9.,\-'() ]"
        town_province_pattern = "[a-zA-Z,.\-'() ]"
        postal_cd_pattern = "[0-9]"

        for f in r_fields:
            row_val = str(row[f]).strip()

            if row_val == '':
                errs.append(f'{f} not available')
                continue

            if f == 'street_name' and bool(re.match(street_pattern, row_val)) is False:
                errs.append(f'{f} contains invalid special character')

            if f in ['area_name', 'Barangay/District'] and bool(re.match(area_pattern, row_val)) is False:
                errs.append(f'{f} contains invalid special character')

            if f in ['town', 'province', 'City', 'Province'] and bool(
                    re.match(town_province_pattern, row_val)) is False:
                errs.append(f'{f} contains invalid special character')

            if f in ['postal_cd', 'PostCode'] and bool(re.match(postal_cd_pattern, row_val)) is False:
                errs.append(f'{f} contains non-numeric character')

            if f in ['postal_cd', 'PostCode'] and all([s == '0' for s in row_val]):
                errs.append(f'{f} is all zero')

            if any([s.lower() in row_val for s in ['dummy', 'null', 'test']]) or all(
                    [s in ['.', ',', '-'] for s in row_val]):
                errs.append(f'{f} contains default values')
                continue

        if len(errs) == 0:
            errs.append('Recommended address failed confidence level score defined')

        row[err_field] = ' | '.join(errs)

        return row
