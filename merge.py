import os
from Resolvers import PathResolver
import pandas as pd
from time import sleep
from datetime import datetime
from numpy import median, array
from utils import toMapOmitValue

# 取得遺漏年份補集合
def get_com_set(years: list, at_most: int):
    com_set = []
    for y in range(2004, at_most+1):
        if not str(y) in years:
            com_set.append(str(y))
    return com_set


def merge_day(
    new_folder: str,
    sequence_type: str,
    table_type: str,
    cn: list
):
    folder = 'day'
    cur_year = datetime.now().year

    pr = PathResolver(['data', folder], mkdir=True)
    src_path = pr.path()
    pr.pop_back(times=1)

    files_name_list = os.listdir(path=src_path)

    pr.push_back(node=folder)
    file_path_list = pr.push_ret_pop(nodes=files_name_list)
    pr.pop_back()

    if table_type == 'single-column': 
        df = merge_main_df(
            file_path_list=file_path_list, 
            folder=folder,
            new_folder=new_folder,
            cn=cn
        )
        pr.push_back(new_folder)
        pr.mkdir()
        pr.push_back(f'{folder}.csv' if sequence_type ==
                     'none-cross' else f'{folder} (cross-year).csv')
        write_path = pr.path()
        df.to_csv(write_path)
        print(f'\n({"非跨年" if sequence_type == "none-cross" else "跨年"}) 日資料 合併完成 !')
        return 
            
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


def merge_week(
    sequence_type: str,
    geo: str,
    new_folder: str,
    cn: list,  # columns_name
):
    folder = 'week'
    pr = PathResolver(['data', folder], mkdir=True)
    src_path = pr.path()
    pr.pop_back(times=1)

    files_name_list = []
    for file in os.listdir(path=src_path):
        if sequence_type == 'cross-year' and 'cross-year' in file:
            files_name_list.append(file)
        elif sequence_type == 'none-cross' and not 'cross-year' in file:
            files_name_list.append(file)

    pr.push_back(node=folder)
    file_path_list = pr.push_ret_pop(nodes=files_name_list)
    pr.pop_back()
    
    df = merge_main_df(file_path_list=file_path_list, folder=folder, new_folder=new_folder, cn=cn)
    pr.push_back(new_folder)
    pr.mkdir()
    pr.push_back(f'{folder}.csv' if sequence_type ==
                 'none-cross' else f'{folder} (cross-year).csv')
    write_path = pr.path()
    df.to_csv(write_path)
    print(f'\n({"非跨年" if sequence_type == "none-cross" else "跨年"}) 週資料 合併完成 !')


def merge_main_df(file_path_list: list, folder: str, new_folder: str, cn: list):
    data = []
    adjust_data = []
    date = []
    index = []
    index_tw = []
    median_list = []

    for f_p in file_path_list:
        csv = pd.read_csv(f_p)

        key_map = list(csv.columns)
        key = key_map[1]
        name = key_map[0]

        # treat data
        col = csv[key]
        adjust_col = list( array(col)+1 )

        # treat date
        row = csv[list(csv.columns)[0]]

        size = len(row)

        if size == 0:
            os.remove(f_p)
            continue

        # treat keys
        keys = [key for _ in range(size)]
        keys_tw = [name for _ in range(size)]

        # treat median
        med = []
        for i in range(len(col)):
            if i < 8:
                med.append('NA')
            else:
                medi = median(adjust_col[i-8: i])
                med.append(medi)

        data.extend(col)
        adjust_data.extend(adjust_col)
        date.extend(row)
        index.extend(keys)
        index_tw.extend(keys_tw)
        median_list.extend(med)

    df = pd.DataFrame()
    df[cn[0]] = index
    df[cn[1]] = index_tw
    df[cn[2]] = date
    df[cn[3]] = data
    df[cn[4]] = adjust_data
    df[cn[5]] = median_list
    df[cn[6]] = toMapOmitValue(datas=data, medians=median_list)
    df = df.set_index(cn[0])
    return df