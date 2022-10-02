import re
import os

import pandas

from Utilities.Utils import Utils as utils


class LeasedLine:

    def __init__(self):
        self.leasedline_folder_name = 'LeasedLine'
        self.iccbs_folder_name = 'ICCBS'
        self.iccbs_current_folder_name = 'Current'
        self.iccbs_noncurrent_folder_name = 'NonCurrent'

    def check_path(self, path: str) -> None:
        leasedline_path = os.path.abspath(f'{path}/{self.leasedline_folder_name}')
        iccbs_folder_path = os.path.abspath(f'{leasedline_path}/{self.iccbs_folder_name}')
        iccbs_current_folder_path = os.path.abspath(f'{iccbs_folder_path}/{self.iccbs_current_folder_name}')
        iccbs_noncurrent_folder_path = os.path.abspath(f'{iccbs_folder_path}/{self.iccbs_noncurrent_folder_name}')

        utils.check_path(leasedline_path)
        utils.check_path(iccbs_folder_path)
        utils.check_path(iccbs_current_folder_path)
        utils.check_path(iccbs_noncurrent_folder_path)

        utils.check_folder(leasedline_path)
        utils.check_folder(iccbs_folder_path)
        utils.check_folder(iccbs_current_folder_path)
        utils.check_folder(iccbs_noncurrent_folder_path)

        self.iccbs_current_path = iccbs_current_folder_path
        self.iccbs_noncurrent_path = iccbs_noncurrent_folder_path

    def apply_leasedline_process(self, df: pandas.DataFrame) -> pandas.DataFrame:
        bt_gt_df = df[(df['company_id'] == 'BT') | (df['company_id'] == 'GT')]

        bt_gt_df.drop_duplicates(subset=['net_svc_id'], inplace=True)
        bt_gt_df['l_name'] = bt_gt_df['l_name'].str.replace(',', '.')

        bt_gt_df['NID_Length'] = bt_gt_df['net_svc_id'].apply(len)
        bt_gt_df = bt_gt_df[(bt_gt_df['NID_Length'] == 6) | (bt_gt_df['NID_Length'] == 11)]

        return bt_gt_df


