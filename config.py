from os import path
import pandas as pd
from Resolvers import PathResolver


def tw_stock_config():
    pr = PathResolver(['config'], mkdir=True)
    pr.push_back('config.json')
    config_path = pr.path()

    update_config = False
    config = {}

    if path.isfile(config_path):
        config = pd.read_json(config_path)
        cols = config.columns
        print('\n\n----- 👇👇👇 爬蟲預設選項 👇👇👇 -----')
        for col in cols:
            setting = config[col][0]
            print(f'\n{col}: {setting}')
        print('\n----- ☝️ ☝️ ☝️  爬蟲預設選項 ☝️ ☝️ ☝️ -----\n')
        update_config = bool(input('\n----- 請問是否更新爬蟲預設選項 ？ (y / n) -----\n') in 'Yy')

    if not update_config:
        return config

    geo = 'TW' if str(
        input('\n----- 搜索區域：預設台灣(y) / 更改區域(n) -----\n')
    ) in 'yY' else str(
        input('\n----- 區域英文縮寫 (全球: Global, 其他地區自行估狗) -----\n'))

    daily = bool(input('\n----- 是否需要日資料? (y / n) -----\n') in 'yY')

    cross_year = bool(input('\n----- 是否需要跨年度資料？ (y / n) -----\n') in 'yY')

    all_year_range = bool(input('\n----- 是否爬取全部資料？ (y / n)-----\n') in 'yY')

    prevent_spamming = bool(input('\n----- 是否開啟略過重複任務的選項 ? (y / n) -----\n') in 'yY')

    columns_name = config['table.columns_name'][0] if bool(input(
        '\n----- 是否更改 Table Columns Name ? (y / n) -----\n') in 'nN') else list(input('\n----- 以空格分隔 依序輸入 Table Columns Name -----\n').split(' '))

    config_json = pd.json_normalize({
        "geo": geo,
        "daily": daily,
        "cross_year": cross_year,
        "all_year_range": all_year_range,
        "prevent_spamming":  prevent_spamming,
        "table": {
            "columns_name": columns_name,
        }
    })
    config_json.to_json(config_path)
    print('\n----- 爬蟲預設組態已經更新於 config.json 檔中 -----\n')
    return config_json

