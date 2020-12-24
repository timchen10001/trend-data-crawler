from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
from time import sleep
from Resolvers import PathResolver

class TaiwanStock ex:
    def __init__(self, mark_name):
        self.mark_name = mark_name

    def get_driver(self):
        driver_path = PathResolver(['driver'])