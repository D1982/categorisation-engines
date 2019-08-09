"""Common utilities.

Basic utilities e.g. for dealing with files (data, JSON).
Working With JSON Data in Python: https://realpython.com/python-json/

"""
import Categorisation.Common.config as cfg

import csv
import json
import os.path
import logging
import sys


class FileHandler:

    """
    File handling utility class.
    """

    def read_json_file(self, filename):
        """
        Read a JSON file from the local file system.

        :param filename: the full qualified filename (path + file).
        :return: a python ``Object`` (``dict``) representing the json read from the file.
        :raises: Any exception that could potentially occur will be raised.
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        extension = os.path.splitext(filename)[1]
        try:
            if extension == '.json':
                with open(filename) as file:
                    data = json.load(file)
        except Exception as ex:
            logging.error(ex)
            raise

        return data

    def write_json_file(self, json_data, filename):
        """
        Write a JSON file to the local file system.

        :param json_data: A dictionary containing the data to be written
        :param filename: the full qualified filename (path + file)
        :return: True if the file was written successfully, otherwise False
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        try:
            json_file = open(filename, 'w')
            json.dump(json_data, json_file)
            json_file.write('\n')
            success = True
        except Exception as ex:
            logging.error(ex)
            success = False

        return success


    def read_csv_file(self, filename, fieldnames, skip_header=True):
        """
        Read a CSV file from the local file system.

        :param filename: the full qualified filename (path + file)
        :param fieldnames: a tuple of strings containing the name of all the fields of interest
        :param skip_header: flag indicating to ignore the first row
        :return: The CSV data as an instance of <class 'list'>: [OrderedDict()]
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        extension = os.path.splitext(filename)[1]
        if extension in ('.data', '.txt', '.csv'):
            csv_file = open(filename, 'r')
            csv_reader = csv.DictReader(f=csv_file,
                                        delimiter=cfg.CSV_DELIMITER,
                                        fieldnames=fieldnames)
            csv_data = list()
            if skip_header:
                next(csv_reader)  # This skips the first row of the data file
            try:
                for row in csv_reader:
                    csv_data.append(row)
            except Exception as ex:
                msg = f'csv.DictReader row {csv_reader.line_num} => {ex}'
                logging.error(msg)
                raise ex

        return csv_data

    def write_csv_file(self, data, fieldnames, filename):
        """
        Write a CSV file to the local file system.
        :param data: A dictionary containing the data to be written
        :param fieldnames: a tuple of strings containing the name of all the fields of interest
        :param filename: the full qualified filename (path + file)
        :return: True if the file was written successfully, otherwise False
        """
        msg = f'{self.__class__.__name__}.{sys._getframe().f_code.co_name}'
        logging.info(msg)

        try:
            csv_file = open(filename, 'w')
            csv_writer = csv.DictWriter(f=csv_file,
                                        delimiter=cfg.CSV_DELIMITER,
                                        fieldnames=fieldnames)
            csv_writer.writeheader()
            for rec in data:
                csv_writer.writerow(rec)
            success = True
        except Exception as ex:
            logging.error(ex)
            success = False

        return success

def list_to_string(lst):
    """
    Function to print a list as a better readable formatted string.

    :param lst: a list of tuples List<Tuple>
    :return: a text in format  key1:value1, key2:value2, ...
    """
    text = ''
    for e in enumerate(lst):
        for k, v in e[1].items():
            text = text + '{k}:{v},'.format(k=k, v=v)
        # Replace last ',' with a '\n' character using slicing.
        text = text[:-1] + os.linesep

    return text


def strdate(date):
    """
    :param date: A date like e.g. datetime.datetime.now()
    :return: a formatted date string following the pattern DD.MM.YYYY HH:MM:SS
    """
    return date.strftime('%d.%m.%Y %H:%M:%S')


def message_detail_level():
    """
    Returns the value of the MessageDetailLevel currently set
    :return: cfg.MessageDetailLevel (Currently hard coded to cfg.UI_RESULT_LOG_MSG_DETAIL)
    """
    # TODO: Ideally the message detail level is to be gathered from a new field in the ui
    level = cfg.UI_RESULT_LOG_MSG_DETAIL

    return level
