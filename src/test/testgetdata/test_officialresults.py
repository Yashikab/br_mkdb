# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""

import pytest
from module import getdata


class TestOfficialResults:
    '''
    2020 4月8日 浜名湖(06) 9レースの情報でテスト\n
    http://boatrace.jp/owpc/pc/race/raceresult?rno=12&jcd=06&hd=20200410
    '''
    # 選手直前情報取得のための前処理
    @pytest.fixture(scope='class')
    def racerls(self):
        # 5R
        self.race_no = 12
        # place : hamanako 06
        self.jyo_code = 6
        # day 2020/04/08
        self.day = 20200410
        ors = getdata.OfficialResults(
            self.race_no, self.jyo_code, self.day)
        # 各行呼び出し可能
        racerls = []
        for i in range(1, 7):
            racerls.append(ors.getplayerresult2dict(waku=i))
        return racerls

    # 名前
    @pytest.mark.parametrize("waku, target, expected", [
        (1, 'name', '守田俊介'),
        (6, 'name', '森竜也'),
        (1, 'no', 3721),
        (6, 'no', 3268),
        (1, 'rank', -1),
        (6, 'rank', 1),
        (1, 'racetime', -1),
        (6, 'racetime', 115.8),
        (2, 'racetime', 118.4),
        (1, 'course', 1),
        (6, 'course', 3),
    ])
    def test_getplayerresult2dict(self, waku, target, expected, racerls):
        # listなのでwakuが1つずれる
        assert racerls[waku - 1][target] == expected
