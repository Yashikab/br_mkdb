# python 3.7.5
# coding: utf-8
import pytest
from module.getdata import OfficialProgram, OfficialChokuzen


class TestOfficialProgram:
    """
    番組表\n
    2020 4月8日 浜名湖(06) 3レースの情報でテスト\n
    http://boatrace.jp/owpc/pc/race/racelist?rno=3&jcd=06&hd=20200408 \n
    """
    # 選手番組情報の取得のための前処理
    @pytest.fixture(scope='class')
    def programinfo(self):
        """
        テスト用前処理
        公式サイトの番組表から選手欄の情報を選手毎に抜くテスト

        """
        # 3R
        self.race_no = 3
        # place : hamanako 06
        self.jyo_code = 6
        # day 2020/04/08
        self.day = 20200408

        op = OfficialProgram(self.race_no, self.jyo_code, self.day)
        # 各行呼び出し可能
        sample_info = []
        for i in range(1, 7):
            sample_info.append(op.getplayerinfo2dict(row=i))

        return sample_info

    # 公式番組表に関するテスト
    @pytest.mark.parametrize("target, idx, expected", [
        ('name', 0, "鈴木裕隆"),
        ('name', 1, "小林晋"),
        ('id', 0, 4231),
        ('id', 1, 4026),
        ('level', 0, 'B1'),
        ('level', 1, 'B1'),
        ('home', 0, '愛知'),
        ('home', 1, '東京'),
        ('birth_place', 0, '愛知'),
        ('birth_place', 1, '東京'),
        ('age', 0, 36),
        ('age', 1, 42),
        ('weight', 0, 57.0),
        ('weight', 1, 53.9),
        ('num_F', 0, 0),
        ('num_F', 1, 0),
        ('num_L', 0, 0),
        ('num_L', 1, 0),
        ('avg_ST', 0, 0.21),
        ('avg_ST', 1, 0.20),
        ('all_1rate', 0, 4.81),
        ('all_1rate', 1, 4.24),
        ('all_2rate', 0, 29.47),
        ('all_2rate', 1, 20.34),
        ('all_3rate', 0, 46.32),
        ('all_3rate', 1, 32.20),
        ('local_1rate', 0, 5.00),
        ('local_1rate', 1, 4.04),
        ('local_2rate', 0, 33.33),
        ('local_2rate', 1, 17.39),
        ('local_3rate', 0, 60.00),
        ('local_3rate', 1, 34.78),
        ('motor_no', 0, 23),
        ('motor_no', 1, 21),
        ('motor_2rate', 0, 54.66),
        ('motor_2rate', 1, 27.00),
        ('motor_3rate', 0, 72.46),
        ('motor_3rate', 1, 46.84),
        ('boat_no', 0, 34),
        ('boat_no', 1, 73),
        ('boat_2rate', 0, 15.05),
        ('boat_2rate', 1, 32.32),
        ('boat_3rate', 0, 33.33),
        ('boat_3rate', 1, 52.53)
    ])
    def test_p_inf_program(self, target, idx, expected, programinfo):
        assert programinfo[idx][target] == expected


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
        och = OfficialChokuzen(self.race_no, self.jyo_code, self.day)
        return och

    @pytest.fixture(scope='class')
    def p_chokuzen(self, calloch):
        # 1行目
        p_chokuzen = []
        for i in range(1, 7):
            p_chokuzen.append(calloch.getplayerinfo2dict(row=i))

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
        ('tenji_T', 0, 6.63),
        ('tenji_T', 5, 6.64),
        ('tilt', 0, -0.5),
        ('tilt', 5, -0.5),
        ('tenji_C', 0, 1),
        ('tenji_C', 5, 4),
        ('tenji_ST', 0, 0.14),
        ('tenji_ST', 2, -0.04),
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
