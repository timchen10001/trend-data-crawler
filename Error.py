from pandas.core.frame import DataFrame
from pandas import read_csv, read_json
from Resolvers import PathResolver
from utils import today_folder_name
from os import path

class ErrorResolver:
    def __init__(self, error_list):
        self.error_list = error_list
        self.option_init()
        self.destruct()

    def option_init(self):
        config_path = PathResolver(['config', 'config.json']).path()
        self.table_columns_name = read_json(config_path)['table.columns_name'][0]
        self.err = {
            'month': [],
            "day": [],
            "cross-year": [],
            "week": []
        }

    def destruct(self):
        if not self.error_list:
            return

        for error in self.error_list:
            q = error['q']
            key = error['key']
            date = error['date']
            error_map = error['error_map']
            for dataType in error_map.keys():
                if error_map[dataType]:
                    self.err[dataType].append({
                        "q": q,
                        "key":key,
                        "date": date
                    })
        self.rewrite(folder='day')
        self.rewrite(folder='month')
        self.rewrite(folder='cross-year')
        self.rewrite(folder='week')

    def logging(self):
        cross_year = self.err['cross-year']
        day = self.err['day']
        month = self.err['month']
        week = self.err['week']

        print('\n----- 無資料除錯紀錄 -----')

        print('\n* 月資料:', end=' ')
        for m in month:
            print(m['q'], end=' ')

        print('\n* 週資料:', end=' ')
        for w in week:
            print(w['q'], end=' ')

        print('\n* 週跨年:', end=' ')
        for cy in cross_year:
            print(cy['q'], end=' ')

        print('\n* 日資料:', end=' ')
        for d in day:
            print(d['q'], end=' ')
        print('\n\n----- 無資料之關鍵字已紀錄在 error 資料夾中 -----\n')


    def rewrite(self, folder:str):
        def file_name():
            if folder == 'cross-year':
                return 'week (cross-year).csv'
            else:
                return f'{folder}.csv'

        error_map = self.err
        pr = PathResolver(['data', 'error', today_folder_name()], mkdir=True)

        infos = []
        try:
            infos = error_map[folder]
        except:
            return

        pr.push_back(node=file_name())
        write_path = pr.path()
        pr.pop_back()

        index = []
        first = []
        second = []
        third = []
        if path.isfile(write_path):
            csv = read_csv(filepath_or_buffer=write_path)
            columns = csv.columns
            index = list(csv[columns[0]])
            first = list(csv[columns[1]])
            second = list(csv[columns[2]])
            third = list(csv[columns[3]])

        for info in infos:
            index.append(info['q'])
            first.append(info['key'])
            second.append(f'{info["date"][0]}-{info["date"][1]}')
            third.append('NA')
        df = DataFrame()
        df[self.table_columns_name[0]] = index
        df[self.table_columns_name[1]] = first
        df[self.table_columns_name[2]] = second
        df[self.table_columns_name[3]] = third
        df.fillna('NA').set_index(self.table_columns_name[0]).to_csv(write_path, encoding="utf-8-sig")
