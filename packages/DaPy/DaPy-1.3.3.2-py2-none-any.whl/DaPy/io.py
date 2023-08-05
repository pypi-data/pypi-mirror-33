from os import path
from core import DataSet

def read(addr, dtype='col', sheet_name=None, miss_symbol='', miss_value=None, sep=None,
            first_line=1, title_line=0, prefer_type=bool):
    data = DataSet()
    data.read(addr, dtype, sheet_name, miss_symbol, miss_value, sep, first_line,
              title_line, prefer_type)
    return data

def encode(code='cp936'):
    import sys
    stdi, stdo, stde = sys.stdin, sys.stdout, sys.stderr
    reload(sys)
    sys.stdin, sys.stdout, sys.stderr = stdi, stdo, stde
    sys.setdefaultencoding(code)
    return

