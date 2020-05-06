# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""

import pytest
from module import getdata


class TestGetHoldPlace:
    """
    本日のレーステーブルから開催会場を取得
    URL: https://www.boatrace.jp/owpc/pc/race/index?hd=20200408
    """

    name_list1 = {'江戸川', '浜名湖', '常滑', '津',
                  '三国', '尼崎', '徳山', '下関',
                  '若松', '福岡', '大村'}
    name_list2 = {'多摩川', '浜名湖', '蒲郡', '常滑', '津',
                  '三国', '住之江', '丸亀', '児島',
                  '宮島', '芦屋', '福岡'}

    @pytest.mark.parametrize("date, expected", [
        (20200408, name_list1),
        (20110311, name_list2)
    ])
    def test_holdplace2strlist(self, date, expected):
        ghp = getdata.GetHoldPlace(date)
        assert ghp.holdplace2strset() == expected
