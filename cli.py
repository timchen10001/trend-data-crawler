from utils import *
from time import time
from GoogleTrend import GoogleTrend
from time import sleep
from merge import merge_day, merge_week

def google_trend_cli(geo:str, daily:str):
    geo = '' if geo == 'Global' else geo
    qs = input('\n-----請輸入要搜索的關鍵字： 例如 google facebook-----\n').split()
    y_range = [2004, valid_year_at_most(daily=daily, output_type='int')]
    y_start: int
    y_end: int
    if input('\n-----是否爬取全部資料？ 是(y) / 否(n)-----\n') in 'yY':
        year_at_most_default = default_at_most(daily=daily)
        y_start = year_at_most_default[0]
        y_end = year_at_most_default[1]
    else:
        while True:
            y_start = valid_number(input('\n-----請輸入起始年份： (2004 require at least)   -----\n'), output_type='int')
            if is_valid_year(y_range, y_start): break
            else: print(f'\n!!! 起始年份必須介於 {y_range[0]} ~ {y_range[1]}之間')
        while True:
            y_end = valid_number(input(f'\n請輸入結尾年份： ({y_range[1]} require at most)\n'),     output_type='int')
            if is_valid_year(y_range, y_end): break
            else: print(f'\n!!! 結尾年份必須介於 {y_range[0]} ~ {y_range[1]}')


    t_start = time()
    for q in qs:
        q = q.replace('-', ' ')
        print(f'\n開始抓取 {q} ···')
        tt_st = time()
        google_trend = GoogleTrend(q, [y_start, y_end], dev=True, daily=daily, geo=geo)
        google_trend.main()
        tt_ed = time()
        print(f'{q} 耗時約 {int(tt_ed-tt_st)}s')
    t_end = time()
    print(f'\n總計耗時約 {int(t_end-t_start)}s')
    return input('-----繼續 (y) / 結束 (n)-----\n') in 'yY'

def taiwan_stock_cli():
    print(f'\n-----{datetime.now()}-----')
    print('\n-----若要背景執行大量資料爬蟲，請將系統 *螢幕保護 或 *休眠關閉，否則可能造成資訊中斷而損失資料-----')
    dot()
    geo = 'TW' if str(
        input('\n-----搜索區域：預設台灣(y) / 更改區域(n)-----\n')
    ) in 'yY' else str(
        input('-----請輸入區域英文縮寫 (全球: Global, 其他地區自行估狗)-----\n')
    )
    daily = bool(input('\n-----是否需要日資料? (y/n)-----\n') in 'yY')
    while True:
        if not google_trend_cli(geo=geo, daily=daily): break

    merge_week(sequence_type='none-cross', geo=geo, new_folder='merged')
    merge_week(sequence_type='cross-year', geo=geo, new_folder='merged')
    if daily: merge_day(new_folder='merged')
    print('系統將在 2 秒後自動關閉視窗，或是手動點擊右上角離開視窗 ···')
    sleep(1)

def create_config():
    return True

def dot():
    d = '·'
    for i in range(3):
        print(f'\r{d}', end='')
        d += '·'
        sleep(1.5)