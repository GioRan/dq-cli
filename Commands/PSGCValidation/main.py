import glob
import os

import click

from Commands.GoogleDriveAPI.gdrive import GDrive
from Commands.PSGCValidation.psgc_validation import PSGCValidation
from Commands.PollAddress.poller import Poller as poller
from Commands.SendEmail.mail import Mail
from Commands.TopErrors.top_errors import TopErrors
from Utilities.Utils import Utils as utils
from Utilities.config import props

project_folder = os.path.dirname(os.path.realpath(__file__))
cli_name = os.path.dirname(os.path.realpath(__file__)).split(os.sep)[-1]


@click.command(name=cli_name, )
@click.option('--input', '-i',
              type=str)
def cli(input: str) -> None:
    mail = Mail()
    validation = PSGCValidation(input)
    top_errors = TopErrors(validation.folder_path)
    gdrive = GDrive()

    for df, filename in validation.dfs:
        cfu = filename.split('_')[1]

        df['concat'] = df[validation.req_cols].agg('_'.join, axis=1)
        df = utils.parallelize(top_errors.tag_errors, df)
        df = utils.parallelize(validation.validation, df)

        df.drop(['concat'], axis=1, inplace=True)

        valid_rows = df[(df['PSGC Error(s)'] == '') & (df['Is PSGC Compliant'] == 'True')]
        invalid_rows = df[~df.index.isin(valid_rows.index)]

        if len(valid_rows) > 0:
            utils.save_to_excel(f'{input}/{filename}_passed', valid_rows)

        if len(invalid_rows) > 0:
            utils.save_to_excel(f'{input}/{filename}_errors', invalid_rows)

        error_files = glob.glob(f'{input}/*_errors.xlsx')
        passed_files = glob.glob(f'{input}/*_passed.xlsx')
        error_files = [poller.get_cfu_by_filename(f) for f in error_files]
        passed_files = [poller.get_cfu_by_filename(f) for f in passed_files]

        [gdrive.upload(folder_id=props['gdrive'][f"poll_{f['cfu']}_rejected"], file_path=f['file']) for f in
         error_files]
        [gdrive.upload(folder_id=props['gdrive'][f"poll_archive_passed"], file_path=f['file']) for f in
         passed_files]

        validation.send_validation_result(df, valid_rows, invalid_rows, cfu, filename, mail)

    validation.cleanup_files()
