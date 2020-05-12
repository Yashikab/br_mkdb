# python 3.7.5
# coding: utf-8
"""
一定期間の過去のデータを取得．
最新データ取得用プログラムではない．
スクレイピングを行い, mysqlにデータを格納
"""
from logging import getLogger
from datetime import datetime

from module.getdata import DateList as dtl
from module.getdata import GetHoldPlacePast


logger = getLogger(__name__)


def main():
    # TODO: データを取得する期間を決める
    # オッズデータが存在する最初の日
    start_date = datetime(2017, 3, 8)
    # とりあえず2年間
    end_date = datetime(2019, 3, 8)
    # 日付リスト取得
    datelist = dtl.datelist(start_date, end_date)

    for target_date in datelist:
        # TODO: 対象日のレース情報を取得
        ghpp = GetHoldPlacePast(target_date)
        holdplace_name_set = ghpp.holdplace2strset()
        holdplace_code_set = ghpp.holdplace2cdset()

    # TODO: 各会場，レースにおける情報の取得
    # TODO: 取得した情報をMYSQLに格納する
    pass
