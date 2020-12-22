from random import randint
import os
from shutil import rmtree
from platform import system
from datetime import datetime

def rd_ms():
    return randint(1, 3)

def iTs(i: int) -> (str):
    s = ''
    if i < 10:
        s += '0'
    return s + str(i)


def remove_folder(path):
    if os.path.exists(path):
        rmtree(path)
    else:
        raise Exception(f'{path} not exist')

def path_separate():
    plat = system()
    ps = ''
    if plat == 'Windows': ps = '\\'
    else: ps = '/'
    return ps

def is_path(path: str) -> (bool):
    ps = path_separate()
    if ps in path:
        return True
    return False

def files_cleaner(path: str):
    if os.path.isdir(path):
        remove_folder(path)
    if not os.path.isdir(path):
        os.mkdir(path)

def valid_number(ss: str, output_type: str='int'):
    valid_int = [str(i) for i in range(10)]
    valid_ss = ''
    for s in ss:
        if s in valid_int: valid_ss += s
    return valid_ss if output_type == 'str' else int(valid_ss)

def is_valid_year(y_r: list, year: int) -> (bool):
    if len(y_r) != 2:
        raise Exception('the length in year_range must be 2')
    return (year >= y_r[0] and year <= y_r[1])

def valid_year_at_most(daily: bool, output_type: str='int'):
    y = datetime.now().year
    if daily:
        return y-1 if output_type == 'int' else str(y-1)
    return y if output_type == 'int' else str(y)

def default_at_most(daily: bool):
    y = datetime.now().year
    if daily:
        return [2004, y-1]
    return [2004, y]