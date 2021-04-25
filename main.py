from cli import SVI_CLI
from config import tw_stock_config
from datetime import datetime
from utils import dot
from Updater import DriverUpdater
from selenium.common.exceptions import SessionNotCreatedException


def main():
    print('\n----- Google Trend Crawler -----')
    dot(.5)
    print('\n----- github: https://github.com/timchen10001/trend-data-crawler/tree/main -----')
    print(f'\n----- {datetime.now()} -----')
    print('\n----- 若要背景執行大量資料爬蟲，請將系統 *螢幕保護 或 *休眠關閉，否則可能造成資訊中斷而損失資料 -----')
    dot(.5)

    try:
        updater = DriverUpdater()
        updater.to_page(url="https://www.whatismybrowser.com/detect/what-version-of-chrome-do-i-have")
        updater.check_version()
    except SessionNotCreatedException:
        print('session created failed~')

    config = tw_stock_config()

    svi = SVI_CLI(config=config)
    svi.taiwan_stock_cli()


main()
