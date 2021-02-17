# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""
import pytest

from infrastructure.getdata_lxml import GetHoldPlacePast
from infrastructure.getter import GetParserContent

from ..common import CommonMethod


class TestGetHoldPlace(CommonMethod):
    """
    本日のレーステーブルから開催会場を取得
    URL: https://www.boatrace.jp/owpc/pc/race/index?hd=20110311
    """

    name_list1 = ['江戸川', '浜名湖', '常滑', '津',
                  '三国', '尼崎', '徳山', '下関',
                  '若松', '福岡', '大村']
    name_list2 = ['多摩川', '浜名湖', '蒲郡', '常滑', '津',
                  '三国', '住之江', '丸亀', '児島',
                  '宮島', '芦屋', '福岡']
    code_list2 = [5, 6, 7, 8, 9, 10, 12, 15, 16, 17, 21, 22]

    @pytest.mark.parametrize("date, expected", [
        (20200408, name_list1),
        (20110311, name_list2)
    ])
    def test_holdplace2strlist(self, date, expected, mocker):
        ghp = self._ghp(date, mocker)
        assert ghp.holdplace2strlist() == expected

    @pytest.mark.parametrize("date, expected", [
        (20110311, code_list2)
    ])
    def test_holdplace2cdlist(self, date, expected, mocker):
        ghp = self._ghp(date, mocker)
        assert ghp.holdplace2cdlist() == expected

    tama_info = {
        'shinko': '9R以降中止',
        'ed_race_no': 9
    }
    hama_info = {
        'shinko': '-',
        'ed_race_no': 12
    }

    @pytest.mark.parametrize("date, hp_name, expected", [
        (20110311, '多摩川', tama_info),
        (20110311, '浜名湖', hama_info)
    ])
    def test_holdinfo2dict(self, date, hp_name, expected, mocker):
        ghp = self._ghp(date, mocker)
        assert ghp.holdinfo2dict(hp_name) == expected

    def _ghp(self, date, mocker):
        """mock用に共通項にする"""
        filepath = super().get_html_filepath(f'ghp_{date}.html')
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(GetParserContent, "url_to_content",
                            return_value=lx_content)
        ghp = GetHoldPlacePast(date)
        return ghp
