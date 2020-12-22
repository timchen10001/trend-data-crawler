import os
from time import sleep
from platform import system

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd

from Resolvers import PathResolver
from Resolvers import DataResolver
from utils import *

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
        # download = self.driver.find_element(By.CSS_SELECTOR, selector)
        download = self.driver.find_element_by_css_selector(selector)
        sleep(rd_ms())
        download.click()
        sleep(rd_ms())
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
            if len(tidy[y]) != 366: continue
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