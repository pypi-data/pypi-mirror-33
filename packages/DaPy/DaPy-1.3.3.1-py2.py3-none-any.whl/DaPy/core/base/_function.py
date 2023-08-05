from collections import namedtuple, deque, Iterable, deque
from datetime import datetime
from time import struct_time
from array import array
from os import path
from string import atof, atoi
from distutils.util import strtobool

__all__ = ['_value_types', '_sequence_types', 'get_sorted_index',
           'is_value', 'is_math', 'is_iter', 'is_seq', 'str2value', 'parse_addr']

_value_types = (type(None), int, float, str, long, complex,
                unicode, datetime, struct_time)
_sequence_types = [list, tuple, deque, array, set, frozenset]

try:
    from numpy import ndarray
    _sequence_types.append(ndarray)
except ImportError:
    pass

try:
    from pandas import Series
    _sequence_types.append(Series)
except ImportError:
    pass

_sequence_types = tuple(_sequence_types)
    
def get_sorted_index(seq, cmp=None, key=None, reverse=False):
    index_dict = dict()
    for i, value in enumerate(seq):
        if value in index_dict:
            index_dict[value].append(i)
        else:
            index_dict[value] = [i, ]

    new_value = sorted(index_dict.keys(), cmp, key, reverse)
    new_index = list()
    for value in new_value:
        new_index.extend(index_dict[value])

    if reverse:
        return new_index.reverse()
    return new_index

def is_value(n):
    '''Determine that if a variable is a value

    Return
    ------
    Bool : the result of evaluation.
        True - input is a value
        False - input is not a value
    '''
    if isinstance(n, _value_types):
        return True
    return False

def is_math(n):
    '''Determine that if a variable is a number

    Return
    ------
    Bool : the result of evaluation.
        True - 'n' is a number
        False - 'n' is not a number
    '''
    if isinstance(n, (int, float, long)):
        return True
    return False

def is_iter(obj):
    '''Determine that if a variable is a iterable

    Return
    ------
    Bool
    '''
    try:
        if isinstance(obj, Iterable):
            return True
    except TypeError:
        return False
    else:
        return False

def is_seq(obj):
    ''' Determin that if a variable is a sequence object
    '''
    if isinstance(obj, _sequence_types):
        return True
    return False

def str2value(value, prefer_type=None):
    if prefer_type is str:
        pass
    
    elif value.isdigit() or value[1:].isdigit():
        if isinstance(prefer_type, float):
            return atof(value)
        return atoi(value)
    
    elif value.count('.') == 1:
        return atof(value)

    elif prefer_type is bool:
        try:
            return strtobool(value)
        except ValueError:
            pass
        
    if value[-2:] == '\n':
        return value[:-2]
    return value

def parse_addr(addr):
    file_path, file_name = path.split(addr)
    if file_name.count('.') > 1:
        file_base = '.'.join(file_name.split('.')[:-1])
        file_type = file_name.split('.')[-1]
    else:
        file_base, file_type = file_name.split('.')
    return file_path, file_name, file_base, file_type
