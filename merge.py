import os
from Resolvers import PathResolver
import pandas as pd
from time import sleep
from datetime import datetime
from numpy import median, array
from utils import *


def merge_main_df(
    file_path_list: list,
    folder: str,
    new_folder: str,
    cn: list,
    mr:int,
    sequence_type: str = 'none-cross',
    data_type: str = 'day',
):
    data = []
    adjust_data = []
    date = []
    index = []
    index_tw = []
    median_list = []

    for f_p in file_path_list:
        csv = pd.read_csv(f_p)

        key_map = list(csv.columns)
        name = key_map[0]
        key = key_map[1]

        # treat data
        col = tidy_array(data=csv[key])

        if not isSameType(element_list=col, dtype=type(1)):
            print('\n')
            raise Exception(f'\n  型別錯誤\n  可能原因：{name} {key} 之原始資料被不明原因更動\n  解決辦法：請確認該原始資料的數據型態是否一致')

        with_adj_col = data_type == 'week' or data_type == 'month'
        adjust_col = list(array(col)+1) if with_adj_col else None

        # treat date
        row = list(csv[key_map[0]])

        size = len(row)
        size_range = range(size)

        if size == 0:
            os.remove(f_p)
            continue

        # treat keys
        keys = [key for _ in size_range]
        keys_tw = [name for _ in size_range]

        # treat median
        med = None
        if adjust_col:
            med = fill_ommit_with_na(
                size_range=size_range,
                row=row,
                adjust_col=adjust_col,
                sequence_type=sequence_type,
                mr=mr
            )

        data.extend(col)
        date.extend(row)
        index.extend(keys)
        index_tw.extend(keys_tw)
        if adjust_col:
            adjust_data.extend(adjust_col)
            median_list.extend(med)

    df = pd.DataFrame()
    df[cn[0]] = index
    df[cn[1]] = index_tw
    df[cn[2]] = date
    df[cn[3]] = data
    if adjust_data:
        df[cn[4]] = adjust_data
        df[cn[5]] = median_list
        df[cn[6]] = toMapOmitValue(datas=adjust_data, medians=median_list)
    return df.set_index(cn[0])


def fill_ommit_with_na(
    size_range:list,
    row:list,
    adjust_col: list,
    sequence_type: str,
    mr:int
):
    med = []
    if sequence_type == 'none-cross':
         year = None
         c = 0
         for i in size_range:
             y = row[i].split('-')[0]
             if y != year:
                 year = y
                 c = 0
             if c < mr:
                 med.append('NA')
             else:
                 median_ = median(adjust_col[i-mr: i])
                 med.append(median_)
             c += 1
    elif sequence_type == 'cross-year':
        c = 0
        month = '06'
        reset = False
        for i in size_range:
            m = row[i].split('-')[1]
            if m == '07' and month == '06':
                c = 0
            if c < mr:
                median_ = 'NA'
            else:
                median_ = median(adjust_col[i-mr: i])
            med.append(median_)
            month = m
            c += 1
    elif sequence_type == 'month':
        c = 0
        for i in size_range:
            if c < mr:
                med.append('NA')
            else:
                median_ = median(adjust_col[i-mr: i])
                med.append(median_)
            c += 1
    return med


def merge_day(
    new_folder: str,
    sequence_type: str,
    table_type: str,
    cn: list,
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
            cn=cn,
            data_type='day',
            mr=8
        )
        pr.push_back(new_folder)
        pr.mkdir()
        pr.push_back(f'{folder}.csv')
        write_path = pr.path()
        df = df.fillna('NA')
        df.to_csv(write_path, encoding='utf-8-sig')
        print(f'\n日資料 合併完成 !')
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
    df.to_csv(write_path, encoding='utf-8-sig')
    print(f'日資料 合併完成 !\n')


def merge_week(
    sequence_type: str,
    new_folder: str,
    cn: list,  # columns_name
    mr:int
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

    df = merge_main_df(file_path_list=file_path_list, folder=folder,
                       new_folder=new_folder, cn=cn, sequence_type=sequence_type, data_type='week', mr=mr)
    pr.push_back(new_folder)
    pr.mkdir()
    pr.push_back(f'{folder}.csv' if sequence_type ==
                 'none-cross' else f'{folder} (cross-year).csv')
    write_path = pr.path()
    df.to_csv(write_path, encoding='utf-8-sig')
    print(f'\n{"" if sequence_type == "none-cross" else "(跨年)"}週資料 合併完成 !')

def merge_month(
    new_folder: str,
    cn: list,  # columns_name
    mr:int
):
    folder = 'month'
    pr = PathResolver(['data', folder], mkdir=True)
    src_path = pr.path()
    pr.pop_back(times=1)

    files_name_list = []
    for file in os.listdir(path=src_path):
        files_name_list.append(file)

    pr.push_back(node=folder)
    file_path_list = pr.push_ret_pop(nodes=files_name_list)
    pr.pop_back()

    df = merge_main_df(file_path_list=file_path_list, folder=folder,
                       new_folder=new_folder, cn=cn, data_type='month', sequence_type='month', mr=mr)

    pr.push_back(new_folder)
    pr.mkdir()
    pr.push_back(f'{folder}.csv')
    write_path = pr.path()
    df.to_csv(write_path, encoding='utf-8-sig',)
    print(f'\n月資料 合併完成 !')
