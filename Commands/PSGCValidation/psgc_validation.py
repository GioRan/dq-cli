import glob
import os

import pandas

from Commands.SendEmail.mail import Mail
from Commands.TopErrors.top_errors import TopErrors
from Services.psgc_new import PSGC_NEW
from Utilities.Utils import Utils as utils
from Utilities.config import props


class Constants:
    req_cols = ['PostCode', 'Barangay/District', 'City', 'Province']


class PSGCValidation(Constants):

    def __init__(self, input: str) -> None:
        self.cwd = os.path.dirname(os.path.realpath(__file__))

        if input is None:
            input = f'{self.cwd}/Resource'

        self.folder_path = utils.check_folder(input)
        self.dfs = utils.read_all_excel(self.folder_path, concat=False)
        self.psgc = PSGC_NEW()
        self.top_errors = TopErrors(self.folder_path)

    def validation(self, row: pandas.Series) -> pandas.Series:
        r_fields = self.req_cols
        match = self.psgc.match(row['concat'], 'concat')
        err_field = 'PSGC Error(s)'
        errs = []

        if len(match) > 0:
            row['Is PSGC Compliant'] = 'True'
        else:
            row['Is PSGC Compliant'] = 'False'
            errs.append('PSGC combination does not match')

            for f in r_fields:
                if len(self.psgc.match(row[f], f)) == 0:
                    errs.append(f'{f} is invalid')

        row[err_field] = ' | '.join(errs)

        return row

    def send_validation_result(self,
                               original_df: pandas.DataFrame,
                               valid_rows: pandas.DataFrame,
                               invalid_rows: pandas.DataFrame,
                               cfu: str,
                               file_name: str,
                               mail: Mail):

        total_rows: int = len(original_df)
        recipients: str = mail._get_recipients_by_cfu('TEST') if props['system']['mode'] == 'test' else \
            mail._get_recipients_by_cfu(cfu)

        if len(invalid_rows) > 0:
            subject: str = f"{file_name} validation completed with error(s)"
            mail.send(subject, recipients, 'validation-with-error',
                      {'fileName': file_name,
                       'totalRows': total_rows,
                       'validRows': len(valid_rows),
                       'invalidRows': len(invalid_rows)})

        if total_rows == len(valid_rows):
            subject: str = f"{file_name} validation completed"
            mail.send(subject, recipients, 'validation-no-error',
                      {'fileName': file_name,
                       'totalRows': total_rows,
                       'validRows': len(valid_rows)})

    def cleanup_files(self):
        files = glob.glob(f'{self.folder_path}/*')
        for f in files:
            os.remove(f)
