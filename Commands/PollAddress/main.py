import json
import logging
import os

import click
import time

from Commands.GoogleDriveAPI.gdrive import GDrive
from Commands.PSGCValidation.main import cli as psgc_cli, cli_name as psgc_cli_name
from Commands.PollAddress.poller import Poller
from Commands.SendEmail.mail import Mail
from Utilities.config import props

project_folder = os.path.dirname(os.path.realpath(__file__))
cli_name = os.path.dirname(os.path.realpath(__file__)).split(os.sep)[-1]


@click.command(name=f'{cli_name}',
               short_help='Poll drive directory for existing files then move it on another directory.')
@click.pass_context
def cli(ctx):
    mail = Mail()
    gdrive = GDrive()
    poller = Poller()

    files = poller.poll(props['gdrive']['poll_inbound'], gdrive)

    if len(files) > 0:
        logging.info(f"Found files from {props['gdrive']['poll_inbound']}")
        logging.info(json.dumps(files))

        files = [poller.validate_file_name(f) for f in files]
        files = [poller.validate_file_columns(f, gdrive) for f in files]

        invalid_files = [f for f in files if len(f['errs']) > 0]
        valid_files = [f for f in files if len(f['errs']) == 0]

        for f in valid_files:
            dest_folder = f'{os.path.dirname(project_folder)}/{psgc_cli_name}/Resource'

            logging.debug(dest_folder)
            gdrive.download(f, destination_folder=dest_folder)
            gdrive.move_to_folder(f['id'], props['gdrive']['poll_archive_for_validation'])

            subject: str = f"{f['name']} successfully received, process ongoing"
            recipients: str = mail._get_recipients_by_cfu('TEST') if props['system']['mode'] == 'test' else \
                        mail._get_recipients_by_cfu(f['cfu'])
            mail.send(subject, recipients, 'file-received', {'fileName': f['name']})

            ctx.invoke(psgc_cli, input=dest_folder)

        [gdrive.move_to_folder(f['id'], props['gdrive'][f"poll_{f['cfu']}_rejected"]) for f in invalid_files]
        poller.send_errs(invalid_files, mail)

    else:
        logging.warning('No Files in directory.')
