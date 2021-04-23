from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Resolvers import PathResolver
from platform import system

class DriverPath:
    def __init__(self):
        self._set_driver_path()

    def _set_driver_path(self):
        driver_pr = PathResolver([
            'driver',
            self._get_driver_file_name()
        ])
        self.driver_directory = driver_pr.path()

    def _get_driver_file_name(self):
        platform = system()
        file_name = 'chromedriver'
        if platform == 'Windows':
            file_name += '.exe'
        elif platform == 'Linux':
            file_name += '-linux'
        return file_name








class Driver(DriverPath):
    def __init__(
        self,
        download_directory: str,
        headless: bool = True
    ):
        DriverPath.__init__(self)
        download_prefs = {
            'download.default_directory': download_directory,
            'download.prompt_for_download': False,
            'profile.default_content_settings.popups': 0
        }
        chrome_options = Options()
        chrome_options.add_experimental_option('prefs', download_prefs)
        chrome_options.add_argument('--disable-notifications')
        chrome_options.add_argument('blink-settings=imagesEnabled=false')
        chrome_options.add_argument('--log-level=3')

        if headless:
            chrome_options.add_argument('--window-size=1440,900')
            chrome_options.add_argument('--headless')

        driver = webdriver.Chrome(
            executable_path=self.driver_directory,
            options=chrome_options
        )

        driver.set_window_size(1440, 900)
        self._driver = driver

    def driver(self):
        return self._driver








class DriverUpdater(DriverPath):
    def __init__(self, down_file_name: str):
        DriverPath.__init__(self)
        self.download_file_name = download_file_name
        self._get_driver()

    def _get_driver(self):

        download_pr = PathResolver([
            'download',
            self.download_file_name
        ], mkdir=True)

        self.driver = Driver(
            driver_directory=self.driver_directory,
            download_directory=download_pr.path()
        )



