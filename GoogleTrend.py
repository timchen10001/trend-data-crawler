import os
from time import sleep
from platform import system

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
import pandas as pd

from Resolvers import *
from utils import *
from random import randint

class GoogleTrend:
    def __init__(
        self,
        origin_q: str,
        q: str,
        dr: list,
        day: bool,
        week: bool,
        month: bool,
        cross_year: bool,
        dev: bool = False,
        geo: str='TW'
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
        self.origin_q = origin_q
        self.q = q  # query to search
        self.key = None
        self.day = day
        self.week = week
        self.month = month
        self.cross_year = cross_year
        self.sy = int(dr[0])
        self.ey = int(dr[1])
        self.env_dir = os.getcwd()
        self.platform = system()
        self.driver = None

        self.temp_path = PathResolver(['temp', self.q], mkdir=True)

        self._get_driver()

    def _get_driver(self) -> (webdriver.chrome.webdriver.WebDriver):
        headless = not self.dev

        driver_pr = PathResolver(['driver'])
        driver_pr.push_back(self._driver_file_name())

        # get temp data path
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
            executable_path=driver_pr.path(),
            options=chrome_options
        )
        driver.set_window_size(1440, 900)
        self.driver = driver

    def to_google_trend_page(self):
        self.driver.get(self.url)
        sleep(.5)
        self.driver.refresh()


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
