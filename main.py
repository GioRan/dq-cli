import importlib
import os

import fire
from dotenv import load_dotenv

from helpers.utilities import convert_to_pascal, check_file_exist


def init_cli(project: str, input_file: str, output_directory: str = os.path.abspath(os.getcwd())) -> None:
    """
    CLI
    :param project: project selection
    :return: Execute DQ scripts via CLI
    """
    
    file: str = os.path.abspath(input_file)
    
    if not check_file_exist(file):
        print(f'File {file} does not exits!')
        return

    module = importlib.import_module(f'projects.{project}')
    class_ = getattr(module, convert_to_pascal(project))
    class_(file)
    
    print(output_directory)

if __name__ == '__main__':
    load_dotenv()
    
    fire.Fire({
        'run': init_cli
    })
