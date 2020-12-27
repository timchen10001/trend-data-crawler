from utils import *
from time import time
from GoogleTrend import GoogleTrend
from merge import merge_day, merge_week


def google_trend_cli(geo: str, daily: str, y_range: list, pspam: bool):
    geo = '' if geo == 'Global' else geo
    qs = input('\n----- 趨勢關鍵字(群)： 例如 google、股票代號 -----\n').split()

    t_start = time()
    for q in qs:
        q = q.replace('-', ' ')

        if pspam and already_exist(q) and not_spamming_server(q=q, timeout_default=True):
            sleep(1)
            continue

        tt_st = time()
        google_trend = GoogleTrend(
            q=q, dr=y_range, dev=False, daily=daily, geo=geo)
        google_trend.main()
        tt_ed = time()
        print(f'{q} 耗時約 {int(tt_ed-tt_st)}s')
    t_end = time()
    print(f'\n總計耗時約 {int(t_end-t_start)}s')
    return input('----- 繼續 (y) / 結束 (n) -----\n') in 'yY'


def taiwan_stock_cli(
    geo: str,
    daily: bool,
    all_year_range: bool,
    columns_name: list,
    pspam: bool,
    sleep_time: float = 1.0
):
    # valid range
    y_range = [2004, valid_year_at_most(daily=daily, output_type='int')]

    year_at_most_default: list

    # All data ?
    if all_year_range:
        year_at_most_default = default_at_most(daily=daily)
        y_start = year_at_most_default[0]
        y_end = year_at_most_default[1]
    else:
        while True:
            y_start = valid_number(
                input('\n----- 請輸入起始年份： (2004 require at least) -----\n'), output_type='int')
            if is_valid_year(y_range, y_start):
                break
            else:
                print(f'\n!!! 起始年份必須介於 {y_range[0]} ~ {y_range[1]}之間')
        while True:
            y_end = valid_number(
                input(f'\n請輸入結尾年份： ({y_range[1]} require at most)\n'),     output_type='int')
            if is_valid_year(y_range, y_end):
                break
            else:
                print(f'\n!!! 結尾年份必須介於 {y_range[0]} ~ {y_range[1]}')
        year_at_most_default = [y_start, y_end]

    while True:
        if not google_trend_cli(geo=geo, daily=daily, y_range=year_at_most_default, pspam=pspam):
            sleep(sleep_time)
            break

    merge_week(sequence_type='none-cross', geo=geo,
               new_folder='merged', cn=columns_name)
    merge_week(sequence_type='cross-year', geo=geo,
               new_folder='merged', cn=columns_name)
    if daily:
        merge_day(new_folder='merged', table_type='single-column',
                  sequence_type='none-cross', cn=columns_name)

    print('\n----- 系統將在 2 秒後自動關閉視窗，或是手動點擊右上角離開視窗 ··· -----')
    sleep(1)

