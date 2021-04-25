import os
from time import sleep
from platform import system

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
import pandas as pd

from Driver import Driver
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
        geo: str='TW',
        cat: str=""
    ):
        self.download_button_selector = 'body > div.trends-wrapper > div:nth-child(2) > div > md-content > div > div > div:nth-child(1) > trends-widget > ng-include > widget > div > div > div > widget-actions > div > button.widget-actions-item.export'
        self.input_selector = '#search_text_table'
        self.submit_selector = '#bttb > table > tbody > tr > td > div > form > table > tbody > tr > td:nth-child(3) > input[type=button]'
        self.result_selector = '#stocks_list_table > table > tbody > tr > td > a'
        self.no_data_error_selector = 'body > div.trends-wrapper > div:nth-child(2) > div > md-content > div > div > div:nth-child(1) > trends-widget > ng-include > widget > div > div > ng-include > div > ng-include > div > p.widget-error-title'
        self.error_title_selector = 'body > div.trends-wrapper > div:nth-child(2) > div > error > div > div > div.error-title'

        self.error_selectors = [
            self.no_data_error_selector,
            self.error_title_selector
        ]

        self.url = u'https://trends.google.com.tw/trends/explore'
        self.dev = dev
        self.geo = geo
        self.cat = cat
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

        self.temp_path = PathResolver(['temp', self.q], mkdir=True)

        self._get_driver()

    def _get_driver(self) -> (webdriver.chrome.webdriver.WebDriver):
        headless = not self.dev
        # get temp data path
        temp_path = self.temp_path.path()
        files_cleaner(temp_path)
        self.driver = Driver(download_directory=temp_path).driver()

    def to_google_trend_page(self):
        self.driver.get(self.url)
        sleep(.5)
        self.driver.refresh()

    def _toPage(self, url):
        self.driver.get(url)
        s = randint(1, 2) / 2;
        sleep(s)
        print(self.driver.current_url)
        sleep(s)

    def _download(self, failed:int=0):
        dot(.5)

        if failed > 0 and failed <= 3:
            print('\n重啟任務···')
        elif failed > 3:
            return False

        selector = self.download_button_selector
        # download = self.driver.find_element(By.CSS_SELECTOR, selector)
        try:
            download = self.driver.find_element_by_css_selector(selector)
            sleep(1)
            download.click()
            sleep(1)
            self._avoid_rewrite()
            print('Done (成功)')

            return True
        except NoSuchElementException:
            return self.no_error()
        except:
            s = randint(2, 5)
            print(f'Failed (失敗) ··· 休眠約 {s}s 後喚醒')
            dot(s/2.5)
            return self._download(failed=failed+1)


    def no_error(
        self,
        selector_index = 0
    ):
        if selector_index == len(self.error_selectors):
            return True

        selector = self.error_selectors[selector_index]
        s = randint(1, 2) / 2
        try:
            sleep(s)
            error = self.driver.find_element_by_css_selector(selector)
            print(error.text)
            return False
        except:
            return self.no_error(selector_index=selector_index+1)

    def _avoid_rewrite(self):
        temp_path = self.temp_path
        i = 1
        new_path = temp_path.push_ret_pop(f'{i}.csv')
        while os.path.isfile(new_path):
            i += 1
            new_path = temp_path.push_ret_pop(f'{i}.csv')
        origin_path = temp_path.push_ret_pop('multiTimeline.csv')
        os.rename(origin_path, new_path)
