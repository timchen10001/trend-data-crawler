from selenium import webdriver
from Resolvers import PathResolver
from Driver import Driver
from time import sleep
from selenium.common.exceptions import NoSuchElementException

class DriverUpdater:
    def __init__(self):
        self._get_driver()

    def _get_driver(self) -> (webdriver.chrome.webdriver.WebDriver):
        download_pr = PathResolver(['download'], mkdir=True)
        self.updater = Driver(
            download_directory=download_pr.path(),
            headless=False
        ).driver()

    def to_page(self, url:str):
        self.updater.get(url=url)
        sleep(1)

    def check_version(self):
        try:
            judgment = self.updater.find_element_by_css_selector(
            "#content-base > section.section-block.section-block-main-extra > div > div.content-block-main > div.judgment.judgment-bad")
            print(judgment.text)
        except NoSuchElementException:
            self.updater.close();
            print('Done!')

