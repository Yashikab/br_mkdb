# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""

import pytest

from infrastructure.getdata_lxml import OfficialProgram
from infrastructure.getter import GetParserContent

from ..common import CommonMethod


class TestOfficialProgram(CommonMethod):
    """
    番組表\n
    2020 4月8日 浜名湖(06) 3レースの情報でテスト\n
    http://boatrace.jp/owpc/pc/race/racelist?rno=3&jcd=06&hd=20200408 \n
    """
    @pytest.fixture(scope='function')
    def loadcls(self, mocker):
        """
        テスト用前処理
        公式サイトの番組表から選手欄の情報を選手毎に抜くテスト

        """
        # 3R
        race_no = 3
        # place : hamanako 06
        jyo_code = 6
        # day 2020/04/08
        date = 20200408

        # mocking
        filepath = super().get_html_filepath(
            f"pro_{date}{jyo_code}{race_no}.html"
        )
        lx_content = GetParserContent.file_to_content(filepath, "lxml")
        mocker.patch.object(
            GetParserContent, "url_to_content",
            return_value=lx_content)

        op = OfficialProgram(
            race_no, jyo_code, date)
        return op

    # 選手番組情報の取得のための前処理
    @pytest.fixture(scope='function')
    def programinfo(self, loadcls):

        # 各行呼び出し可能
        programinfo = []
        for i in range(1, 7):
            programinfo.append(loadcls.getplayerinfo2dict(waku=i))

        return programinfo

    @pytest.fixture(scope='function')
    def raceinfo(self, loadcls):
        return loadcls.getcommoninfo2dict()

    # 公式番組表に関するテスト
    @pytest.mark.parametrize("waku, idx, expected", [
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
    def test_p_inf_program(self, waku, idx, expected, programinfo):
        assert programinfo[idx][waku] == expected

    @pytest.mark.parametrize("idx, expected", [
        ('taikai_name', 'スポーツ報知　ビクトリーカップ'),
        ('grade', 'is-ippan'),
        ('race_type', '予選'),
        ('race_kyori', 1800),
        ('is_antei', False),
        ('is_shinnyukotei', False)
    ])
    def test_raceinfo(self, idx, expected, raceinfo):
        assert raceinfo[idx] == expected
