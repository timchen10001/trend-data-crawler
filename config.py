from os import path
from pandas import read_json, json_normalize
from Resolvers import PathResolver


def tw_stock_config():
    pr = PathResolver(['config'], mkdir=True)
    pr.push_back('config.json')
    config_path = pr.path()

    update_config = False
    config = {}

    if path.isfile(config_path):
        config = read_json(config_path)
        cols = config.columns
        print('\n\n----- 爬蟲預設選項 -----')
        for col in cols:
            setting = config[col][0]
            print(f'\n{col}: {setting}')
        print('\n----- 爬蟲預設選項 -----\n')
        update_config = bool(input('\n----- 請問是否更新 爬蟲預設選項 ? (y / n) -----\n') in 'yY')

    if not update_config:
        return config

    geo = 'TW' if str(
        input('\n----- 搜索區域：預設台灣 (y) / 更改區域 (n) -----\n')
    ) in 'yY' else str(
        input('\n----- 區域英文縮寫 (全球: Global, 其他地區自行估狗) -----\n'))

    cat = bool(input('\n----- 指定類別：工商業 (y) / 所有類別 (n) -----\n') in 'yY')

    txt = bool(input('\n----- 是否需要 文字檔 ? (y / n) -----\n') in 'yY')

    day = bool(input('\n----- 是否需要 日資料 ? (y / n) -----\n') in 'yY')

    week = bool(input('\n----- 是否需要 週資料 ? (y / n) -----\n') in 'yY')

    cross_year = bool(input('\n----- 是否需要 跨年(週) 資料？ (y / n) -----\n') in 'yY')


    month = bool(input('\n----- 是否需要 月資料 ? (y / n)\n') in 'yY')

    all_year_range = bool(input('\n----- 是否爬取 全部資料 ? (y / n)-----\n') in 'yY')

    prevent_spamming = bool(input('\n----- 是否開啟 *忽略重複任務* 選項 ? (y / n) -----\n') in 'yY')

    columns_name = config['table.columns_name'][0] if bool(input(
        '\n----- 是否自訂 Table Columns Name ? (y / n) -----\n') in 'nN') else list(input('\n----- 以空格分隔 依序輸入 Table Columns Name -----\n').split(' '))

    mr_w_default = config['median_range.week'][0]
    mr_m_default = config['median_range.month'][0]

    mr_w = mr_w_default if bool(input(
        f'\n----- 是否自訂 week 週資料 中位數取值全距 ? 預設:{mr_w_default}個時間單位  (y / n) -----\n') in 'nN') else int(input('\n----- 請輸入 week 週資料中位數取值全距 -----\n'))
    mr_m = mr_m_default if bool(input(
        f'\n----- 是否自訂 month 月資料 中位數取值全距 ? 預設:{mr_m_default}個時間單位  (y / n) -----\n') in 'nN') else int(input('\n----- 請輸入 month 月資料中位數取值全距 -----\n'))

    config_json = json_normalize({
        "geo": geo,
        'txt': txt,
        "cat": cat,
        "day": day,
        "week": week,
        "month": month,
        "cross_year": cross_year,
        "all_year_range": all_year_range,
        "prevent_spamming":  prevent_spamming,
        "table": {
            "columns_name": columns_name,
        },
        "median_range": {
            "week": mr_w,
            "month": mr_m
        }
    })
    config_json.to_json(config_path)
    print('\n----- 爬蟲預設組態已經更新於 config.json 檔中 -----\n')
    return config_json

