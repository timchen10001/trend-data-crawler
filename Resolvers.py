import os
from platform import system
from pandas import read_csv
from utils import *

class PathResolver:
    def __init__(self, nodes: list=[], mkdir=False):
        self._ps = self._path_separater()
        self._root = os.getcwd()
        self._nodes = nodes
        if mkdir: self.mkdir()

    def clear(self):
        self._nodes = []

    def _path_separater(self):
        plat = system()
        ps = ''
        if plat == 'Windows': 
            return '\\'
        return '/'

    def path(self, merge:bool = False) -> (str):
        path = self._root
        for node in self._nodes:
            path += f'{self._ps}{node}'
        return path

    def push_back(self, node: str or list):
        if type(node) == str:
            self._nodes.append(node)
        elif type(node) == list:
            self._nodes.extend(node)
        else:
            raise TypeError(f'type of {node} must be str or list')

    def pop_back(self, times: int=1):
        while times > 0:
            self._nodes.pop()
            times -= 1

    def mkdir(self, nodes:list=[]):
        if len(nodes) != 0:
            self.push_back(nodes)
        if len(self._nodes) == 0: 
            return

        ps = self._ps
        p = self._root
        for node in self._nodes:
            if not node: continue
            p += f'{ps}{node}'
            if not os.path.isdir(p):
                os.mkdir(p)
        self.pop_back(times=len(nodes))
        return p

    def push_ret_pop(self, nodes):
        p: list or str
        if type(nodes) == str:
            self._nodes.append(nodes)
            p = self.path()
            self.pop_back()
            return p
        elif type(nodes) == list:
            p = []
            for node in nodes:
                file_path = self.push_ret_pop(node)
                p.append(file_path)
        return p

    def isfile(self, file_path: str)->bool:
        fp = self.push_ret_pop(file_path)
        if os.path.isfile(fp): return True
        return False

# data cleaner
class DataResolver:
    def __init__(self, q: str):
        self.ps = path_separate()
        self.q = q
        self.temp_path = PathResolver(['temp', q], mkdir=True)
        self.tidy_map = self._tidy_list()

    def _tidy_list(self) -> (dict):
        path_list = self._temp_file_mapper()
        if len(path_list) == 0:
            raise Exception(f'{self.q} 搜尋資料不足')

        _tidy = {}
        for p in path_list:
            csv = read_csv(p)

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

    def _temp_file_mapper(self) -> (list):
        temp_path = self.temp_path
        i = 1
        l = []
        while temp_path.isfile(f'{i}.csv'):
            l.append(temp_path.push_ret_pop(f'{i}.csv'))
            i += 1
        return l

    def _merge_with_conflict(self, data: list, date: list) -> (list):
        tidy = []
        i = 0
        for e, val in zip(date, data):
            t = e.split('-')[1:]
            month = t[0]
            day = t[1]
            tidy.append([month, day, int(val)])
            if len(date) == 181 and month == '02' and day == '28':
                tidy.append(['02', '29', 'NA'])
            i += 1
        return tidy