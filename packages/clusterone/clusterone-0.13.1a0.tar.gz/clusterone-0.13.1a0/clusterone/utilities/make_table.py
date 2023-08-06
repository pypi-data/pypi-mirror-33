""" blah blah blah
"""

from clusterone.utils import render_table

def main(_data, header=None):
    """
    ???
    """
    #TODO: Pull the code from render_table here and refactor it, then test


    # Otherwise the table would broke
    assert len(header) == len(_data[0])

    table_data = [header] + [row for row in _data]

    table = render_table(table_data, 70).table
    return table

