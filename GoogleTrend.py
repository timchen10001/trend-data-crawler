import os
from shutil import rmtree
from time import sleep
from time import time
from random import randint
from platform import system
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd


def rd_ms():
    return randint(1, 2)

def iTs(i: int) -> str:
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

def is_path(path: str) -> bool:
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

def is_valid_year(y_r: list, year: int)->bool:
    if len(y_r) != 2:
        raise Exception('the length in year_range must be 2')
    return (year >= y_r[0] and year <= y_r[1])

def valid_year_at_most(daily: bool, output_type: str='int'):
    y = datetime.now().year
    if daily:
        return y-1 if output_type == 'int' else str(y-1)
    return y if output_type == 'int' else str(y)

class PathResolver:
    def __init__(self, nodes: list=[], mkdir=False):
        self._ps = self._path_separater()
        self._root = os.getcwd()
        self._nodes = nodes
        if mkdir: self.mkdir()

    def _path_separater(self):
        plat = system()
        ps = ''
        if plat == 'Windows': ps = '\\'
        else: ps = '/'
        return ps

    def path(self) -> str:
        path = self._root
        for node in self._nodes:
            path += f'{self._ps}{node}'
        return path

    def push_back(self, node: str):
        self._nodes.append(node)

    def pop_back(self):
        self._nodes.pop()

    def mkdir(self):
        if len(self._nodes) == 0: return
        ps = self._ps
        p = self._root
        for node in self._nodes:
            if not node: continue
            p += f'{ps}{node}'
            if not os.path.isdir(p):
                os.mkdir(p)
        return p

    def push_ret_pop(self, node: str):
        self.push_back(node)
        path_str = self.path()
        self.pop_back()
        return path_str

    def isfile(self, file_path: str)->bool:
        fp = self.push_ret_pop(file_path)
        if os.path.isfile(fp): return True
        return False

class GoogleTrend:
    def __init__(self, q: str, dr: list, daily: str, dev: bool=False, geo='TW'):
        self.download_button_selector = 'body > div.trends-wrapper > div:nth-child(2) > div > md-content > div > div > div:nth-child(1) > trends-widget > ng-include > widget > div > div > div > widget-actions > div > button.widget-actions-item.export'
        self.no_data_error_selector = 'body > div.trends-wrapper > div:nth-child(2) > div > md-content > div > div > div:nth-child(1) > trends-widget > ng-include > widget > div > div > ng-include > div > ng-include > div > p.widget-error-title'

        self.url = u'https://trends.google.com.tw/trends/explore'
        self.dev = dev
        self.geo = geo
        self.ps = path_separate() # path_separate
        self.q = q  # query to search
        self.daily = daily
        self.dr = dr  # date range
        self.env_dir = os.getcwd()
        self.platform = system()
        self.temp_path = PathResolver(['temp', self.q], mkdir=True)
        self.data_path_week = PathResolver(['data', 'week'], mkdir=True)
        self.data_path_day = PathResolver(['data', 'day'], mkdir=True) if daily else None
        self.driver = self._get_driver()

    def _get_driver(self) -> webdriver.chrome.webdriver.WebDriver:
        headless = not self.dev

        driver_path = PathResolver(['driver'])
        driver_path.push_back(self._driver_file_name())

        temp_path = self.temp_path.path()

        files_cleaner(temp_path)

        download_prefs = {
            'download.default_directory': temp_path,
            'download.prompt_for_download': False,
            'profile.default_content_settings.popups': 0
        }

        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', download_prefs)

        if headless:
            chrome_options.add_argument('--window-size=1440,900')
            chrome_options.add_argument('--headless')

        driver = webdriver.Chrome(
            executable_path=driver_path.path(),
            options=chrome_options
        )
        driver.set_window_size(1440, 900)
        driver.get(self.url)
        sleep(0.5)
        driver.refresh()
        return driver


    def _driver_file_name(self):
        file_name = 'chromedriver'
        if self.platform == 'Windows': file_name += '.exe'
        elif self.platform == 'Linux': file_name += '-linux'
        return file_name

    def _toPage(self, url):
        self.driver.get(url)
        sleep(rd_ms())
        print(self.driver.current_url)

    def _download(self):
        headless = not self.dev
        selector = self.download_button_selector
        try:
            # download = self.driver.find_element(By.CSS_SELECTOR, selector)
            download = self.driver.find_element_by_css_selector(selector)
        except:
            raise Exception(f'{self.driver.current_url} no trending data')
        sleep(rd_ms())
        download.click()
        sleep(1)
        self._avoid_rewrite()

    def _isData(self):
        selector = self.no_data_error_selector
        try:
            error = self.driver.find_element_by_css_selector(selector)
            print(error.text)
            return False
        except:
            return True

    def _avoid_rewrite(self):
        temp_path = self.temp_path
        i = 1
        new_path = temp_path.push_ret_pop(f'{i}.csv')
        while os.path.isfile(new_path):
            i+= 1
            new_path = temp_path.push_ret_pop(f'{i}.csv')
        origin_path = temp_path.push_ret_pop('multiTimeline.csv')
        os.rename(origin_path, new_path)

    def _get_tidy_df_per_day(self):
        resolver = DataResolver(self.q)
        tidy = resolver.tidy_map
        df = pd.DataFrame()
        for y in tidy.keys():
            df[f'{y}'] = [e[2] for e in tidy[y]]
            df['M/D'] = [f'{e[0]}-{e[1]}' for e in tidy[y]]
        return df.set_index('M/D')

    def scrapping_per_week(self, sy: int, ey: int):
        geo_query = f'&geo={self.geo}'
        cy = sy
        sm = 1
        n = 1
        while cy <= ey:
            print(f'\n正在抓取 {cy}年 週資料···')
            url = f'{self.url}?date={cy}-01-01%20{cy}-12-31&q={self.q}{geo_query}'
            self._toPage(url)
            sleep(1)
            self._download()
            sleep(rd_ms())
            cy += 1
    def _merge_per_week(self, sy: int, ey: int):
        print(f'\n正在合併週資料 ···')
        data_path = self.data_path_week
        temp_path = self.temp_path
        df = pd.DataFrame()
        i = 1
        cy = sy

        column = []
        index = []
        while cy <= ey:
            csv = pd.read_csv(temp_path.push_ret_pop(f'{i}.csv'))
            data = csv['類別：所有類別'][1:]
            column += list(data)
            index += list(data.index)
            cy += 1
            i += 1
        df[f'{self.q}'] = column
        df.index = index
        df.to_csv(data_path.push_ret_pop(f'{self.q}.csv'))
        print(f'Done !\n{self.q} 資料位於 {data_path.path()}')

    def scrapping_per_day(self, sy: int, ey: int):
        # sy: start year
        # ey: end year
        # cy: current_year
        # sm: start month
        # em: end month
        # iTs: integer to string

        def _0_or_1(i: int):
            return '0' if i == 6 else '1'
        geo_query = f'&geo={self.geo}'

        cy = sy
        sm = 1
        while cy <= ey:
            print(f'\n正在抓取 {cy}年 日資料···')
            while sm <= 7:
                url = f'{self.url}?'
                url += f'date={cy}-{iTs(sm)}-01%20{cy}-{iTs(sm+5)}-3{_0_or_1(sm+5)}&q={self.q}{geo_query}'
                sm += 6
                self._toPage(url)
                sleep(1)
                if self._isData():
                    self._download()
                sleep(rd_ms())
            cy += 1
            sm = 1

    def _merge_per_day(self):
        print(f'\n正在合併日資料 ···')
        data_path = self.data_path_day
        df = self._get_tidy_df_per_day()
        df.to_csv(data_path.push_ret_pop(f'{self.q}.csv'))
        print(f'Done !\n目標位置在 {data_path.path()}')


    def main(self):
        start_year = int(self.dr[0])
        end_year = int(self.dr[1])
        temp_path = self.temp_path
        if self.daily:
            self.scrapping_per_day(start_year, end_year)
            self._merge_per_day()
            files_cleaner(temp_path.path())
        self.scrapping_per_week(start_year, end_year)
        self._merge_per_week(start_year, end_year)
        files_cleaner(temp_path.path())
        self.driver.close()

# data cleaner
class DataResolver:
    def __init__(self, q: str):
        self.ps = path_separate()
        self.q = q
        self.temp_path = PathResolver(['temp', q], mkdir=True)
        self.tidy_map = self._tidy_list()

    def _tidy_list(self) -> dict:
        path_list = self._temp_file_mapper()
        if len(path_list) == 0:
            raise Exception(f'{self.q} 搜尋資料不足')

        _tidy = {}
        for p in path_list:
            csv = pd.read_csv(p)

            data = csv['類別：所有類別'][1:]  # not tidy
            date = list(data.index)  # not tidy

            tidy_data = self._merge_with_conflict(data=data, date=date)

            # int
            year = date[1].split('-')[0]

            if year in _tidy.keys():
                _tidy[year] += tidy_data
            else:
                _tidy[year] = tidy_data
        return _tidy

    def _temp_file_mapper(self) -> list:
        temp_path = self.temp_path
        i = 1
        l = []
        while temp_path.isfile(f'{i}.csv'):
            l.append(temp_path.push_ret_pop(f'{i}.csv'))
            i += 1
        return l

    def _merge_with_conflict(self, data: list, date: list) -> list:
        tidy = []
        i = 0
        for e, val in zip(date, data):
            t = e.split('-')[1:]
            month = t[0]
            day = t[1]
            tidy.append([month, day, int(val)])
            if len(date) == 181 and month == '02' and day == '28':
                tidy.append(['02', '29', 'NAN'])
            i += 1
        return tidy

def google_trend_cli():
    print(f'\n-----{datetime.now()}-----')
    geo = 'TW' if str(
        input('\n-----搜索區域：預設台灣(y) / 更改區域(n)-----\n')
    ) in 'yY' else str(
        input('-----請輸入區域英文縮寫 (全球: Global, 其他地區自行估狗)-----')
    )
    qs = str(input('-----請輸入要搜索的關鍵字： 例如 google facebook-----\n')).split()
    daily = bool(input('\n-----是否需要日資料? (y/n)-----\n') in 'yY')
    y_range = [2004, valid_year_at_most(daily=daily, output_type='int')]
    y_start: int
    y_end: int
    while True:
        y_start = valid_number(input('\n-----請輸入起始年份： (2004 require at least)-----\n'), output_type='int')
        if is_valid_year(y_range, y_start): break
        else: print(f'\n!!! 起始年份必須介於 {y_range[0]} ~ {y_range[1]}之間')
    while True:
        y_end = valid_number(input(f'\n請輸入結尾年份： ({y_range[1]} require at most)\n'), output_type='int')
        if is_valid_year(y_range, y_end): break
        else: print(f'\n!!! 結尾年份必須介於 {y_range[0]} ~ {y_range[1]}')

    t_start = time()
    for q in qs:
        q = q.replace('-', ' ')
        print(f'\n開始抓取 {q} ···')
        tt_st = time()
        google_trend = GoogleTrend(q, [y_start, y_end], dev=False, daily=daily, geo=geo)
        google_trend.main()
        tt_ed = time()
        print(f'{q} 耗時約 {int(tt_ed-tt_st)}s')
    t_end = time()
    print(f'\n總計耗時約 {int(t_end-t_start)}s')
    return input('-----繼續 (y) / 結束 (n)-----\n') in 'yY'

def main():
    while True:
        if not google_trend_cli(): break
    sleep(rd_ms())
    print('系統將在 2 秒後自動關閉視窗，或是手動點擊右上角離開視窗 ···')

if __name__ == "__main__":
    main()
