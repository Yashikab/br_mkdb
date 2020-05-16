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

    name_list1 = ['江戸川', '浜名湖', '常滑', '津',
                  '三国', '尼崎', '徳山', '下関',
                  '若松', '福岡', '大村']
    name_list2 = ['多摩川', '浜名湖', '蒲郡', '常滑', '津',
                  '三国', '住之江', '丸亀', '児島',
                  '宮島', '芦屋', '福岡']
    code_list2 = [5, 6, 7, 8, 9, 10, 12, 15, 16, 17, 21, 22]

    dict2 = {'多摩川': '9R以降中止',
             '浜名湖': '-',
             '蒲郡': '-',
             '常滑': '-',
             '津': '-',
             '三国': '-',
             '住之江': '-',
             '丸亀': '-',
             '児島': '-',
             '宮島': '-',
             '芦屋': '-',
             '福岡': '-'}
    possible_dict2 = {
        '多摩川': list(range(1, 9)),
        '浜名湖': list(range(1, 13)),
        '蒲郡': list(range(1, 13)),
        '常滑': list(range(1, 13)),
        '津': list(range(1, 13)),
        '三国': list(range(1, 13)),
        '住之江': list(range(1, 13)),
        '丸亀': list(range(1, 13)),
        '児島': list(range(1, 13)),
        '宮島': list(range(1, 13)),
        '芦屋': list(range(1, 13)),
        '福岡': list(range(1, 13))}

    # @pytest.fixture(scope='class')
    # def ghp(self):
    #     return getdata.GetHoldPlasePast()
    @pytest.mark.parametrize("date, expected", [
        (20200408, name_list1),
        (20110311, name_list2)
    ])
    def test_holdplace2strlist(self, date, expected):
        ghp = getdata.GetHoldPlacePast(date)
        assert ghp.holdplace2strlist() == expected

    @pytest.mark.parametrize("date, expected", [
        (20110311, code_list2)
    ])
    def test_holdplace2cdlist(self, date, expected):
        ghp = getdata.GetHoldPlacePast(date)
        assert ghp.holdplace2cdlist() == expected

    @pytest.mark.parametrize("date, expected", [
        (20110311, dict2)
    ])
    def test_shinkoinfodict(self, date, expected):
        ghp = getdata.GetHoldPlacePast(date)
        assert ghp.shinkoinfodict() == expected

    @pytest.mark.parametrize("date, expected", [
        (20110311, possible_dict2)
    ])
    def test_possibleraces(self, date, expected):
        ghp = getdata.GetHoldPlacePast(date)
        assert ghp.holdracedict() == expected
