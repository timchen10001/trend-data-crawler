from utils import *
from time import time
from Stock import Stock
from merge import merge_day, merge_month, merge_week

class SVI_CLI:
    def __init__(self, config):
        self.config = config
        self._state_init()

    def _state_init(self):
        self.geo = self.config['geo'][0]
        self.week = self.config['week'][0]
        self.day = self.config['day'][0]
        self.month = self.config['month'][0]
        self.cross_year = self.config['cross_year'][0]
        self.all_year_range = self.config['all_year_range'][0]
        self.columns_name = self.config['table.columns_name'][0]
        self.pspam = self.config['prevent_spamming'][0]

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
            merge_week(sequence_type='none-cross', new_folder='merged', cn=self.columns_name)
        if self.cross_year:
            merge_week(sequence_type='cross-year', new_folder='merged', cn=self.columns_name)
        if self.day:
            merge_day(new_folder='merged', table_type='single-column', sequence_type='none-cross', cn=self.columns_name)
        if self.month:
            merge_month(new_folder='merged', cn=self.columns_name)

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

        if self.day: self.day = bool_dt_map['day']
        if self.week: self.week = bool_dt_map['week']
        if self.cross_year: self.cross_year = bool_dt_map['cross_year']
        if self.month: self.month = bool_dt_map['month']



    def google_trend_cli(self):
        geo = '' if self.geo == 'Global' else self.geo
        qs = input('\n----- 趨勢關鍵字(群)： 例如 google、股票代號 -----\n').split()

        t_start = time()
        for q in qs:
            q = q.replace('-', ' ')

            if self.pspam:
                self.check_duplication(q=q)

            tt_st = time()
            stock_google_trend = Stock(
                q=q,
                dr=self.y_range,
                dev=False,
                day=self.day,
                week=self.week,
                month=self.month,
                cross_year=self.cross_year,
                geo=geo)
            stock_google_trend.main()
            tt_ed = time()
            print(f'{q} 耗時約 {int(tt_ed-tt_st)}s')
        t_end = time()
        print(f'\n總計耗時約 {int(t_end-t_start)}s')

        self.save()

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