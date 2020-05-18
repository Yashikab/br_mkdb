# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""

import pytest
from module import getdata


class TestOfficialChokuzen:
    '''
    2020 4月8日 浜名湖(06) 9レースの情報でテスト\n
    直前情報\n
    枠なりじゃないF処理を見たいので9レースでの実行\n
    http://boatrace.jp/owpc/pc/race/beforeinfo?rno=9&jcd=06&hd=20200408
    '''

    # 選手直前情報取得のための前処理
    @pytest.fixture(scope='module')
    def calloch(self):
        # 5R
        self.race_no = 9
        # place : hamanako 06
        self.jyo_code = 6
        # day 2020/04/08
        self.day = 20200408
        och = getdata.OfficialChokuzen(
            self.race_no, self.jyo_code, self.day)
        return och

    @pytest.fixture(scope='class')
    def p_chokuzen(self, calloch):
        # 1行目
        p_chokuzen = []
        for i in range(1, 7):
            p_chokuzen.append(calloch.getplayerinfo2dict(waku=i))

        return p_chokuzen

    # 直前情報の取得
    # 選手
    # 1行目と6行目みてるので注意
    @pytest.mark.parametrize("target, idx, expected", [
        ('name', 0, "一瀬明"),
        ('name', 5, "濱本優一"),
        ('weight', 0, 51.6),
        ('weight', 5, 49.5),
        ('chosei_weight', 0, 0.0),
        ('chosei_weight', 5, 1.5),
        ('tenji_time', 0, 6.63),
        ('tenji_time', 5, 6.64),
        ('tilt', 0, -0.5),
        ('tilt', 5, -0.5),
        ('tenji_course', 0, 1),
        ('tenji_course', 5, 4),
        ('tenji_st', 0, 0.14),
        ('tenji_st', 2, -0.04),
    ])
    def test_p_chokuzen(self, target, idx, expected, p_chokuzen):
        assert p_chokuzen[idx][target] == expected

    # 会場コンディション
    @pytest.mark.parametrize("target, expected", [
        ('temp', 17.0),
        ('weather', '晴'),
        ('wind_v', 4),  # m
        ('w_temp', 16.0),
        ('wave', 2),  # cm
        ('wind_dr', 13)
    ])
    def test_jyo_chokuzen(self, target, expected, calloch):
        # cnd_chokuzen = 直前のコンディションの意
        cnd_chokuzen = calloch.getcondinfo2dict()
        assert cnd_chokuzen[target] == expected