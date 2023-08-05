import os
import _csv
from pandas.io.parsers import read_csv


class ExportCSV:
    def __init__(self, list, file_name):
        # Creates a text file with the full file paths
        self.file_name = file_name
        self.inputList = list

        self.list_to_text()
        csv_name = self.text_to_csv

    def __str__(self):
        return str(os.getcwd()) + str(self.file_name + '.csv')

    def list_to_text(self):
        text = 'list.txt'

        # If no text file exists a text file is created
        try:
            text_file = open(text, "r+")
        except IOError:
            text_file = open(text, "w")

        # text_file contents of text file
        text_file.truncate()

        # For each file in inputList a new line is written
        # */* is replaced with *,* to convert to csv (except first character of line)
        for row in self.inputList:
            if type(row) is not None:
                if type(row) == str:
                    modifiedstr = row.replace('/', ',') + '\n'
                elif type(row) == list:
                    modifiedstr = str(row)
                    modifiedstr = modifiedstr[1:len(modifiedstr) - 1] + '\n'
                    modifiedstr = modifiedstr.replace("'", '')
                elif type(row) == tuple:
                    modifiedstr = str(row)
                    modifiedstr = modifiedstr[1:len(modifiedstr) - 1] + '\n'
                    modifiedstr = modifiedstr.replace("'", '')
                text_file.write(modifiedstr)
        text_file.close()

    @property
    def text_to_csv(self):
        # Isolate csv and text name
        csv_name = self.file_name + ".csv"
        text = 'list.txt'

        # If file exists, remove
        if os.path.isfile(csv_name):
            os.remove(csv_name)
        csv_file = csv_name

        try:
            csv_file = open(csv_file, "r+")
        except IOError:
            csv_file = open(csv_file, "w")
        # Write each line of text file to csv
        in_txt = _csv.reader(open(text, "rb"), delimiter=',')
        out_csv = _csv.writer(csv_file)
        out_csv.writerows(in_txt)
        os.remove(text)
        return str(os.getcwd()) + str(csv_name)


def csv_to_list(csv_file):
    with open(csv_file, 'rb') as f:
        reader = _csv.reader(f)
        your_list = list(reader)
        return your_list


def remove_empty_cols(csv_file):
    data = read_csv(csv_file)
    filtered_data = data.dropna(axis='columns', how='all')
    filtered_data.to_csv(csv_file)
