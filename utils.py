from random import randint
import os
from shutil import rmtree
from platform import system
from datetime import datetime
from numpy import log
from Resolvers import PathResolver, path_separate
from inputimeout import inputimeout, TimeoutOccurred
from time import sleep

def rd_ms():
    return randint(1, 2)


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


def valid_number(ss: str, output_type: str = 'int'):
    valid_int = [str(i) for i in range(10)]
    valid_ss = ''
    for s in ss:
        if s in valid_int:
            valid_ss += s
    return valid_ss if output_type == 'str' else int(valid_ss)


def is_valid_year(y_r: list, year: int) -> (bool):
    if len(y_r) != 2:
        raise Exception('the length in year_range must be 2')
    return (year >= y_r[0] and year <= y_r[1])


def valid_year_at_most(daily: bool, output_type: str = 'int'):
    y = datetime.now().year
    if daily:
        return y-1 if output_type == 'int' else str(y-1)
    return y if output_type == 'int' else str(y)


def default_at_most(daily: bool):
    y = datetime.now().year
    if daily:
        return [2004, y-1]
    return [2004, y]

def today_folder_name():
    now = datetime.now()
    y = iTs(now.year)
    m = iTs(now.month)
    d = iTs(now.day)
    return y + m + d

# nature log
def ln(num: float) -> (float):
    return log(num)

def try_except(key, _map, default):
    try:
        return _map[key]
    except:
        return default

# file exist check
def already_exist(q:str, data_type:str):
    is_cross = data_type == 'cross_year'

    data_type = 'week' if is_cross else data_type
    data_path = PathResolver(['data', data_type], mkdir=True).path()
    for file_name in os.listdir(data_path):
        if is_cross:
            if f'{q} (cross-year).csv' == file_name:
                return True
        else:
            if f'{q}.csv' == file_name:
                return True
    return False


# merge
# 取得遺漏年份補集合
def get_com_set(years: list, at_most: int):
    com_set = []
    for y in range(2004, at_most+1):
        if not str(y) in years:
            com_set.append(str(y))
    return com_set


def tidy_array(data):
    tidy = []
    for ele in data:
        s_ele = str(ele)
        if s_ele == 'NA' or s_ele == 'NaN' or s_ele == 'nan':
            tidy.append('NA')
        else:
            tidy.append(ele)
    return tidy


def toMapOmitValue(datas: list, medians: list) -> (list):
    adjust = []
    for d, m in zip(datas, medians):
        asvi = 0
        if d == 'NA' or m == 'NA':
            asvi = "NA"
        elif d == 0 and m == 0:
            asvi = 0
        elif d == 0 and m != 0:
            asvi = 0 - ln(m)
        elif d != 0 and m == 0:
            asvi = ln(d) - 0
        else:
            asvi = ln(d) - ln(m)
        adjust.append(asvi)
    return adjust

def not_spamming_server(q: str, timeout_default: bool, timeout: int=10) -> (bool):
    try:
        prompt = f'\n----- {q} 已存在，繼續擷取 ? 爬(y) / 不爬(n) -----\n'
        something = bool(not inputimeout(prompt=prompt, timeout=timeout) in 'yY')
    except TimeoutOccurred:
        something = timeout_default
        print(f'{"y" if something else "n"}')
    return bool(something)

def dot(s: float):
    d = '·'
    for i in range(3):
        c = f'\r{d}'

        print(c, end='')
        d += '·'
        sleep(s)
    print(' ', end='')