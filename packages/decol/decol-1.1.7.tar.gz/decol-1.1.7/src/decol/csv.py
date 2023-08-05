from __future__ import absolute_import
import csv
import os
from .util import dslice

def select(col_select, head_select, input_sep, output_sep, keep, input, output):
    """Drop or keep selected columns of a CSV file."""
    reader = csv.reader(input, delimiter=str(input_sep))
    try:
        header_fields = next(reader)
    except StopIteration:
        return

    colnum = len(header_fields)
    columnsi0 = []  # zero-based column indexes

    if head_select:
        header_lookup = dict((h, i) for i, h in enumerate(header_fields))
        for h in head_select:
            try:
                columnsi0.append(header_lookup[h])
            except KeyError:
                pass
    elif col_select:
        # column indexes come from user as 1-based
        # - convert to 0-based indexing
        # - adjust negative indices
        # - check range
        for c in col_select:
            if c > 0 and c <= colnum:
                columnsi0.append(c - 1)
            elif c < 0 and c >= -colnum:
                columnsi0.append(c + colnum)
        columnsi0 = [c for c in columnsi0 if c < colnum]

    if not keep:
        columnsi0 = [c for c in range(colnum) if c not in columnsi0]

    if columnsi0:
        if output_sep is None:
            output_sep = input_sep
        writer = csv.writer(output, delimiter=str(output_sep), lineterminator=os.linesep)
        writer.writerow(dslice(header_fields, columnsi0))
        for row in reader:
            writer.writerow(dslice(row, columnsi0))
