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

    name_set1 = {'江戸川', '浜名湖', '常滑', '津',
                 '三国', '尼崎', '徳山', '下関',
                 '若松', '福岡', '大村'}
    name_set2 = {'多摩川', '浜名湖', '蒲郡', '常滑', '津',
                 '三国', '住之江', '丸亀', '児島',
                 '宮島', '芦屋', '福岡'}
    code_set2 = {5, 6, 7, 8, 9, 10, 12, 15, 16, 17, 21, 22}

    @pytest.mark.parametrize("date, expected", [
        (20200408, name_set1),
        (20110311, name_set2)
    ])
    def test_holdplace2strset(self, date, expected):
        ghp = getdata.GetHoldPlace(date)
        assert ghp.holdplace2strset() == expected

    @pytest.mark.parametrize("date, expected", [
        (20110311, code_set2)
    ])
    def test_holdplace2cdset(self, date, expected):
        ghp = getdata.GetHoldPlace(date)
        assert ghp.holdplace2cdset() == expected
