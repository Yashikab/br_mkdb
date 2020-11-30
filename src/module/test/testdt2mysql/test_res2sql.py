# python 3.7.5
# coding: utf-8
"""
chokuseninfoo2sqlテスト
"""
import pytest

from module.dt2sql import ResultData2sql
from ..common import CommonMethod


@pytest.mark.run(order=5)
class TestResult2sql(CommonMethod):
    __target_date = 20200512
    __jyo_cd = 21
    __race_no = 1
    __res2sql = ResultData2sql()

    @pytest.fixture(scope='class', autouse=True)
    def insertdata(self):
        self.__res2sql.create_table_if_not_exists()
        self.__res2sql.insert2table(
            date=self.__target_date,
            jyo_cd_list=[self.__jyo_cd],
            raceno_dict={
                self.__jyo_cd: range(self.__race_no, self.__race_no+1)},
        )

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

    race_id = f"{__target_date}{__jyo_cd:02}{__race_no:02}"
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
    waku_id = f"{__target_date}{__jyo_cd:02}{__race_no:02}5"
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
