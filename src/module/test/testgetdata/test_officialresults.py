# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""

import pytest
from module import getdata


class TestOfficialResults:
    '''
    2020 4月10日 浜名湖(06) 9レースの情報でテスト\n
    http://boatrace.jp/owpc/pc/race/raceresult?rno=9&jcd=06&hd=20200410
    '''
    # 選手直前情報取得のための前処理
    @pytest.fixture(scope='class')
    def getcls(self):
        # 5R
        self.race_no = 9
        # place : hamanako 06
        self.jyo_code = 6
        # day 2020/04/08
        self.day = 20200410
        ors = getdata.OfficialResults(
            self.race_no, self.jyo_code, self.day)
        return ors

    # 選手結果
    @pytest.fixture(scope='class')
    def playerrls(self, getcls):
        # 各行呼び出し可能
        p_rls = []
        for i in range(1, 7):
            p_rls.append(getcls.getplayerresult2dict(waku=i))
        return p_rls

    @pytest.mark.parametrize("waku, target, expected", [
        (1, 'name', '萬正嗣'),
        (6, 'name', '川合理司'),
        (1, 'no', 4177),
        (6, 'no', 3839),
        (1, 'rank', -1),
        (6, 'rank', 4),
        (1, 'racetime', -1),
        (6, 'racetime', 114.5),
        (2, 'racetime', -1),
        (1, 'course', 1),
        (6, 'course', 6),
        (1, 'st_time', -0.02),
        (6, 'st_time', 0.10)
    ])
    def test_getplayerresult2dict(self, waku, target, expected, playerrls):
        # listなのでwakuが1つずれる
        assert playerrls[waku - 1][target] == expected

    # レース結果
    @pytest.fixture(scope='class')
    def racerls(self, getcls):
        return getcls.getraceresult2dict()

    # 会場コンディション
    @pytest.mark.parametrize("target, expected", [
        ('temp', 16.0),
        ('weather', '晴'),
        ('wind_v', 6),  # m
        ('w_temp', 16.0),
        ('wave', 4),  # cm
        ('wind_dr', 3),
        ('henkantei', [1]),
        ('is_henkan', True),
        ('kimarite', '恵まれ'),
        ('biko', '【返還艇あり】'),
        ('payout_3tan', 1880),
        ('popular_3tan', 8),
        ('payout_3fuku', 500),
        ('popular_3fuku', 3),
        ('payout_2tan', 310),
        ('popular_2tan', 2),
        ('payout_2fuku', 150),
        ('popular_2fuku', 1),
        ('payout_1tan', 410),
    ])
    def test_raceresult2dict(self, target, expected, racerls):
        assert racerls[target] == expected
