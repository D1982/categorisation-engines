""" Common utilities

Basic utilities e.g. for dealing with files (data, JSON).
Working With JSON Data in Python: https://realpython.com/python-json/

"""
import Categorisation.Common.config as cfg

import csv
import json
import os.path


class FileHandler:

    def read_json_file(self, filename):
        extension = os.path.splitext(filename)[1]
        if extension == '.json':
            with open(filename) as json_data:
                json_dict = json.load(json_data)
        return json_dict

    def write_json_file(self, json_data, filename):
        jsonfile = open(filename, 'w')
        json.dump(json_data, jsonfile)
        jsonfile.write('\n')

    def read_csv_file(self, filename, fieldnames, skip_header=True):
        extension = os.path.splitext(filename)[1]
        if extension == '.data' or extension == '.txt':
            csvfile = open(filename, 'r')
            csvreader = csv.DictReader(csvfile, delimiter=cfg.CSV_DELIMITER, fieldnames=fieldnames)
            csv_data = []
            if skip_header == True:
                next(csvreader)  # This skips the first row of the data file
            for row in csvreader:
                csv_data.append(row)
        return csv_data

    def write_csv_file(self, data, fieldnames, filename):
        csvfile = open(filename, 'w')
        csvwriter = csv.DictWriter(csvfile, delimiter=cfg.CSV_DELIMITER, fieldnames=fieldnames)
        csvwriter.writeheader()
        for rec in data:
            csvwriter.writerow(rec)
