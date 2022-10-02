import re

import pandas
from rapidfuzz import fuzz


class FreeTextMatching:

    def __init__(self, psgc: pandas.DataFrame):
        self.psgc = psgc
        self.psgc_copy = self.psgc.copy()

        self.psgc_copy['Barangay/District'] = self.psgc_copy['Barangay/District']\
                                                .str.replace(r"\s\(.*\)", "", regex=True)\
                                                .str.replace(" POB.", " ", regex=False)\
                                                .str.replace("BARANGAY ", "", regex=False)

        self.psgc_copy['City'] = self.psgc_copy['City']\
                                    .str.replace("CITY OF ", "", regex=False)\
                                    .str.replace(r"\s\(.*\)", "", regex=True)

        self.psgc_copy['Province'] = self.psgc_copy['Province']\
                                    .str.replace("NCR, CITY OF MANILA, FIRST DISTRICT (NOT A PROVINCE)", "MANILA FIRST DISTRICT", regex=False)\
                                    .str.replace("NCR, ", "", regex=False).str.replace(" (NOT A PROVINCE)", "", regex=False)\
                                    .str.replace(r"\s\(.*\)", "", regex=True)

    def apply_matching(self, row: pandas.Series) -> pandas.Series:
        if row['Cleansing Status'] == 'Cleansed': return row

        address = row['concat_address']
        address = self.replace_potential_words(address)

        town_containability = self.psgc_copy['City'].apply(self.get_value_to_address_containability, args=(address,))
        area_containability = self.psgc_copy['Barangay/District'].apply(self.get_value_to_address_containability, args=(address,))
        province_containability = self.psgc_copy['Province'].apply(self.get_value_to_address_containability, args=(address,))
        matches = self.psgc_copy[town_containability & area_containability & province_containability].to_dict('index')
        matches = [{**matches[mk], 'index': mk} for mk in matches]
        match = self.get_orig_psgc_row(self.get_highest_match(address, matches))

        if bool(match):
            row = {**self.attach_to_fields(row, match), 'Cleansing Status': 'Cleansed',
                   'Script Tagging': 'Free Text Matching'}

        return pandas.Series(row)

    def attach_to_fields(self, row: pandas.Series, match: dict) -> pandas.Series:
        row['postal_cd_NEW'] = match['PostCode']
        row['area_name_NEW'] = match['Barangay/District']
        row['town_NEW'] = match['City']
        row['province_NEW'] = match['Province']

        return row

    def get_orig_psgc_row(self, match: dict):
        return self.psgc.iloc[[match['index']]].to_dict('records')[0] if bool(match) else match

    def get_highest_match(self, address: str, match_list: list) -> dict:
        x = [m for m in match_list if all([m[d] != '' for d in m])]

        if len(x) > 0:

            m = [self.init_score(d, address) for d in x]
            m = sorted(m, key=lambda d: len(d['Barangay/District']), reverse=True)

            if any(['CPO' in x['Barangay/District'] for x in m]) and 'CPO' not in address:
                m = [x for x in m if 'CPO' not in x['Barangay/District']]

            if len(m) == 0: m = [{'score': 0}]

            h_m = max(m, key=lambda x: x['score'])

            return dict() if self.is_duplicate_score(h_m, m) or h_m['score'] == 0 else h_m

        return dict()

    def init_score(self, match: dict, address: str):
        c = 0
        c_f = []
        address = re.sub('[^a-zA-Z0-9 \n\.]', '', address)
        match = {x: re.sub('[^a-zA-Z0-9 \n\.]', '', match[x]) if isinstance(match[x], str) else match[x] for x in match}

        for prop in match:
            if prop in ['Post Code', 'index', *c_f]: continue
            if prop == 'Province' and re.search(fr"\b{match[prop]}\b", address):
                c = c + 3
                c_f.append(prop)
            elif prop == 'City' and re.search(fr"\b{match[prop]}\b", address):
                c = c + 3
                c_f.append(prop)
            elif prop == 'Barangay/District' and re.search(fr"\b{match[prop]}\b", address):
                if match[prop].isnumeric() and (re.search(fr"\bBARANGAY {match[prop]}\b", address) is None or re.search(
                        fr"\bBRGY {match[prop]}\b", address) is None):
                    c = c + 0
                    c_f.append(prop)
                else:
                    c = c + 3
                    c_f.append(prop)

        for prop in match:
            if prop in ['Post Code', 'index', *c_f]: continue
            if re.search(fr"\b{match[prop]}\b", address):
                c = c + 2
                c_f.append(prop)

        for prop in match:
            if prop in ['Post Code', 'index', *c_f]: continue
            if fuzz.WRatio(address, match[prop]) >= 80:
                c = c + 1
                c_f.append(prop)

        if all([x in c_f for x in ['Province', 'City', 'Barangay/District']]):
            match['score'] = c
            return match

        match['score'] = 0
        return match

    def is_duplicate_score(self, highest_match, matches):
        c = 0

        for match in matches:
            if highest_match['score'] == match['score']: c = c + 1

        return False if c == 1 else True

    def get_value_to_address_containability(self, val, address):
        alignment = fuzz.partial_ratio_alignment(val, address)
        return fuzz.partial_ratio(val[alignment.src_start:alignment.src_end], address[alignment.dest_start:alignment.dest_end]) >= 90

    def replace_potential_words(self, text: str) -> str:
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