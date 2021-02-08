from GoogleTrend import GoogleTrend
from utils import default_at_most, files_cleaner, iTs, rd_ms
from time import sleep
from Resolvers import DataResolver, PathResolver
from pandas.core.frame import DataFrame
from pandas.io.parsers import read_csv
from datetime import datetime

class Stock(GoogleTrend):
    def async_init_driver(self, url: str):
        try:
            self.driver.get(url)
        except:
            raise Exception('\n網路狀況不太好，伺服器回應超時···\n')

    def scrapping_per_week(self):
        geo_query = f'&geo={self.geo}'

        sequence_type = self.sequence_type
        sy = self.sy
        ey = self.ey

        cy = sy
        while cy <= ey:
            if sequence_type == 'none-cross':
                print(f'\n正在抓取 {self.q} {self.key} {cy}年 週資料···')
                url = f'{self.url}?date={cy}-01-01%20{cy}-12-31&q={self.q}{geo_query}'
                self._toPage(url)
                sleep(1)
                if self._isData():
                    if not self._download(): continue

            elif sequence_type == 'cross-year':
                print(f'\n正在抓取 {self.q} {self.key} {cy}年 跨 {cy+1}年 週資料···')
                url = f'{self.url}?date={cy}-07-01%20{cy+1}-6-30&q={self.q}{geo_query}'
                self._toPage(url)
                sleep(1)
                if self._isData():
                    if not self._download(): continue
            cy += 1

    def merge_per_week(self):
        sy = self.sy
        ey = self.ey
        sequence_type = self.sequence_type

        file_name = ''
        if sequence_type == 'none-cross':
            print(f'\n正在合併 週資料(未跨越年度) ···')
            file_name = f'{self.q}.csv'
        elif sequence_type == 'cross-year':
            print(f'\n正在合併 週資料(跨越年度) ···')
            file_name = f'{self.q} (cross-year).csv'

        data_path = self.data_path_week
        temp_path = self.temp_path
        df = DataFrame()
        i = 1
        cy = sy

        column = []
        index = []
        while cy <= ey:
            f_name = f'{i}.csv'
            if temp_path.isfile(f_name):
                filepath = temp_path.push_ret_pop(f_name)
                csv = read_csv(filepath_or_buffer=filepath)
                data = csv['類別：所有類別'][1:]
                column += list(data)
                index += list(data.index)
            cy += 1
            i += 1

        if len(column) == 0 or len(index) == 0:
            raise Exception(f'{self.q} {self.key} 沒有資料')

        df[f'{self.q}'] = column
        df[f'{self.key}'] = index
        df.set_index(f'{self.key}').to_csv(
            path_or_buf=data_path.push_ret_pop(file_name), encoding='utf-8-sig')
        print(f'Done !\n{self.q} 資料位於 {data_path.path()}')

    def scrapping_per_day(self):

        def _0_or_1(i: int):
            return '0' if i == 6 else '1'
        geo_query = f'&geo={self.geo}'

        # sy: start year
        # ey: end year
        # cy: current_year
        # sm: start month
        # em: end month
        # iTs: integer to string
        sy = self.sy
        ey = self.ey
        cy = sy
        sm = 1
        while cy <= ey:
            print(f'\n正在抓取 {self.q} {self.key} {cy}年 日資料···')
            while sm <= 7:
                url = f'{self.url}?'
                url += f'date={cy}-{iTs(sm)}-01%20{cy}-{iTs(sm+5)}-3{_0_or_1(sm+5)}&q={self.q}{geo_query}'
                sm += 6
                self._toPage(url)
                sleep(1)
                if self._isData():
                    if not self._download(): continue
                sleep(rd_ms())
            cy += 1
            sm = 1

    def merge_per_day(self):
        print(f'\n正在合併日資料 ···')
        data_path = self.data_path_day
        df = self._get_tidy_df_per_day()
        df.to_csv(data_path.push_ret_pop(f'{self.q}.csv'), encoding='utf-8-sig')
        print(f'Done !\n目標位置在 {data_path.path()}')

    def _get_tidy_df_per_day(self):
        table_type = self.table_type

        resolver = DataResolver(q=self.q, data_type='day')
        tidy = resolver.get_data()
        df = DataFrame()

        if table_type == 'multi-column':
            for y in tidy.keys():
                if len(tidy[y]) != 366:
                    continue
                df[f'{y}'] = [e[2] for e in tidy[y]]
                df['M/D'] = [f'{e[0]}-{e[1]}' for e in tidy[y]]
            return df.set_index('M/D')

        if table_type == 'single-column':
            key = []
            q = []
            for y in tidy.keys():
                key_ = []
                q_ = []
                for t in tidy[y]:
                    _y = y
                    _m = t[0]
                    _d = t[1]
                    _data = t[2]
                    key_.append(f'{_y}-{_m}-{_d}')
                    q_.append(_data)
                key.extend(key_)
                q.extend(q_)
            df[f'{self.key}'] = key
            df[f'{self.q}'] = q
            return df.set_index(f'{self.key}')

    def scrapping_per_month(self):
        start_date = '2004-01-01'
        current_date = str(datetime.now()).split()[0]
        current_year = current_date.split('-')[0]

        geo_query = f'&geo={self.geo}'

        print(f'\n正在抓取 {self.q} {self.key} {2004}年 跨 {current_year}年 月資料···')
        url = f'{self.url}?date={start_date}%20{current_date}&q={self.q}{geo_query}'
        self._toPage(url)
        sleep(1)
        if self._isData():
            self._download()

    def merge_per_month(self):
        print(f'\n正在合併月資料 ···')
        month_resolver = DataResolver(q=self.q, data_type='month')
        tidy = month_resolver.get_data()
        data_path = self.data_path_month
        df = DataFrame()
        df[f'{self.key}'] = tidy['date']
        df[f'{self.q}'] = tidy['data']
        df.set_index(f'{self.key}').to_csv(data_path.push_ret_pop(f'{self.q}.csv'), encoding='utf-8-sig')
        print(f'Done !\n目標位置在 {data_path.path()}')


    def has_set_ticker_detail(self) -> (bool):
        print(f'\n分析公司代號 {self.q} ···')
        self.driver.delete_cookie('stock_user_uuid')
        self.async_init_driver('https://pchome.megatime.com.tw/search')
        sleep(rd_ms())

        input_selector = self.driver.find_element_by_css_selector(self.input_selector)
        sleep(0.5)
        input_selector.click()
        sleep(0.5)
        input_selector.clear()
        sleep(0.5)
        input_selector.send_keys(self.q)
        sleep(0.5)
        submit = self.driver.find_element_by_css_selector(self.submit_selector)
        sleep(0.5)
        submit.click()
        sleep(0.5)
        try:
            elements = self.driver.find_elements_by_css_selector(self.result_selector)
            sleep(1)

            key: list
            for element in elements:
                splited_elements = element.text.split(' ')
                for text in splited_elements:
                    if text == self.q:
                        key = splited_elements
            print(key)
            sleep(1)
            
            if key:
                if self.q == key[1]:
                    self.key = key[0]
                else:
                    self.key = key[1]
            print(f'\n開始擷取 {self.key} 資料···\n')
        except:
            self.key = f'* {self.q}'
            sleep(rd_ms() + 1)

    def catch(self):
        if self.error_map:
            return {
                'q': self.q,
                'key': self.key,
                "date": [self.sy, self.ey],
                'error_map': self.error_map
            }


    def main(self, table_type:str='single-column'):
        temp_path = self.temp_path.path()

        self.data_path_week = PathResolver(['data', 'week'], mkdir=True)
        self.data_path_day = PathResolver(['data', 'day'], mkdir=True)
        self.data_path_month = PathResolver(['data', 'month'], mkdir=True)
        self.table_type = table_type
        self.sequence_type = 'none-cross' if not self.cross_year else 'cross-year'

        self.has_set_ticker_detail()
        self.to_google_trend_page()
        files_cleaner(path=temp_path)


        error_map = {
            "month": False,
            "day": False,
            "cross-year": False,
            "week": False
        }
        hasError = False

        if self.month:
            self.scrapping_per_month()
            try:
                self.merge_per_month()
            except:
                error_map['month'] = True
                hasError = True
            files_cleaner(path=temp_path)

        if self.day:
            self.scrapping_per_day()
            try:
                self.merge_per_day()
            except:
                error_map['day'] = True
                hasError = True
            files_cleaner(path=temp_path)

        if self.sequence_type == 'cross-year':
            self.scrapping_per_week()
            try:
                self.merge_per_week()
            except:
                error_map['cross-year'] = True
                hasError = True
            files_cleaner(path=temp_path)
            self.sequence_type = 'none-cross'

        if self.week:
            self.scrapping_per_week()
            try:
                self.merge_per_week()
            except:
                error_map['week'] = True
                hasError = True
            files_cleaner(path=temp_path)

        self.error_map = error_map if hasError else None

        self.driver.close()
