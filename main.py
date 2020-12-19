from time import sleep
from datetime import datetime
from cli import google_trend_cli, dot
from merge import merge_week, merge_day

def main():
    print(f'\n-----{datetime.now()}-----')
    print('\n-----若要背景執行大量資料爬蟲，請將系統 *螢幕保護 或 *休眠關閉，否則可能造成資訊中斷而損失資料-----')
    dot() 
    geo = 'TW' if str(
        input('\n-----搜索區域：預設台灣(y) / 更改區域(n)-----\n')
    ) in 'yY' else str(
        input('-----請輸入區域英文縮寫 (全球: Global, 其他地區自行估狗)-----\n')
    )
    daily = bool(input('\n-----是否需要日資料? (y/n)-----\n') in 'yY')
    while True:
        if not google_trend_cli(geo=geo, daily=daily): break
    merge_week(geo=geo, new_folder='merged')
    if daily: merge_day(new_folder='merged')
    print('系統將在 2 秒後自動關閉視窗，或是手動點擊右上角離開視窗 ···')
    sleep(1)

main()