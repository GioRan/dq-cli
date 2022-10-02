import os

import click

from Commands.GoogleDriveAPI.gdrive import GDrive
from Utilities.Utils import Utils as utils

project_folder = os.path.dirname(os.path.realpath(__file__))
cli_name = os.path.dirname(os.path.realpath(__file__)).split(os.sep)[-1]
operation_type = ['upload', 'download']


@click.command(name=cli_name,
               short_help='upload or download with Google Drive API')
@click.option('--operation_type', '-ot',
              type=click.Choice(operation_type),
              help='Operation type')
@click.option('--path', '-p',
              type=str,
              help='Absolute path of local storage')
@click.option('--folder_id', '-fdid',
              type=str,
              help='Folder id from Google Drive. Can get from URL')
@click.option('--file_id', '-flid',
              type=str,
              help='File id. Can get from URL')
@click.option('--filename', '-fn',
              type=str,
              help='Filename from Google Drive. Only applied in operation_type: download')
@click.option('--refresh_token', '-rt',
              type=bool,
              is_flag=True,
              default=False,
              help='Login GoogleDriveAPI credentials, generates token.json')
def cli(operation_type: str, path: str, folder_id: str, file_id: str, filename: str, refresh_token: bool):
    if refresh_token:
        if os.path.exists(f'{project_folder}/token.json'):
            os.remove(f'{project_folder}/token.json')
            GDrive()
            return

    if operation_type is None: raise ValueError('operation_type is required.')
    if path is None: raise ValueError('path is required.')
    if operation_type == 'download':
        if file_id is None:
            if folder_id is None: raise ValueError('g_folder_id is required.')
            if filename is None: raise ValueError('filename is required.')
        else:
            if folder_id is not None: raise ValueError('Remove g_folder_id.')
            if filename is not None: raise ValueError('Remove filename.')

        utils.check_folder(path)

    if operation_type == 'upload':
        if folder_id is None: raise ValueError('g_folder_id is required.')

        utils.check_file(path)

    gdrive = GDrive()

    if operation_type == 'download':
        sheets = gdrive.search(type='sheet', file_id=file_id, folder_id=folder_id, name=filename)

        if sheets is None:
            raise ValueError(f'No sheet found with filename -> {filename}')

        [gdrive.download(file=s, destination_folder=path) for s in sheets]

    if operation_type == 'upload':
        gdrive.upload(folder_id=folder_id, file_path=path)
