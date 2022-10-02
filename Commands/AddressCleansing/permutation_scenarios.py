
import pandas

class PermutationScenarios:

    def __init__(self, psgc: pandas.DataFrame):
        self.psgc = psgc

    def apply_scenarios(self, row: pandas.Series) -> pandas.Series:
        psgc = self.psgc
        key_mapping = {
            'PostCode': 'postal_cd',
            'Barangay/District': 'area_name',
            'City': 'town',
            'Province': 'province'
        }
        scenarios: dict = self.get_scenarios()
        row['Cleansing Status'] = ''

        for skey in scenarios:
            s = scenarios[skey]
            keys = list(s.keys())
            psgc_list_query = [f"""(psgc['{k}'] == row['{key_mapping[k]}'])""" for k in keys if s[k]]
            psgc_query_result = eval(f"""len(psgc[eval(' & '.join({psgc_list_query}))]) > 0 if len({psgc_list_query}) > 0 else True""")
            row_list_query = [f""""{row[key_mapping[k]]}" == ''""" for k in keys if s[k] is False]
            row_result = eval(f"""eval(' and '.join({row_list_query})) if len({row_list_query}) > 0 else True""")
            expression = psgc_query_result and row_result

            if expression:
                scenario_category, number = skey.split('_')
                row['scenario'] = f"{'ALIGNED' if scenario_category == 'AS' else 'NOT ALIGNED'} - Scenario {number}"

                if row['scenario'] == 'ALIGNED - Scenario 1':
                    row['Cleansing Status'] = 'Cleansed'
                    row['Script Tagging'] = 'Permutation Scenarios'

                break

        return row

    def get_scenarios(self) -> dict:
        postal_code: str = 'PostCode'
        area_name: str = 'Barangay/District'
        town: str = 'City'
        province: str = 'Province'

        return {
            'AS_1': {
                postal_code: True,
                area_name: True,
                town: True,
                province: True,
            },
            'AS_2': {
                postal_code: False,
                area_name: True,
                town: True,
                province: True,
            },
            'AS_3': {
                postal_code: True,
                area_name: False,
                town: True,
                province: True,
            },
            'AS_4': {
                postal_code: True,
                area_name: True,
                town: False,
                province: True,
            },
            'AS_5': {
                postal_code: True,
                area_name: True,
                town: True,
                province: False,
            },
            'AS_6': {
                postal_code: True,
                area_name: True,
                town: True,
                province: True,
            },
            'AS_7': {
                postal_code: False,
                area_name: False,
                town: True,
                province: True,
            },
            'AS_8': {
                postal_code: False,
                area_name: True,
                town: False,
                province: True,
            },
            'AS_9': {
                postal_code: False,
                area_name: True,
                town: True,
                province: False,
            },
            'AS_10': {
                postal_code: False,
                area_name: True,
                town: True,
                province: True,
            },
            'AS_11': {
                postal_code: True,
                area_name: False,
                town: False,
                province: True,
            },
            'AS_12': {
                postal_code: True,
                area_name: False,
                town: True,
                province: False,
            },
            'AS_13': {
                postal_code: True,
                area_name: False,
                town: True,
                province: True,
            },
            'AS_14': {
                postal_code: True,
                area_name: True,
                town: False,
                province: False,
            },
            'AS_15': {
                postal_code: True,
                area_name: True,
                town: False,
                province: True,
            },
            'AS_16': {
                postal_code: True,
                area_name: True,
                town: True,
                province: False,
            },
            'AS_17': {
                postal_code: False,
                area_name: False,
                town: False,
                province: True,
            },
            'AS_18': {
                postal_code: False,
                area_name: False,
                town: True,
                province: False,
            },
            'AS_19': {
                postal_code: False,
                area_name: False,
                town: True,
                province: True,
            },
            'AS_20': {
                postal_code: False,
                area_name: True,
                town: False,
                province: False,
            },
            'AS_21': {
                postal_code: False,
                area_name: True,
                town: False,
                province: True,
            },
            'AS_22': {
                postal_code: False,
                area_name: True,
                town: True,
                province: False,
            },
            'AS_23': {
                postal_code: True,
                area_name: False,
                town: False,
                province: False,
            },
            'AS_24': {
                postal_code: True,
                area_name: False,
                town: False,
                province: True,
            },
            'AS_25': {
                postal_code: True,
                area_name: False,
                town: True,
                province: False,
            },
            'AS_26': {
                postal_code: True,
                area_name: True,
                town: False,
                province: False,
            },
            'AS_27': {
                postal_code: False,
                area_name: False,
                town: False,
                province: False,
            },
            'AS_28': {
                postal_code: False,
                area_name: False,
                town: False,
                province: True,
            },
            'AS_29': {
                postal_code: False,
                area_name: False,
                town: True,
                province: False,
            },
            'AS_30': {
                postal_code: False,
                area_name: True,
                town: False,
                province: False,
            },
            'AS_31': {
                postal_code: True,
                area_name: False,
                town: False,
                province: False,
            },
            'NAS_1': {
                postal_code: True,
                area_name: False,
                town: False,
                province: False,
            },
        }