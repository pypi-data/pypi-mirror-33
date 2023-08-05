import os
import csv
from pandas.io.parsers import read_csv
from pandas import DataFrame


class ExportCSV:
    def __init__(self, list, file_name, cols):
        # Creates a text file with the full file paths
        self.file_name = str(file_name + '.csv')
        self.list = list
        self.cols = cols

        self.list_to_csv()

    def __str__(self):
        return str(os.getcwd()) + str(self.file_name + '.csv')

    def list_to_csv(self):
        df = DataFrame(self.list, columns=self.cols)
        df.to_csv(self.file_name, index=False)


def csv_to_list(csv_file):
    with open(csv_file, 'rb') as f:
        reader = csv.reader(f)
        your_list = list(reader)
        return your_list


def remove_empty_cols(csv_file):
    data = read_csv(csv_file)
    filtered_data = data.dropna(axis='columns', how='all')
    filtered_data.to_csv(csv_file)
