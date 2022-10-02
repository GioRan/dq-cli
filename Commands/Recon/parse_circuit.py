import re
import os

import pandas

from Commands.Recon.leasedline import LeasedLine
from Utilities.Utils import Utils as utils

class ParseCircuit:

    def __init__(self):
        self.additional_columns = ['Switch', 'Circuit ID', 'Len', 'Notes', 'Category', 'Circuit For Parsing']
        self.circuit_for_parsing_folder_name = 'Circuit For Parsing'
        self.switch_columns = {
            'ICON': ['Name'],
            'NOKIA': ['Description', 'Service Description'],
            'LSA': ['Port Alias'],
            'MAGOOS': ['Alias'],
            'PWE': ['Service Name'],
            'IPRAN': ['Description'],
            'BEA': ['Services'],
            'BAX': ['Customer', 'Label'],
            'BAYAN': ['Customer', 'Label']
        }

    def check_path(self, path: str, leasedline: LeasedLine) -> None:
        leasedline_path = os.path.abspath(f'{path}/{leasedline.leasedline_folder_name}')
        circuit_for_parsing_folder_path = os.path.abspath(f'{leasedline_path}/{self.circuit_for_parsing_folder_name}')

        utils.check_path(leasedline_path)
        utils.check_path(circuit_for_parsing_folder_path)

        utils.check_folder(leasedline_path)
        utils.check_folder(circuit_for_parsing_folder_path)

        self.circuit_for_parsing_path = circuit_for_parsing_folder_path

    def apply_circuit_parsing(self, df: pandas.DataFrame) -> pandas.DataFrame:
        df = self.tag_non_circuit(df)

        non_circuit = df[df['Category'] == 'Non-Circuit']
        for_parsing = df[df['Category'] == '']

        for_parsing['Circuit ID'] = for_parsing['Circuit For Parsing'].apply(self.extract_circuit_id)
        for_parsing['Len'] = for_parsing['Circuit ID'].apply(len)
        for_parsing.loc[for_parsing['Len'].astype(str).str.contains('6|11'), ['Notes', 'Category']] = ['Valid Circuit ID', 'Circuit']

        df = pandas.concat([non_circuit, for_parsing])
        df.loc[df['Category'] == '', 'Category'] = 'Blanks'

        return df

    def tag_non_circuit(self, df: pandas.DataFrame) -> pandas.DataFrame:
        non_circuit_tagging = {
            'Test': ['Testing', 'Test', 'test', 'Tst', 'TESTING', 'TEST', 'TST'],
            'RCM (Reserved)': ['RCM', 'rcm', 'RMC'],
            'Reserved': ['RESERVED', 'RESERVE', 'Reserved', 'Reserve', 'reserved', 'reserve', 'RT/'],
            'Management': ['MANAGEMENT', 'Management', 'management', 'MGMT', 'Mgmt', 'mgmt', 'MGT', 'Mgt', 'mgt',
                           'MNGT', 'Mngt', 'mngt', 'MGNT', 'Mgnt', 'mgnt', 'MNGMNT', 'Mngmnt', 'mngmnt'],
            'NMS': ['NMS', 'nms'],
            'Troubleshooting': ['TROUBLESHOOTING', 'Troubleshooting', 'troubleshooting'],
            'Trunk': ['TRUNK', 'Trunk', 'trunk', 'TRK', 'Trk', 'trk'],
            'Server': ['SERVER', 'Server', 'server', 'ST/'],
            'Monitoring': ['MONITORING', 'Monitoring', 'monitoring'],
            'Admin': ['ADMIN', 'Admin', 'admin', 'ADMN', 'Admn', 'admn'],
            'Project': ['PROJECT', 'PROJ', 'Project', 'Proj', 'project', 'proj'],
            'Dummy': ['DUMMY', 'Dummy', 'dummy'],
            'Restoral': ['RESTORAL', 'Restoral', 'restoral', 'RESTORATION', 'Restoration', 'restoration'],
            'Protection': ['PROTECTION', 'Protection', 'protection'],
            'vacant port': ['---'],
            'ODU': ['ODU'],
            'Wireless': ['Wireless', 'RNC', 'BTS', '3G', '2G'],
            'CT but no circuit': ['CT (no circuit)'],
            'Wimax': ['Wimax'],
            'Demo': ['Demo'],
            'no information': ['The rest'],
            'Exclude': ['FMS']
        }

        for t in non_circuit_tagging:
            df.loc[df['Circuit For Parsing'].str.contains('|'.join(non_circuit_tagging[t])), ['Notes', 'Category']] = [t, 'Non-Circuit']

        return df

    def extract_circuit_id(self, value: str) -> str:
        try:

            value = value.replace(' ', '')

        except:
            print(True)
        patterns = [
            "IC-[a-zA-Z0-9]{3}-[a-zA-Z0-9]{4}",
            "IH-[a-zA-Z0-9]{3}-[a-zA-Z0-9]{4}",
            "BT-[0-9]{6}",
            "BT[0-9]{6}",
            "CT/[0-9]{6}",
            "CT/BT-[0-9]{6}",
        ]

        numeric_only = ['BT-', 'BT', 'CT/', 'CT/BT-']

        for p in patterns:
            cp = re.compile(p)
            ms = cp.findall(value)

            if len(ms) > 0:
                m = ms[0]
                if any([n in m for n in numeric_only]):
                    return re.compile("[0-9]{6}").findall(m)[0]

                return ms[0]

        return ''

    def standardize_columns(self, df: pandas.DataFrame) -> pandas.DataFrame:
        dfs = []

        for s in self.switch_columns:
            switch_df = df[df['Switch'] == s]

            if not switch_df.empty:
                switch_df['Circuit For Parsing'] = switch_df[self.switch_columns[s]].agg(' '.join, axis=1)
                dfs.append(switch_df)

        df = pandas.concat(dfs)
        df = df[self.additional_columns]

        return df

    def fill_switch_type(self, df: pandas.DataFrame) -> pandas.DataFrame:
        df['Switch'] = df['Filename'].str.split('_').apply(lambda x: x[1])

        return df
