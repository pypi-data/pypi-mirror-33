""" Analysis of CSV files containing time and several signals values. """
from appteka.timestamps import TimeConverter


def get_delimiter(file_name, encoding='utf-8'):
    """ Attempt to detect delimiter (';' or ',') and return it. """
    with open(file_name, encoding=encoding) as buff:
        first_line = buff.readline()
    if ';' in first_line:
        delimiter = ';'
    else:
        delimiter = ','
    return delimiter


def get_head(file_name, delimiter=';', nlines=100, encoding='utf-8'):
    """ Return the first n lines of CSV file as table. """
    head = []
    with open(file_name, encoding=encoding) as buff:
        for i in range(nlines):
            row = buff.readline()
            if row == '':
                break
            row = row.replace('\n', '')
            row_splitted = row.split(delimiter)
            head.append(row_splitted)
    return head


def get_time_converter(head):
    """ Return the TimeConverter object. """
    converter = TimeConverter()
    list_of_ts = []
    for row in head[1:]:
        list_of_ts.append(row[0])
    if not converter.learn(list_of_ts):
        return None
    return converter


def get_rate(head, time_converter):
    """ Return sample rate. """
    time_1 = time_converter.convert(head[1][0])
    time_2 = time_converter.convert(head[2][0])
    rate = 1.0 / (time_2 - time_1)
    return rate
