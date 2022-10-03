import os
from datetime import datetime
from typing import List

import pandas

from Commands.GoogleDriveAPI.gdrive import GDrive
from Commands.SendEmail.mail import Mail
from Utilities.config import props


class Poller:

    def __init__(self):
        pass

    def poll(self, folder_id: str, gdrive: GDrive) -> List[dict]:
        return gdrive.search(type='sheet', folder_id=folder_id)

    def validate_file_name(self, file: dict) -> dict:
        address_types: List[str] = ['INSTALLATION', 'BILLING', 'COMPANY']
        cfus: List[str] = ['EG', 'SG']

        file['errs'] = []
        filename: str = file['name']
        sp_name: List[str] = os.path.splitext(filename)[0].split('_')

        if len(sp_name) != 4:
            file['errs'].append('Filename is invalid.')
            file['cfu'] = self.get_cfu_by_file_owner(self.get_file_owner(file))

        elif len(sp_name) == 4:
            if sp_name[0] not in address_types:
                file['errs'].append(f'AddressType -> <b>{sp_name[0]}</b> in filename is invalid.')
            else:
                file['address_type'] = sp_name[0]

            if sp_name[1] not in cfus:
                file['errs'].append(f'CFU -> <b>{sp_name[1]}</b> in filename is invalid.')
                file['cfu'] = self.get_cfu_by_file_owner(self.get_file_owner(file))
            else:
                file['cfu'] = sp_name[1]

            try:
                date_given = datetime.strptime(sp_name[2], '%Y%m%d')
                date_today = datetime.strptime(datetime.today().strftime('%Y%m%d'), '%Y%m%d')

                if date_today.year != date_given.year:
                    file['errs'].append(f'DateUploaded year -> <b>{date_given.year}</b> is not the current year.')

                if date_today.month != date_given.month:
                    file['errs'].append(
                        f'DateUploaded month -> <b>{0 if len(str(date_given.month)) == 1 else ""}{date_given.month}</b> is not the current month.')

            except ValueError:
                file['errs'].append(f'DateUploaded -> <b>{sp_name[2]}</b> is invalid.')

            try:
                datetime.strptime(sp_name[3], '%H%M')
            except ValueError:
                file['errs'].append(f'TimeUploaded -> <b>{sp_name[3]}</b> is invalid.')

        return file

    @staticmethod
    def validate_file_columns(file: dict, gdrive: GDrive) -> dict:
        if len(file['errs']) > 0: return file

        req_cols: List[str] = ['wo_cust_addr_id', 'cust_ac_no', 'CFU', 'company name', 'site_no', 'Site_Addr_ID',
                               'Room/Floor No', 'Bldg/House No.', 'Bldg Name', 'Street No./Name', 'Barangay/District',
                               'City', 'Province', 'Region', 'Country', 'PostCode', 'Address Type', 'Top Error(s)',
                               'Is PSGC Compliant', 'PSGC Error(s)']

        file_data: pandas.DataFrame = gdrive.download(file, in_memory_only=True)

        if len(file_data) == 0:
            file['errs'].append('File has empty Sheet')

        for c in file_data.columns:
            if c not in req_cols:
                file['errs'].append(f'Invalid column <b>{c}</b>')

        for c in req_cols:
            if c not in file_data.columns:
                file['errs'].append(f'Column <b>{c}</b> is not existing')

        if 'CFU' in file_data.columns:
            cfu = file_data['CFU'].unique()

            if len(cfu) == 0:
                file['errs'].append('Column <b>CFU</b> is empty')

        return file

    @staticmethod
    def send_errs(files: List[dict], mail: Mail) -> None:
        for f in files:
            subject: str = f"{f['name']} failed validation due to error(s)"
            recipients: str = mail._get_recipients_by_cfu('TEST') if props['system']['mode'] == 'test' else \
                            mail._get_recipients_by_cfu(f['cfu'])
            html_errs = mail._parse_list_to_html(f['errs'])
            payload = {'fileName': f['name'], 'errorList': html_errs}

            mail.send(subject, recipients, 'file-with-error', payload)

    @staticmethod
    def get_cfu_by_filename(filepath: str) -> dict:
        filename_list: List[str] = os.path.splitext(filepath.split(os.sep)[-1])[0].split('_')
        cfu: str = filename_list[1]

        return {'cfu': cfu, 'file': filepath}

    @staticmethod
    def get_file_owner(file: dict) -> str:
        return [p['emailAddress'] for p in file['permissions'] if p['role'] == 'owner'][0]

    @staticmethod
    def get_cfu_by_file_owner(file_owner: str) -> str:
        if file_owner in props['mail']['EG_users']:
            return 'EG'

        if file_owner in props['mail']['SG_users']:
            return 'SG'

        if file_owner in props['mail']['TEST_users']:
            return 'TEST'

    ############
    ## Backup ##
    ############
    # def validate_fallout_folder(self, folder_id: str) -> None:
    #     fallout_folder_name = self.get_fallout_folder_name()
    #     fallout_folder = self.search(type='folder', folder_id=folder_id, name=fallout_folder_name)
    #
    #     if fallout_folder is None: return
    #     if len(fallout_folder) == 0:
    #         print(f'Automatically creating folder -> {fallout_folder_name}, because it does not exists.')
    #         self.create_folder(fallout_folder_name, folder_id)

    # def get_fallout_folder(self, folder_id: str) -> dict:
    #     fallout_folders = self.search(type='folder', folder_id=folder_id)
    #     fallout_folder = self.get_latest_folder_by_name_date(fallout_folders)
    #
    #     return fallout_folder

    # def validate_if_filename_existing(self, files: List[dict], business_concern_folder: dict) -> List[dict]:
    #     for f in files:
    #         if len(f['errs']) > 0: continue
    #
    #         filename = os.path.splitext(f['name'])[0]
    #         fallout_folder = self.get_fallout_folder(business_concern_folder[f['business']][f['business_concern']])
    #         folder_files = self.search(type='sheet', folder_id=fallout_folder['id'])
    #         existing_files = [ff for ff in folder_files if filename == os.path.splitext(ff['name'])[0]]
    #
    #         if len(existing_files) > 0:
    #             f['errs'].append(f"Filename -> <b>{f['name']}</b> already exists")
    #
    #     return files

    # def get_fallout_folder_id_by_filename(self, filepath: str, business_concern_folder: dict) -> dict:
    #     filename_list: List[str] = os.path.splitext(filepath.split(os.sep)[-1])[0].split('_')
    #     business_concern: str = filename_list[0].title()
    #     business: str = filename_list[1]
    #
    #     return {'id': business_concern_folder[business][business_concern], 'file': filepath }

    # def get_latest_file_by_name_datetime(self, files: List[dict]) -> dict:
    #     date_now = datetime.now()
    #     min_date = date_now - timedelta(days=7)
    #
    #     date_list = [(datetime.strptime(f"{os.path.splitext(f['name'])[0].split('_')[2]}{os.path.splitext(f['name'])[0].split('_')[3]}", '%Y%m%d%H%M'), f)
    #                  for f in files
    #                  if datetime.strptime(f"{os.path.splitext(f['name'])[0].split('_')[2]}{os.path.splitext(f['name'])[0].split('_')[3]}", '%Y%m%d%H%M') >= min_date]
    #
    #     if len(date_list) == 0: return None
    #
    #     latest_date, file = max(date_list, key=itemgetter(0))
    #     return file

    # def get_latest_folder_by_name_date(self, folders: List[dict]):
    #     date_list = [(datetime.strptime(f['name'].split(' ')[0], '%Y%m'), f['id']) for f in folders]
    #     latest_date = max(date_list, key=itemgetter(0))
    #
    #     return [f for f in folders if f['id'] == latest_date[1]][0]

    # def get_fallout_folder_name(self) -> str:
    #     date_today = datetime.today()
    #     delta_date = date_today - relativedelta(months=1)
    #     formatted_delta_date = delta_date.strftime("%Y%m")
    #     return f'{formatted_delta_date} Fallouts'
