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

        :param filename: the full qualified filename (path + file)
        :return: a dictionary representing the json read from the file
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        extension = os.path.splitext(filename)[1]
        if extension == '.json':
            with open(filename) as json_data:
                json_dict = json.load(json_data)
        return json_dict

    def write_json_file(self, json_data, filename):
        """
        Write a JSON file to the local file system.

        :param json_data: A dictionary containing the data to be written
        :param filename: the full qualified filename (path + file)
        :return:
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        json_file = open(filename, 'w')
        json.dump(json_data, json_file)
        json_file.write('\n')


    def read_csv_file(self, filename, fieldnames, skip_header=True):
        """
        Read a CSV file from the local file system.

        :param filename: the full qualified filename (path + file)
        :param fieldnames: a tuple of strings containing the name of all the fields of interest
        :param skip_header: flag indicating to ignore the first row
        :return: The CSV data as an instance of <class 'list'>: [OrderedDict()]
        """
        extension = os.path.splitext(filename)[1]
        if extension == '.data' or extension == '.txt' or extension == '.csv':
            csvfile = open(filename, 'r')
            csvreader = csv.DictReader(csvfile, delimiter=cfg.CSV_DELIMITER, fieldnames=fieldnames)
            csv_data = []
            if skip_header == True:
                next(csvreader)  # This skips the first row of the data file
            for row in csvreader:
                csv_data.append(row)
        return csv_data

    def write_csv_file(self, data, fieldnames, filename):
        """
        Write a CSV file to the local file system.
        :param data: A dictionary containing the data to be written
        :param fieldnames: a tuple of strings containing the name of all the fields of interest
        :param filename: the full qualified filename (path + file)
        :return:
        """
        logging.debug('{c}.{m}'.format(c=self.__class__.__name__, m=sys._getframe().f_code.co_name))

        csv_file = open(filename, 'w')
        csv_writer = csv.DictWriter(csv_file, delimiter=cfg.CSV_DELIMITER, fieldnames=fieldnames)
        csv_writer.writeheader()
        for rec in data:
            csv_writer.writerow(rec)


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
