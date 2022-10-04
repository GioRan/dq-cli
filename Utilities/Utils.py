import glob
import json
import logging
import os
import shutil
from functools import partial
from io import BytesIO
from typing import List, Any, Union

import itertools
import pandas
from tqdm.contrib.concurrent import process_map

from Services.log_formatter import LogFormatter
from Utilities.config import props


class Utils:

    @staticmethod
    def read_csv(input_dir: Union[str, BytesIO], required_columns=None, nrows=None, encoding='utf-8', converters=None,
                 cast_to_string=True,
                 additional_columns=None) -> pandas.DataFrame:

        """
        Read csv from file path

        :param input_dir: file path
        :type input_dir: str
        :param required_columns: required columns, defaults to None
        :type required_columns: List[str]
        :param nrows: number of rows, defaults to None
        :type nrows: int
        :param encoding: text encoding, defaults to utf-8
        :type encoding: str
        :param converters: specify function to convert column(s), defaults to None
        :type converters: dict
        :param cast_to_string: cast all columns to string
        :type cast_to_string: bool
        :param additional_columns: additional columns that will be appended after the last column
        :type additional_columns: List[str]
        :return: pandas.DataFrame
        :rtype: pandas.DataFrame
        """
        logging.info(f'Loading dataframe -> {input_dir}')

        if additional_columns is None:
            additional_columns = []

        csv = pandas.read_csv(input_dir, header=0, index_col=False, lineterminator='\n', usecols=required_columns,
                              nrows=nrows, encoding=encoding, low_memory=False, converters=converters,
                              keep_default_na=False) \
            .replace('\r', '', regex=True).replace('#N/A', '').replace(u'\xa0', u'') \
            .apply(lambda x: x.astype(str) if cast_to_string else x) \
            .apply(lambda x: x.str.strip() if cast_to_string else x)

        for column in additional_columns:
            csv[column] = ''

        csv.columns = csv.columns.str.strip()

        logging.info(f'Dataframe length -> {len(csv)}')

        return csv

    @staticmethod
    def read_excel(input_dir: Union[str, BytesIO], cast_to_string=True, additional_columns=None) -> pandas.DataFrame:
        """
        Read Excel file from given file path

        :param input_dir: file path
        :type input_dir: str
        :param cast_to_string: cast all columns to string
        :type cast_to_string: bool
        :param additional_columns: additional columns that will be appended after the last column
        :type additional_columns: List[str]
        :return: pandas.DataFrame
        :rtype: pandas.DataFrame
        """
        logging.info(f'Loading dataframe -> {input_dir}')

        if additional_columns is None:
            additional_columns = []

        excel = pandas.read_excel(input_dir, sheet_name=0, header=0, index_col=False, engine='openpyxl',
                                  keep_default_na=False) \
            .replace('\r', '', regex=True).replace('#N/A', '').replace(u'\xa0', u'') \
            .apply(lambda x: x.astype(str) if cast_to_string else x) \
            .apply(lambda x: x.str.strip() if cast_to_string else x)

        for column in additional_columns:
            excel[column] = ''

        excel.columns = excel.columns.str.strip()

        logging.info(f'Dataframe length -> {len(excel)}')

        return excel

    @staticmethod
    def read_all_csv(input_dir: str, additional_columns=None, concat: bool = True):
        """
        Read all csv files from given folder path

        :param input_dir: folder path to read all csv files
        :type input_dir: str
        :param additional_columns: additional columns that will be appended after the last column
        :type additional_columns: List[str]
        :param concat: concat DataFrame vertically if set to True then return DataFrame, otherwise, return list of
        DataFrame and filename as tuple
        :type concat: bool
        :return: Union[pandas.DataFrame, List[tuple[pandas.DataFrame, str]]]
        :rtype: Union[pandas.DataFrame, List[tuple[pandas.DataFrame, str]]]
        """
        csv_files_path = glob.glob(f'{input_dir}/*.csv')
        dfs = []

        for csv in csv_files_path:
            df = Utils.read_csv(csv, additional_columns=additional_columns)

            filename = os.path.splitext(csv.split(os.sep)[-1])[0]

            if concat:
                df['Filename'] = filename

            dfs.append((df, filename))

        if concat:
            return pandas.concat([df for df, f in dfs], axis=0, ignore_index=True)

        return dfs

    @staticmethod
    def read_all_excel(input_dir: str, additional_columns=None, concat: bool = True) -> Union[pandas.DataFrame,
                                                                                              List[tuple[
                                                                                                  pandas.DataFrame,
                                                                                                  str]]]:
        """
        Read all Excel files from given folder path

        :param input_dir: folder path to read all csv files
        :type input_dir: str
        :param additional_columns: additional columns that will be appended after the last column
        :type additional_columns: List[str]
        :param concat: concat DataFrame vertically if set to True then return DataFrame, otherwise, return list of
        DataFrame and filename as tuple
        :type concat: bool
        :return: Union[pandas.DataFrame, List[tuple[pandas.DataFrame, str]]]
        :rtype: Union[pandas.DataFrame, List[tuple[pandas.DataFrame, str]]]
        """
        csv_files_path = glob.glob(f'{input_dir}/*.xlsx')
        dfs = []

        for csv in csv_files_path:
            df = Utils.read_excel(csv, additional_columns=additional_columns)

            filename = os.path.splitext(csv.split(os.sep)[-1])[0]

            if concat:
                df['Filename'] = filename

            dfs.append((df, filename))

        if concat:
            return pandas.concat([df for df, f in dfs], axis=0, ignore_index=True)

        return dfs

    @staticmethod
    def save_to_excel(output_file: str, df: pandas.DataFrame) -> None:
        """
        Save DataFrame to Excel format

        :param output_file: file path, NOTE: file path should not include file extension
        :type output_file: str
        :param df: DataFrame
        :type df: pandas.DataFrame
        :return: None
        :rtype: None
        """
        excel_output: pandas.ExcelWriter = pandas.ExcelWriter(f'{output_file}.xlsx', engine='xlsxwriter')

        df.to_excel(excel_output, index=False)
        excel_output.save()

        logging.info(f'source df: {output_file}')
        logging.info(f'df length: {len(df)}')

    @staticmethod
    def save_to_csv(output_file: str, df: pandas.DataFrame) -> None:
        """
        Save DataFrame to csv format

        :param output_file: file path, NOTE: file path should not include file extension
        :type output_file: str
        :param df: DataFrame
        :type df: pandas.DataFrame
        :return: None
        :rtype: None
        """
        df.to_csv(f'{output_file}.csv', index=False, encoding="utf-8-sig")
        logging.info('output df: ' + output_file)

    @staticmethod
    def save_to_csv_by_group(output_file: str, df: pandas.DataFrame, field: str):
        """
        Save DataFrame to csv format by group, with given column name as reference for group

        :param output_file: file path, NOTE: file path should not include file extension
        :type output_file: str
        :param df: DataFrame
        :type df: DataFrame
        :param field: column name to be used for group
        :type field: str
        :return: None
        :rtype: None
        """
        df.groupby(field).apply(lambda x: Utils.save_to_csv(f'{output_file}_{x.name}.csv', x))

    @staticmethod
    def move_files(files: List[str], destination_folder: str) -> None:
        """
        Move list of file path to destination folder path

        :param files: list of file path
        :type files: List[str]
        :param destination_folder: Destination folder path
        :type destination_folder: str
        :return: None
        :rtype: None
        """
        [shutil.move(f, destination_folder) for f in files]

    @staticmethod
    def check_path(path: str) -> str:
        """
        Check if path is existing, should be file path or folder path, otherwise raise Exception

        :param path: File path or folder path
        :type path: str
        :return: Absolute path of given path
        :rtype: str
        """
        path = os.path.abspath(path)

        if not os.path.exists(path):
            raise ValueError(f'The path -> {path} does not exists.')

        return path

    @staticmethod
    def check_folder(path: str) -> str:
        """
        Check folder if existing, should be folder path, otherwise raise Exception

        :param path: Folder path
        :type path: str
        :return: Absolute path of given path
        :rtype: str
        """

        path = Utils.check_path(path)
        if not os.path.isdir(path):
            raise ValueError(f'The path -> {path} should be a folder path.')

        return path

    @staticmethod
    def check_file(path: str) -> str:
        """
        Check file path if existing, should be file path, otherwise raise Exception

        :param path: File path
        :type path: str
        :return: Absolute path of given path
        :rtype: str
        """
        path = Utils.check_path(path)
        if not os.path.isfile(path):
            raise ValueError(f'The path -> {path} should be a file path.')

        return path

    @staticmethod
    def parallelize(func, df: pandas.DataFrame, **kwargs) -> pandas.DataFrame:
        """
        Runs given function in parallel, accepts DataFrame in respect to function that will be used

        :param func: Function that will be used in parallel on DataFrame
        :type func: function
        :param df: pandas.DataFrame
        :type df: pandas.DataFrame
        :param kwargs: positional argument that will be passed to function
        :type kwargs: kwargs
        :return: pandas.DataFrame
        :rtype: pandas.DataFrame
        """
        row_list = [row for i, row in df.iterrows()]

        logging.info(f"Using {props['system']['mp_max_workers']} cpu workers")
        logging.info(f"Using {props['system']['mp_chunksize']} chunksize")
        res = process_map(partial(func, **kwargs), row_list, max_workers=props['system']['mp_max_workers'],
                          chunksize=props['system']['mp_chunksize'])

        if all(isinstance(r, pandas.Series) for r in res):
            return pandas.DataFrame(res)

        if all(isinstance(r, List) for r in res):
            return pandas.DataFrame(itertools.chain.from_iterable(res))

    @staticmethod
    def load_json(file_path: str) -> Any:
        """
        Loads JSON file

        :param file_path: JSON file path
        :type file_path: str
        :return: Any
        :rtype: Any
        """
        with open(file_path, 'r') as f:
            return json.load(f)

    @staticmethod
    def init_logger() -> None:
        """
        Initialize logger, custom logger from LogFormatter class

        :return: None
        :rtype: None
        """
        log_formatter = LogFormatter()

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)

        file_handler = logging.FileHandler('debug.log')
        file_handler.setFormatter(log_formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)

        # logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG,
        #                     format='%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
