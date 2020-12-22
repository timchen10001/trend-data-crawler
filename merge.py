import os
from Resolvers import PathResolver
import pandas as pd
from time import sleep
from datetime import datetime
from numpy import median

# 取得遺漏年份補集合
def get_com_set(years: list, at_most: int):
    com_set = []
    for y in range(2004, at_most+1):
        if not str(y) in years:
            com_set.append(str(y))
    return com_set


def merge_day(new_folder: str):
    folder = 'day'
    cur_year = datetime.now().year

    pr = PathResolver(['data'])

    src_path = pr.push_ret_pop(folder)
    files_name_list = os.listdir(path=src_path)

    pr.push_back(node=folder)
    file_path_list = pr.push_ret_pop(nodes=files_name_list)
    pr.pop_back()

    columns = {}
    date = []
    index = []
    at_most = cur_year if folder != 'day' else cur_year-1
    date_name = 'M/D' if folder == 'day' else 'Y/M/D'

    # 初始化 hash map
    for y in range(2004, at_most+1):
        columns[f'{y}'] = []

    for f_p, f_name in zip(
        file_path_list,
        files_name_list
    ):
        csv = pd.read_csv(f_p)
        key = f_name.split('.')[0]
        col = list(csv.columns)[1:]
        row = csv[date_name]
        keys = [key for _ in range(len(row))]

        if len(row) == 0:
            os.remove(f_p)
            continue

        sub = get_com_set(years=col, at_most=at_most)
        for y in sub:
            csv[f'{y}'] = [0 for _ in range(0, 366)]
            columns[f'{y}'].extend(csv[f'{y}'])

        for y in col:
            y = str(y)
            columns[y].extend(csv[y])

        date.extend(row)
        index.extend(keys)

    df = pd.DataFrame()
    df[date_name] = date
    for y in range(2004, at_most+1):
        df[f'{y}'] = columns[f'{y}']
    df.index = index

    pr.push_back(new_folder)
    pr.mkdir()
    pr.push_back(f'{folder}.csv')
    write_path = pr.path()
    df.to_csv(write_path)
    print(f'日資料 合併完成 !\n')

def merge_week(geo:str, new_folder: str):
    folder = 'week'
    pr = PathResolver(['data'])

    src_path = pr.push_ret_pop(folder)
    files_name_list = os.listdir(path=src_path)

    pr.push_back(node=folder)
    file_path_list = pr.push_ret_pop(nodes=files_name_list)
    pr.pop_back()

    data = []
    date = []
    index = []
    median_list = []

    date_time = 'Y/M/D' if folder == 'week' else 'M/D'

    for f_p in file_path_list:
        csv = pd.read_csv(f_p)
        key = list(csv.columns)[1]

        # treat data
        col = csv[key]

        # treat date
        row = csv[list(csv.columns)[0]]
        if len(row) == 0: 
            os.remove(f_p)
            continue
        
        # treat keys
        keys = [ key for _ in range(len(row)) ]

        # treat median
        med = []
        for i in range(len(col)):
            if i < 8: 
                med.append('NA')
            else:
                medi = median(col[i-8 : i])
                med.append(medi)

        index.extend(keys)
        data.extend(col)
        date.extend(row)
        median_list.extend(med)

    df = pd.DataFrame()
    df[ 'key' ] = index
    df[ date_time ] = date
    df[ geo ] = data
    df[ 'median' ] = median_list
    df = df.set_index('key')

    pr.push_back(new_folder)
    pr.mkdir()
    pr.push_back(f'{folder}.csv')
    write_path = pr.path()
    df.to_csv(write_path)
    print(f'週資料 合併完成 !\n')