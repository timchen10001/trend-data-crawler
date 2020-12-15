from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import shutil
import os
import time
import random
import pandas as pd
import platform


def rd_ms():
    return random.randint(1, 2)


def remove_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    else:
        raise Exception(f'{path} not exist')


def iTs(i: int) -> str:
    s = ''
    if i < 10:
        s += '0'
    return s + str(i)

def path_exists(path: str) -> bool:
    ps = path_separate()
    if ps in path:
        return True
    return False


def files_cleaner(path: str):
    if os.path.isdir(path):
        remove_folder(path)
    os.mkdir(path)

def path_separate():
    plat = platform.system()
    ps = ''
    if plat == 'Windows': ps = '\\'
    else: ps = '/'
    return ps


class GoogleTrend:
    def __init__(self, q: str, dr: list, dev: bool=False, geo='Global'):
        self.download_button_selector = 'body > div.trends-wrapper > div:nth-child(2) > div > md-content > div > div > div:nth-child(1) > trends-widget > ng-include > widget > div > div > div > widget-actions > div > button.widget-actions-item.export'

        self.url = u'https://trends.google.com.tw/trends/explore'
        self.dev = dev
        self.geo = geo if geo != 'Global' else ''
        self.ps = path_separate() # path_seperate
        self.q = q  # query to search
        self.dr = dr  # date range
        self.env_dir = os.getcwd()
        self.platform = platform.system()
        self.driver = self._get_driver()
        self.main()

    def _get_driver(self) -> webdriver.chrome.webdriver.WebDriver:
        headless = not self.dev

        driver_path = self._get_driver_path()
        data_path = self._create_path(f'{self.ps}temp')
        data_path += f'{self.ps}{self.q}'

        files_cleaner(data_path)

        download_prefs = {
            'download.default_directory': data_path,
            'download.prompt_for_download': False,
            'profile.default_content_settings.popups': 0
        }

        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--window-size=1440,900')
            chrome_options.add_argument('--headless')
        chrome_options.add_experimental_option('prefs', download_prefs)
        driver = webdriver.Chrome(
            executable_path=driver_path,
            options=chrome_options
        )
        driver.set_window_size(1440, 900)
        driver.get(self.url)
        time.sleep(0.5)
        driver.refresh()
        return driver

    def _create_path(self, path: str):
        if not path_exists(path=path):
            return path
        split_p = path.split(self.ps)
        p = f'{self.env_dir}'
        for node in split_p:
            if not node:
                continue
            p += f'{self.ps}{node}'
            if not os.path.isdir(p):
                os.mkdir(p)
        return p

    def _get_driver_path(self):
        path = rf'{self.env_dir}{self.ps}driver{self.ps}chromedriver'
        if self.platform == 'Windows': path += '.exe'
        elif self.platform == 'Linux': path += '-linux'
        return path

    def _toPage(self, url):
        self.driver.get(url)
        time.sleep(rd_ms())

    def _download(self):
        headless = not self.dev
        selector = self.download_button_selector
        download = self.driver.find_element(By.CSS_SELECTOR, selector)
        time.sleep(rd_ms())
        download.click()
        time.sleep(1)
        self._avoid_rewrite()
        print(self.driver.current_url)

    def _avoid_rewrite(self):
        temp_path = f'{self.env_dir}{self.ps}temp{self.ps}{self.q}'
        i = 1
        while os.path.isfile(f'{temp_path}{self.ps}{i}.csv'): i+= 1
        avoid_rewrite_path = f'{temp_path}{self.ps}{i}.csv'
        os.rename(f'{temp_path}{self.ps}multiTimeline.csv', avoid_rewrite_path)

    def _get_tidy_df(self):
        resolver = DataResolver(self.q)
        tidy = resolver.tidy_map

        df = pd.DataFrame()
        for y in tidy.keys():
            df[f'{y}'] = [e[2] for e in tidy[y]]
            df['M/D'] = [f'{e[0]}-{e[1]}' for e in tidy[y]]
        return df.set_index('M/D')

    def _merge_per_day(self):
        print(f'\n正在合併資料 ···')
        data_path = self._create_path(f'{self.ps}data{self.ps}day{self.ps}{self.q}')
        files_cleaner(data_path)
        print(f'合併完成 ···\n目標位置在 {data_path}\n')
        data_path += f'{self.ps}{self.q}.csv'

        df = self._get_tidy_df()
        df.to_csv(data_path)
        

    def scrapping_per_day(self, sy: int, ey: int):
        # sy: start year
        # ey: end year
        # cy: current_year
        # sm: start month
        # em: end month
        # iTs: integer to string

        def _0_or_1(i: int) -> str:
            return '0' if i == 6 else '1'
        geo_query = f'&geo={self.geo}' if self.geo else ''

        cy = sy
        sm = 1
        while cy <= ey:
            print(f'\n正在抓取第 {cy} 年資料 ···')
            while sm <= 7:
                url = f'{self.url}?'
                url += f'date={cy}-{iTs(sm)}-01%20{cy}-{iTs(sm+5)}-3{_0_or_1(sm+5)}&q={self.q}{geo_query}'
                sm += 6
                self._toPage(url)
                time.sleep(1)
                self._download()
                time.sleep(rd_ms())
            cy += 1
            sm = 1

    def main(self):
        start_year = int(self.dr[0].split('-')[0])
        end_year = int(self.dr[1].split('-')[0])

        self.scrapping_per_day(start_year, end_year)
        self.driver.close()
        self._merge_per_day()

# data cleaner
class DataResolver:
    def __init__(self, q: str):
        self.ps = path_separate()
        self.env_dir = os.getcwd()
        self.root = f'{self.env_dir}{self.ps}temp{self.ps}{q}'
        self.valid_int = [str(i) for i in range(10)]
        self.tidy_map = self._tidy_list()

    def _tidy_list(self) -> dict:
        path_list = self._temp_file_mapper()
        if len(path_list) == 0:
            raise Exception(f'{self.root} 沒有暫存資料')

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
        path = self.root
        if not os.path.isdir(path):
            raise Exception(f'{path} 路徑不存在')
        i = 1
        l = []
        while os.path.isfile(f'{self.root}{self.ps}{i}.csv'):
            l.append(f'{self.root}{self.ps}{i}.csv')
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

if __name__ == "__main__":
    q = str(input('請輸入要搜索的關鍵字： 例如：google, 10110, 中文也可以\n'))
    start = str(input('請輸入起始時間 例如：2004-01-01\n'))
    end = str(input('請輸入最後時間 例如：2019-12-31\n'))
    google_trend = GoogleTrend(q, [start, end], dev=False)