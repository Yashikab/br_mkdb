# python 3.7.5
# coding: utf-8
"""
raceinfo2sqlテスト
"""
import pytest
import time

from module.dt2sql import RaceData2sql
from .common import CommonMethod

WAIT = 0.5


@pytest.mark.run(order=3)
class TestRaceInfo2sql(CommonMethod):
    # 先に実行する
    __target_date = 20200512
    __jyo_cd = 21
    __race_no = 1
    __rd2sql = RaceData2sql()

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        self.__rd2sql.create_table_if_not_exists()
        self.__rd2sql.insert2table(
            date=self.__target_date,
            jyo_cd=self.__jyo_cd,
            race_no=self.__race_no)
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

    race_id = f"{__target_date}{__jyo_cd:02}{__race_no:02}"
    race_col_list = ["race_id", "grade", "race_kyori"]
    race_expected = (
        int(race_id),
        'is-G1b',
        1800
    )
    waku_id = f"{__target_date}{__jyo_cd:02}{__race_no:02}1"
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
