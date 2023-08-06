from __future__ import print_function, absolute_import, division
import math

from .uierrors import UIErrorWrapper, UITermError

try:
    from shutil import get_terminal_size
except ImportError:
    from backports.shutil_get_terminal_size import get_terminal_size

_test_entries = ['Alpha', 'Bravo', 'Charlie', 'Delta', 'Echo', 'Foxtrot', 'Golf', 'Hotel', 'India',
                 'Juliet', 'Kilo', 'Lima', 'Mike', 'November', 'Oscar', 'Papa', 'Quebec', 'Romeo',
                 'Sierra', 'Tango', 'Unicorn', 'Victor', 'Whiskey', 'X-ray', 'Yankee', 'Zulu']


def print_in_columns(entries, buffer_chars=4, fixed_width_columns=False, column_major=True):
    """
    Given a list of entries, print them in columns across the terminal

    This function will try to evenly divide the given list of entries into columns across the current terminal.
    By default, it will left-align each column and put at least 4 spaces between each column. Successive entries
    will be printed in columns by default.

    :param entries: the list of entries to print, as strings
    :type entries: list of str

    :param buffer_chars: optional, the minimum number of spaces required between columns, i.e. the number of spaces
        that will follow the longest entry in that column. Default is 4.
    :type buffer: int

    :param fixed_width_columns:  optional, controls whether all columns have the same width (``True``) or different
        widths as long as the number of ``buffer_chars`` is maintained (``False``). Default is ``False``.
    :type fixed_width_columns: bool

    :param column_major: optional, controls whether successive elements are printed along columns (``True``) or rows
        (``False``). Default is ``True``.
    :type column_major: bool

    :return: None
    """
    n_term_col = get_terminal_size().columns
    max_entry_length = _max_len(entries) + buffer_chars
    n_entry_col = n_term_col // max_entry_length

    def make_rows(n_columns, col_width):
        """
        Place the individual entries into rows
        :param n_columns: the starting number of columns to divide them into, this should be a small enough
            number that each row is guaranteed to be smaller than the terminal width
        :param col_width: how wide, in characters, the columns should be. This should be the maximum number
            of characters required for the widest column.
        :return: a list of lists, representing the rows.
        """
        # this will be set the first time through the loop so that once we create a row that is too long
        # we fall back to the last short enough set of rows
        last_rows = None
        # Calculating the necessary number of rows first, then the number of elements per row second will
        # put as close to equal numbers of entries in each row to start as possible.
        n_rows = int(math.ceil(len(entries) / n_columns))
        n_per_row = int(math.ceil(len(entries) / n_rows))
        while True:
            rows = []
            if not column_major:
                # If we want successive entries to go across the screen, then down, each row can just be the
                # next n_per_row block of entries
                for i in range(0, len(entries), n_per_row):
                    j = min(i + n_per_row, len(entries))
                    sub_list = entries[i:j]
                    this_row = []
                    for c, val in enumerate(sub_list):
                        this_row.append(_pad_string(val, col_width))
                    rows.append(this_row)

            else:
                # If we want successive entries to go down the screen first, then across, we need to construct
                # the row by taking every n_per_row'th entry
                for r in range(0, n_rows):
                    sub_list = [entries[i_r] for i_r in range(r, len(entries), n_rows)]
                    this_row = [_pad_string(val, col_width) for c, val in enumerate(sub_list)]
                    rows.append(this_row)

            if fixed_width_columns:
                # fixed_width_columns means that every column must be kept to the same width, which will be the
                # maximum required width. In that case, we've already found the optimal distribution of elements
                # on the screen.
                return rows

            # If not using fixed width columns, then we'll try to find the optimal number of entries per
            # line by shrinking the columns, then adding one element to each row and seeing if that exceeds
            # the terminal width
            rows = shrink_cols(rows)
            longest_row_length = _max_len(join_rows(rows))
            if longest_row_length > n_term_col:
                if last_rows is None:
                    UIErrorWrapper.raise_error(UITermError('The initial column spacing resulted in a row wider than the terminal'))
                else:
                    return last_rows
            else:
                last_rows = rows
                if column_major:
                    n_rows -= 1
                    if n_rows <= 0:
                        return rows
                else:
                    n_per_row += 1

    def rows_to_columns(rows):
        cols = []
        max_n_per_row = _max_len(rows)
        for i in range(max_n_per_row):
            this_col = [row[i] for row in rows if len(row) > i]
            cols.append(this_col)
        return cols

    def columns_to_rows(columns):
        rows = []
        n_rows = _max_len(columns)
        for r in range(n_rows):
            rows.append([col[r] for col in columns if len(col) > r])
        return rows

    def shrink_cols(rows):
        columns = rows_to_columns(rows)
        for col in columns:
            width = _max_len(col, prefxn=lambda x: x.rstrip()) + buffer_chars
            for i, val in enumerate(col):
                col[i] = _pad_string(val.rstrip(), width)
        return columns_to_rows(columns)

    def join_rows(rows):
        return [''.join(r) for r in rows]

    all_rows = make_rows(n_entry_col, max_entry_length)

    for row in join_rows(all_rows):
        print(row)


def _max_len(values, prefxn=lambda x: x):
    return max([len(prefxn(v)) for v in values])


def _pad_string(s, length):
    return s + ' '*(length - len(s))
