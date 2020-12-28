import os
from time import sleep
from platform import system

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd

from Resolvers import *
from utils import *
from random import randint

from pprint import pprint

class GoogleTrend:
    def __init__(
        self,
        q: str,
        dr: list,
        daily: bool,
        cross_year: bool,
        dev: bool = False,
        geo='TW'
    ):
        self.download_button_selector = 'body > div.trends-wrapper > div:nth-child(2) > div > md-content > div > div > div:nth-child(1) > trends-widget > ng-include > widget > div > div > div > widget-actions > div > button.widget-actions-item.export'
        self.no_data_error_selector = 'body > div.trends-wrapper > div:nth-child(2) > div > md-content > div > div > div:nth-child(1) > trends-widget > ng-include > widget > div > div > ng-include > div > ng-include > div > p.widget-error-title'
        self.input_selector = '#search_text_table'
        self.submit_selector = '#bttb > table > tbody > tr > td > div > form > table > tbody > tr > td:nth-child(3) > input[type=button]'
        self.result_selector = '#stocks_list_table > table > tbody > tr > td > a'

        self.url = u'https://trends.google.com.tw/trends/explore'
        self.dev = dev
        self.geo = geo
        self.ps = path_separate()  # path_separate
        self.q = q  # query to search
        self.key = ''
        self.daily = daily
        self.cross_year = cross_year
        self.dr = dr  # date range
        self.env_dir = os.getcwd()
        self.platform = system()
        self.driver = None

        self.temp_path = PathResolver(['temp', self.q], mkdir=True)
        self.data_path_week = PathResolver(['data', 'week'], mkdir=True)
        self.data_path_day = PathResolver(
            ['data', 'day'], mkdir=True) if daily else None
        self._get_driver()
        self.has_set_query_detail()
        self.to_google_trend_page()

    def _get_driver(self) -> (webdriver.chrome.webdriver.WebDriver):
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
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('blink-settings=imagesEnabled=false')

        if headless:
            chrome_options.add_argument('--window-size=1440,900')
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--log-level=3')

        driver = webdriver.Chrome(
            executable_path=driver_path.path(),
            options=chrome_options
        )
        driver.set_window_size(1440, 900)
        print(f'\n分析公司代號 {self.q} ···')
        driver.delete_cookie('stock_user_uuid')
        async_init_driver(driver, 'https://pchome.megatime.com.tw/search')
        sleep(rd_ms())
        self.driver = driver

    def to_google_trend_page(self):
        self.driver.get(self.url)
        sleep(.5)
        self.driver.refresh()

    def has_set_query_detail(self) -> (bool):
        input_selector = self.driver.find_element_by_css_selector(
            self.input_selector)
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
            key = self.driver.find_element_by_css_selector(
                self.result_selector).text.split(' ')
            if key:
                if self.q == key[1]:
                    self.key = key[0]
                else:
                    self.key = key[1]
            print(f'\n開始擷取 {self.key} 資料···\n')
        except:
            self.key = f'* {self.q}'
            sleep(rd_ms() + 1)

    def _driver_file_name(self):
        file_name = 'chromedriver'
        if self.platform == 'Windows':
            file_name += '.exe'
        elif self.platform == 'Linux':
            file_name += '-linux'
        return file_name

    def _toPage(self, url):
        self.driver.get(url)
        sleep(0.5)
        print(self.driver.current_url)

    def _download(self, failed:int=0):
        dot(.5)

        if failed > 0 and failed <= 3: 
            print('\n重啟任務···')
        elif failed > 3:
            return False

        headless = not self.dev
        selector = self.download_button_selector
        # download = self.driver.find_element(By.CSS_SELECTOR, selector)
        try:
            download = self.driver.find_element_by_css_selector (selector)
            sleep(1)
            download.click()
            sleep(1)
            self._avoid_rewrite()
            print('Done (成功)')
            return True
        except:
            s = randint(5, 10)
            print(f'Failed (失敗) ··· 休眠約 {s}s 後喚醒')
            dot(s/2.5)
            return self._download(failed=failed+1)


    def _isData(self):
        selector = self.no_data_error_selector
        try:
            error = self.driver.find_element_by_css_selector(selector)
            sleep(1)
            print(error.text)
            return False
        except:
            return True

    def _avoid_rewrite(self):
        temp_path = self.temp_path
        i = 1
        new_path = temp_path.push_ret_pop(f'{i}.csv')
        while os.path.isfile(new_path):
            i += 1
            new_path = temp_path.push_ret_pop(f'{i}.csv')
        origin_path = temp_path.push_ret_pop('multiTimeline.csv')
        os.rename(origin_path, new_path)

    def scrapping_per_week(self, sequence_type: str, sy: int, ey: int):
        geo_query = f'&geo={self.geo}'
        cy = sy
        sm = 1
        n = 1
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

    def _merge_per_week(self, sequence_type: str, sy: int, ey: int):
        file_name = ''
        if sequence_type == 'none-cross':
            print(f'\n正在合併 週資料(未跨越年度) ···')
            file_name = f'{self.q}.csv'
        elif sequence_type == 'cross-year':
            print(f'\n正在合併 週資料(跨越年度) ···')
            file_name = f'{self.q} (cross-year).csv'

        data_path = self.data_path_week
        temp_path = self.temp_path
        df = pd.DataFrame()
        i = 1
        cy = sy

        column = []
        index = []
        while cy <= ey:
            f_name = f'{i}.csv'
            if temp_path.isfile(f_name):
                filepath = temp_path.push_ret_pop(f_name)
                csv = pd.read_csv(filepath_or_buffer=filepath)
                data = csv['類別：所有類別'][1:]
                column += list(data)
                index += list(data.index)
            cy += 1
            i += 1
        df[f'{self.q}'] = column
        df[f'{self.key}'] = index
        df.set_index(f'{self.key}').to_csv(
            path_or_buf=data_path.push_ret_pop(file_name))
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

    def _merge_per_day(self, table_type: str = 'single-column'):
        print(f'\n正在合併日資料 ···')
        data_path = self.data_path_day
        df = self._get_tidy_df_per_day(table_type=table_type)
        df.to_csv(data_path.push_ret_pop(f'{self.q}.csv'))
        print(f'Done !\n目標位置在 {data_path.path()}')

    def _get_tidy_df_per_day(self, table_type: str):
        resolver = DataResolver(self.q)
        tidy = resolver.tidy_map()
        df = pd.DataFrame()

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

    def main(self):
        start_year = int(self.dr[0])
        end_year = int(self.dr[1])
        temp_path = self.temp_path
        if self.daily:
            self.scrapping_per_day(start_year, end_year)
            self._merge_per_day()
            files_cleaner(temp_path.path())

        if self.cross_year:
            self.scrapping_per_week(sequence_type='cross-year', sy=start_year, ey=end_year)
            self._merge_per_week(sequence_type='cross-year', sy=start_year, ey=end_year)
            files_cleaner(temp_path.path())

        self.scrapping_per_week(sequence_type='none-cross', sy=start_year, ey=end_year)
        self._merge_per_week(sequence_type='none-cross', sy=start_year, ey=end_year)
        files_cleaner(temp_path.path())

        self.driver.close()

def async_init_driver(driver, url: str):
    try:
        driver.get(url)
    except:
        raise Exception('\n網路狀況不太好，伺服器回應超時···\n')