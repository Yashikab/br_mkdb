# python 3.7.5
# coding: utf-8
"""
chokuseninfoo2sqlテスト
"""
import pytest

from domain.model.info import ResultCommonInfo, ResultPlayerInfo
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
        self.__res2sql.insert2table(
            date=self.__target_date,
            jyo_cd_list=[self.__jyo_cd],
            raceno_dict={
                self.__jyo_cd: range(self.__race_no, self.__race_no+1)},
        )

    rr_col_set = {'race_id', 'datejyo_id'}.union(
        set(ResultCommonInfo.__annotations__.keys())
    )
    rp_col_set = {'waku_id', 'race_id'}.union(
        set(ResultPlayerInfo.__annotations__.keys()))

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
    waku_col_list = ["waku_id", "rank", "racetime", "st_time"]
    waku_ex = (
        int(waku_id),
        -1,
        -1,
        0.11
    )

    @ pytest.mark.parametrize("tb_nm, id_nm, t_id, col_list, expected", [
        ("race_result_tb", "race_id", race_id, race_col_list, race_expected),
        ("player_result_tb", "waku_id", waku_id, waku_col_list, waku_ex)
    ])
    def test_insert2table(self, tb_nm, id_nm, t_id, col_list, expected):
        res_tpl = super().get_targetdata(
            tb_nm,
            id_nm,
            t_id,
            col_list
        )
        assert res_tpl == expected
