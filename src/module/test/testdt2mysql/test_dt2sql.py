# python 3.7.5
# coding: utf-8
"""
dt2sqlモジュール用単体テスト
実行順番があるので一つのファイルにまとめる
"""
import pytest
import time

from module.dt2sql import (
    JyoData2sql,
    RaceData2sql,
    ChokuzenData2sql,
    ResultData2sql,
    Odds2sql
)
from module.getdata import OfficialOdds
from .common import CommonMethod

WAIT = 0.5


class TestJyoData2sql(CommonMethod):
    __target_date = 20200512
    __jyo_cd = 20
    __jd2sql = JyoData2sql()
    __jd2sql.create_table_if_not_exists()
    __jd2sql.insert2table(date=__target_date)
    time.sleep(WAIT)

    def test_exist_table(self):
        # カラム名の一致でテスト
        get_set = super().get_columns2set('holdjyo_tb')

        expected_set = {'datejyo_id', 'holddate', 'jyo_cd',
                        'jyo_name', 'shinko', 'ed_race_no'}
        assert get_set == expected_set

    def test_insert2table(self):
        # idの情報を一つ取ってきて調べる
        tb_name = "holdjyo_tb"
        id_name = "datejyo_id"
        target_id = f"{self.__target_date}{self.__jyo_cd:02}"
        col_list = ["datejyo_id", "jyo_cd", "shinko", "ed_race_no"]
        res_tpl = super().getdata2tuple(
            tb_name,
            id_name,
            target_id,
            col_list
        )
        expected_tpl = (
            int(target_id),
            self.__jyo_cd,
            '中止順延',
            0
        )
        assert res_tpl == expected_tpl


class TestRaceInfo2sql(CommonMethod):
    # 先に実行する
    target_date = 20200512
    jyo_cd = 21
    race_no = 1
    __rd2sql = RaceData2sql()
    __rd2sql.create_table_if_not_exists()
    __rd2sql.insert2table(
        date=target_date,
        jyo_cd=jyo_cd,
        race_no=race_no)
    time.sleep(WAIT)

    ri_col_set = {'race_id', 'datejyo_id', 'taikai_name',
                  'grade', 'race_type', 'race_kyori',
                  'is_antei', 'is_shinnyukotei'}
    pr_col_set = {'waku_id', 'race_id',
                  'p_name', 'p_id', 'p_level', 'p_home',
                  'p_birthplace', 'p_age', 'p_weight',
                  'p_num_f', 'p_num_l', 'p_avg_st',
                  'p_all_1rate', 'p_all_2rate', 'p_all_3rate',
                  'p_local_1rate', 'p_local_2rate', 'p_local_3rate',
                  'motor_no', 'motor_2rate', 'motor_3rate',
                  'boat_no', 'boat_2rate', 'boat_3rate'}

    @pytest.mark.parametrize("tb_name, col_set", [
        ('raceinfo_tb', ri_col_set),
        ('program_tb', pr_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns2set(tb_name)
        assert get_set == col_set

    race_id = f"{target_date}{jyo_cd:02}{race_no:02}"
    race_col_list = ["race_id", "grade", "race_kyori"]
    race_expected = (
        int(race_id),
        'is-G1b',
        1800
    )
    waku_id = f"{target_date}{jyo_cd:02}{race_no:02}1"
    waku_col_list = ["waku_id", "p_id", "p_all_1rate", "boat_2rate"]
    waku_expected = (
            int(waku_id),
            4713,
            6.72,
            18.18
        )

    @pytest.mark.parametrize("tb_nm, id_nm, t_id, col_list, expected", [
        ("raceinfo_tb", "race_id", race_id, race_col_list, race_expected),
        ("program_tb", "waku_id", waku_id, waku_col_list, waku_expected)
    ])
    def test_insert2table(self, tb_nm, id_nm, t_id, col_list, expected):
        res_tpl = super().getdata2tuple(
            tb_nm,
            id_nm,
            t_id,
            col_list
        )
        assert res_tpl == expected


class TestChokuzenInfo2sql(CommonMethod):
    target_date = 20200512
    jyo_cd = 21
    race_no = 1
    __ci2sql = ChokuzenData2sql()
    __ci2sql.create_table_if_not_exists()
    __ci2sql.insert2table(target_date, jyo_cd, race_no)
    time.sleep(WAIT)

    cc_col_set = {'race_id', 'datejyo_id',
                  'temp', 'weather', 'wind_v',
                  'w_temp', 'wave', 'wind_dr'}
    cp_col_set = {'waku_id', 'race_id', 'p_name',
                  'p_weight', 'p_chosei_weight',
                  'p_tenji_time', 'p_tilt',
                  'p_tenji_course', 'p_tenji_st'}

    @pytest.mark.parametrize("tb_name, col_set", [
        ('chokuzen_cond_tb', cc_col_set),
        ('chokuzen_player_tb', cp_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns2set(tb_name)
        assert get_set == col_set

    race_id = f"{target_date}{jyo_cd:02}{race_no:02}"
    cond_col_list = ["race_id", "temp", "weather", "wave"]
    cond_expected = (
        int(race_id),
        24.0,
        '晴',
        5
    )
    waku_id = f"{target_date}{jyo_cd:02}{race_no:02}1"
    waku_col_list = ["waku_id", "p_chosei_weight", "p_tenji_time",
                     "p_tilt", "p_tenji_course", "p_tenji_st"]
    waku_ex = (
            int(waku_id),
            0.0,
            6.91,
            -0.5,
            2,
            0.11
        )

    @pytest.mark.parametrize("tb_nm, id_nm, t_id, col_list, expected", [
        ("chokuzen_cond_tb", "race_id", race_id, cond_col_list, cond_expected),
        ("chokuzen_player_tb", "waku_id", waku_id, waku_col_list, waku_ex)
    ])
    def test_insert2table(self, tb_nm, id_nm, t_id, col_list, expected):
        res_tpl = super().getdata2tuple(
            tb_nm,
            id_nm,
            t_id,
            col_list
        )
        assert res_tpl == expected


class TestResult2sql(CommonMethod):
    target_date = 20200512
    jyo_cd = 21
    race_no = 1
    __res2sql = ResultData2sql()
    __res2sql.create_table_if_not_exists()
    __res2sql.insert2table(target_date, jyo_cd, race_no)
    time.sleep(WAIT)

    rr_col_set = {'race_id', 'datejyo_id', 'temp', 'weather', 'wind_v',
                  'w_temp', 'wave', 'wind_dr',
                  'henkantei_list', 'is_henkan', 'kimarite',
                  'biko', 'payout_3tan', 'popular_3tan',
                  'payout_3fuku', 'popular_3fuku',
                  'payout_2tan', 'popular_2tan',
                  'payout_2fuku', 'popular_2fuku', 'payout_1tan'}
    rp_col_set = {'waku_id', 'race_id', 'p_rank', 'p_name',
                  'p_id', 'p_racetime', 'p_course', 'p_st_time'}

    @pytest.mark.parametrize("tb_name, col_set", [
        ('race_result_tb', rr_col_set),
        ('p_result_tb', rp_col_set)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns2set(tb_name)
        assert get_set == col_set

    race_id = f"{target_date}{jyo_cd:02}{race_no:02}"
    race_col_list = ["race_id", "temp", "kimarite", "biko",
                     "payout_3tan", "popular_3tan"]
    race_expected = (
        int(race_id),
        21.0,
        '逃げ',
        '',
        4000,
        14
    )
    # 5号艇を見る
    waku_id = f"{target_date}{jyo_cd:02}{race_no:02}5"
    waku_col_list = ["waku_id", "p_rank", "p_racetime", "p_st_time"]
    waku_ex = (
            int(waku_id),
            -1,
            -1,
            0.11
        )

    @pytest.mark.parametrize("tb_nm, id_nm, t_id, col_list, expected", [
        ("race_result_tb", "race_id", race_id, race_col_list, race_expected),
        ("p_result_tb", "waku_id", waku_id, waku_col_list, waku_ex)
    ])
    def test_insert2table(self, tb_nm, id_nm, t_id, col_list, expected):
        res_tpl = super().getdata2tuple(
            tb_nm,
            id_nm,
            t_id,
            col_list
        )
        assert res_tpl == expected


class TestOdds2sql(CommonMethod):
    target_date = 20200512
    jyo_cd = 21
    race_no = 1

    # load Official Odds for get keys
    __ood = OfficialOdds

    __od2sql = Odds2sql()
    __od2sql.create_table_if_not_exists()
    __od2sql.insert2table(target_date, jyo_cd, race_no)
    time.sleep(WAIT)

    key_set = {'race_id'}
    three_rentan_key = key_set.union(set(__ood.rentan_keylist(3)))
    three_renfuku_key = key_set.union(set(__ood.renfuku_keylist(3)))
    two_rentan_key = key_set.union(set(__ood.rentan_keylist(2)))
    two_renfuku_key = key_set.union(set(__ood.renfuku_keylist(2)))
    one_rentan_key = key_set.union(set(__ood.rentan_keylist(1)))

    @pytest.mark.parametrize("tb_name, col_set", [
        ('odds_3tan_tb', three_rentan_key),
        ('odds_3fuku_tb', three_renfuku_key),
        ('odds_2tan_tb', two_rentan_key),
        ('odds_2fuku_tb', two_renfuku_key),
        ('odds_1tan_tb', one_rentan_key)
    ])
    def test_exist_table_raceinfo(self, tb_name, col_set):
        # カラム名の一致でテスト
        get_set = super().get_columns2set(tb_name)
        assert get_set == col_set

    race_id = int(f"{target_date}{jyo_cd:02}{race_no:02}")
    three_tan_col_list = ["race_id", "`1-2-3`", "`4-5-6`", "`6-5-4`"]
    three_tan_expected = (race_id, 31.9, 157.4, 544.4)
    three_fuku_col_list = ["race_id", "`1-2-3`", "`2-3-4`", "`4-5-6`"]
    three_fuku_expected = (race_id, 7.6, 24.4, 38.3)
    two_tan_col_list = ["race_id", "`1-2`", "`4-5`", "`6-5`"]
    two_tan_expected = (race_id, 10.2, 28.0, 108.3)
    two_fuku_col_list = ["race_id", "`1-2`", "`2-3`", "`4-5`"]
    two_fuku_expected = (race_id, 7.9, 14.7, 11.6)
    one_tan_col_list = ["race_id", "`1`", "`5`"]
    one_tan_expected = (race_id, 2.7, 1.8)

    @pytest.mark.parametrize("tb_nm, col_list, expected", [
        ("odds_3tan_tb", three_tan_col_list, three_tan_expected),
        ("odds_3fuku_tb", three_fuku_col_list, three_fuku_expected),
        ("odds_2tan_tb", two_tan_col_list, two_tan_expected),
        ("odds_2fuku_tb", two_fuku_col_list, two_fuku_expected),
        ("odds_1tan_tb", one_tan_col_list, one_tan_expected),
    ])
    def test_insert2table(self, tb_nm, col_list, expected):
        res_tpl = super().getdata2tuple(
            tb_nm,
            "race_id",
            self.race_id,
            col_list
        )
        assert res_tpl == expected
