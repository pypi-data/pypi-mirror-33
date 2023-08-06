# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import math

import terminaltables
from textwrap import wrap
from builtins import str as text

from cis_client.commands import utils


def get_terminal_size():
    try:
        rows, columns = os.popen('stty size', 'r').read().split()
    except Exception as e:
        # FIXME tmp decission for windows or other...
        return (60, 120)
    return (int(rows), int(columns))


def print_json_as_table(data, header_field_map=None, order_fields=None, wrap_text=True,
                        inner_row_border=True,
                        inner_heading_row_border=True,
                        not_print_header=False):
    rows, cols = get_terminal_size()
    keys = set()
    for row in data:
        row_keys = row.keys()
        keys.update(row_keys)
    ordered_keys = order_fields or keys
    cols_len = len(ordered_keys)
    col_width = math.floor(cols/cols_len)
    rows_data = []
    for row in data:
        row_data = []
        for key in ordered_keys:
            field_data = text(row.get(key))
            # do not wrap 'id' column because we usually must copy it from terminal
            if key == 'id':
                wrapped_string = field_data
            else:
                wrapped_string = '\n'.join(wrap(field_data, int(col_width), replace_whitespace=False)) if wrap_text else field_data
            row_data.append(wrapped_string)
        rows_data.append(row_data)

    # replace table fields with user friendly fields in header
    if header_field_map:
        ordered_keys = map(lambda field_name: header_field_map.get(field_name, field_name), ordered_keys)

    table_data = [] if not_print_header else [list(ordered_keys)]
    table_data.extend(rows_data)
    table = terminaltables.AsciiTable(table_data)

    table.inner_row_border = inner_row_border
    table.inner_heading_row_border = inner_heading_row_border
    utils.display(table.table)
