# encoding: utf-8

import json
import logging_helper
from openpyxl import load_workbook

logging = logging_helper.setup_logging()


def get_col_dicts(worksheet):

    rows = [row for row in worksheet.rows]
    if not rows:
        return []

    keys = [cell.value for cell in rows.pop(0)]

    return [{k: v for k, v in zip(keys, [cell.value for cell in row])}
            for row in rows]


def get_col_lists(worksheet,
                  header_row=0):

    rows = [row for row in worksheet.rows]
    if not rows:
        return []
    row_count = len(rows)
    col_count = max([len(row) for row in rows])

    columns = [[None for _ in range(row_count)] for _ in range(col_count)]
    for row_num, row in enumerate(rows):
        for col_num, cell in enumerate(row):
            columns[col_num][row_num] = cell.value

    col_dicts = {col[header_row]: col[header_row+1:]
                 for col in columns
                 if col[header_row] is not None}

    return col_dicts


def workbook_to_json(filename):
    workbook = load_workbook(filename=filename,
                             read_only=True)

    dictionary = {worksheet: get_col_dicts(workbook[worksheet])
                  for worksheet in workbook.get_sheet_names()}

    dictionary = {worksheet: items
                  for worksheet, items in iter(dictionary.items())
                  if items}

    if len(dictionary) > 1:
        return json.dumps(dictionary)
    return json.dumps(list(dictionary.values())[0])
