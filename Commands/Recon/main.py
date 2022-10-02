import os
import glob
import re

import click
import pandas

from Utilities.Utils import Utils as utils
from Commands.Recon.leasedline import LeasedLine
from Commands.Recon.parse_circuit import ParseCircuit

project_folder = os.path.dirname(os.path.realpath(__file__))
cli_name = os.path.dirname(os.path.realpath(__file__)).split(os.sep)[-1]
operation_type = ['leasedline']



@click.command(name=cli_name,
               short_help='Set 2 Recon')
@click.option('--operation_type', '-ot',
                required=True,
                type=click.Choice(operation_type),
                help='Operation type')
@click.option('--input_path', '-ip',
                required=True,
                type=str,
                help='Absolute folder path of local storage')
def entrypoint(operation_type: str, input_path: str):
    input_path = os.path.abspath(input_path)

    utils.check_path(input_path)
    utils.check_folder(input_path)

    if operation_type == 'leasedline':
        leasedline = LeasedLine()
        parse_circuit = ParseCircuit()

        leasedline.check_path(input_path)
        parse_circuit.check_path(input_path, leasedline)

        for_circuit_parsing_df = utils.read_all_csv(parse_circuit.circuit_for_parsing_path, parse_circuit.additional_columns)
        for_circuit_parsing_df = parse_circuit.fill_switch_type(for_circuit_parsing_df)
        for_circuit_parsing_df = parse_circuit.standardize_columns(for_circuit_parsing_df)
        parsed_circuit_df = parse_circuit.apply_circuit_parsing(for_circuit_parsing_df)

        utils.save_to_csv(f'{input_path}/Parsed', parsed_circuit_df)

        # iccbs_current_df = utils.read_all_csv(leasedline.iccbs_current_path)
        # processed_leasedline = leasedline.apply_leasedline_process(iccbs_current_df)
