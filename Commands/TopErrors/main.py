import os

import click

from Commands.TopErrors.top_errors import TopErrors
from Utilities.Utils import Utils as utils

project_folder = os.path.dirname(os.path.realpath(__file__))
cli_name = os.path.dirname(os.path.realpath(__file__)).split(os.sep)[-1]


@click.command(name=cli_name, )
@click.option('--input', '-i',
              type=str)
def cli(input: str = None):
    top_errors = TopErrors(input)

    for df, filename in top_errors.dfs:
        df = utils.parallelize(top_errors.tag_errors, df)

        utils.save_to_excel(f'{top_errors.folder_path}/{filename}_', df)
