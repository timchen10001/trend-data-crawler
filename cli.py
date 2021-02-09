from utils import *
from time import time
from Stock import Stock
from merge import merge_day, merge_month, merge_week
from Error import ErrorResolver
from os import listdir, rename
from Resolvers import PathResolver
from pandas import read_csv

class SVI_CLI:
    def __init__(self, config):
        self.config = config
        self._state_init()

    def _state_init(self):
        self.txt = self.config['txt'][0]
        self.geo = self.config['geo'][0]
        self.week = self.config['week'][0]
        self.day = self.config['day'][0]
        self.month = self.config['month'][0]
        self.cross_year = self.config['cross_year'][0]
        self.all_year_range = self.config['all_year_range'][0]
        self.columns_name = self.config['table.columns_name'][0]
        self.pspam = self.config['prevent_spamming'][0]
        self.mr_w = self.config['median_range.week'][0]
        self.mr_m = self.config['median_range.month'][0]

        self.year_at_most_default = default_at_most(daily=self.day)
        self.set_valid_year_range()




    def set_valid_year_range(self) -> (list):
        yr = self.year_at_most_default
        self.y_range = self.year_at_most_default
        if not self.all_year_range:
            first = yr[0]
            last = yr[1]
            y_start = 0
            y_end = 0
            while True:
                y_start = valid_number(
                    input('\n----- 請輸入起始年份： (2004 require at least) -----\n'), output_type='int')
                if is_valid_year(y_r=yr, year=y_start):
                    break
                else:
                    print(f'\n!!! 起始年份必須介於 {first} ~ {last}之間')
            while True:
                y_end = valid_number(
                    input(f'\n請輸入結尾年份： ({last} require at most)\n'),     output_type='int')
                if is_valid_year(y_r=yr, year=y_end):
                    break
                else:
                    print(f'\n!!! 結尾年份必須介於 {first} ~ {last}')
            self.y_range = [y_start, y_end]


    def save(self):
        if self.week:
            merge_week(sequence_type='none-cross', new_folder='merged', cn=self.columns_name, mr=self.mr_w)
        if self.cross_year:
            merge_week(sequence_type='cross-year', new_folder='merged', cn=self.columns_name, mr=self.mr_w)
        if self.day:
            merge_day(new_folder='merged', table_type='single-column', sequence_type='none-cross', cn=self.columns_name)
        if self.month:
            merge_month(new_folder='merged', cn=self.columns_name, mr=self.mr_m)

    def check_duplication(self, q:str):
        dt_map = {}

        if self.day: dt_map['day'] = "日"
        if self.week: dt_map['week'] = "週"
        if self.cross_year: dt_map['cross_year'] = "跨年(週)"
        if self.month: dt_map['month'] = "月"

        bool_dt_map = {}
        for key in dt_map.keys():
            d = True
            value = dt_map[key]
            if already_exist(q=q, data_type=key):
                qq = f'{q} {value}資料'
                if not_spamming_server(q=qq, timeout_default=True):
                    d = False
            bool_dt_map[f'{key}'] = d

        dt_map['day'] = bool_dt_map['day'] if self.day else False
        dt_map['week'] = bool_dt_map['week'] if self.week else False
        dt_map['cross_year'] = bool_dt_map['cross_year'] if self.cross_year else False
        dt_map['month'] = bool_dt_map['month'] if self.month else False
        return dt_map

    def csv_to_txt(self):
        if not self.txt: return

        interface_pr = PathResolver(nodes=['interface'], mkdir=True)
        data_pr = PathResolver(nodes=['data'])

        data_path = data_pr.path()
        interface_path = interface_pr.path()

        data_folders = listdir(data_path)

        files_cleaner(interface_path)

        for folder in data_folders:
            if folder == 'error': continue

            data_pr.push_back(node=folder)
            interface_pr.push_back(node=folder)
            interface_pr.mkdir()

            path = data_pr.path()

            files = listdir(path=path)
            for f in files:
                p = data_pr.push_ret_pop(f)
                interface_p = interface_pr.push_ret_pop(f)

                df = read_csv(filepath_or_buffer=p)
                df.to_csv(interface_p)
                rename(src=interface_p, dst=interface_p.replace('csv', 'txt'))

            data_pr.pop_back()
            interface_pr.pop_back()

    def google_trend_cli(self):
        geo = '' if self.geo == 'Global' else self.geo
        qs = input('\n----- 趨勢關鍵字(群)： 例如: 2330 或 台積電 -----\n').split()

        t_start = time()
        errors_list = []
        for q in qs:
            origin_q = q.replace('&', ' ')
            q = q.replace('*', '')

            dt_map = {}
            if self.pspam:
                dt_map = self.check_duplication(q=origin_q)

            tt_st = time()
            stock_google_trend = Stock(
                origin_q=origin_q,
                q=q,
                dr=self.y_range,
                dev=False,
                day=try_except(key='day', _map=dt_map, default=self.day),
                week=try_except(key='week', _map=dt_map, default=self.week),
                month=try_except(key='month', _map=dt_map, default=self.month),
                cross_year=try_except(key='cross_year', _map=dt_map, default=self.cross_year),
                geo=geo)
            stock_google_trend.main()
            error_map = stock_google_trend.catch()
            if error_map:
                errors_list.append(error_map)
            tt_ed = time()
            print(f'{q} 耗時約 {int(tt_ed-tt_st)}s')
        t_end = time()
        print(f'\n總計耗時約 {int(t_end-t_start)}s')
        self.save()

        if self.txt:
            self.csv_to_txt()

        if errors_list:
            err = ErrorResolver(error_list=errors_list)
            err.logging()

        return bool(input('\n----- 繼續 (y) / 結束 (n) -----\n') in 'yY')


    def taiwan_stock_cli(self):
        try:
            while True:
                if not self.google_trend_cli(): break
        except:
            print('\n中斷爬蟲中')
            dot(1)
            self.save()

        print('\n----- 系統將在 2 秒後自動關閉視窗，或是手動點擊右上角離開視窗 ··· -----')
        sleep(1)

