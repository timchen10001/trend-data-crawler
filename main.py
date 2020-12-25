from cli import dot, taiwan_stock_cli
from config import tw_stock_config
from pandas import read_json
from datetime import datetime

def main():
    print('\n----- Google Trend Crawler -----')
    dot(.8)
    print('\n----- github: https://github.com/timchen10001/trend-data-crawler/tree/main -----')
    print(f'\n----- {datetime.now()} -----\n')
    print('\n----- 若要背景執行大量資料爬蟲，請將系統 *螢幕保護 或 *休眠關閉，否則可能造成資訊中斷而損失資料 -----')
    dot(1)

    config = tw_stock_config()
    
    taiwan_stock_cli(
        geo=config['geo'][0],
        daily=config['daily'][0],
        all_year_range=config['all_year_range'][0],
        columns_name=config['table.columns_name'][0],
    )

main()