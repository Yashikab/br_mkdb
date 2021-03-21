# python 3.7.5
# coding: utf-8
"""
chokuseninfoo2sqlテスト
"""
import pytest

from domain.model.info import ChokuzenPlayerInfo, WeatherInfo
from infrastructure.dt2sql import ChokuzenData2sql

from ..common import CommonMethod

WAIT = 0.5


@pytest.mark.run(order=4)
class TestChokuzenInfo2sql(CommonMethod):
    __target_date = 20200512
    __jyo_cd = 21
    __race_no = 1
    __ci2sql = ChokuzenData2sql()

    @pytest.fixture(scope="class", autouse=True)
    def insertdata(self):
        self.__ci2sql.insert2table(
            date=self.__target_date,
            jyo_cd_list=[self.__jyo_cd],
            raceno_dict={self.__jyo_cd: range(self.__race_no, self.__race_no + 1)},
        )

    cc_col_set = {"race_id", "datejyo_id"}.union(
        set(WeatherInfo.__annotations__.keys())
    )
    cp_col_set = {"waku_id", "race_id"}.union(
        set(ChokuzenPlayerInfo.__annotations__.keys())
    )

    race_id = f"{__target_date}{__jyo_cd:02}{__race_no:02}"
    cond_col_list = ["race_id", "temp", "weather", "wave"]
    cond_expected = (int(race_id), 24.0, "晴", 5)
    waku_id = f"{__target_date}{__jyo_cd:02}{__race_no:02}1"
    waku_col_list = [
        "waku_id",
        "chosei_weight",
        "tenji_time",
        "tilt",
        "tenji_course",
        "tenji_st",
    ]
    waku_ex = (int(waku_id), 0.0, 6.91, -0.5, 2, 0.11)

    @pytest.mark.parametrize(
        "tb_nm, id_nm, t_id, col_list, expected",
        [
            ("chokuzen_cond_tb", "race_id", race_id, cond_col_list, cond_expected),
            ("chokuzen_player_tb", "waku_id", waku_id, waku_col_list, waku_ex),
        ],
    )
    def test_insert2table(self, tb_nm, id_nm, t_id, col_list, expected):
        res_tpl = super().get_targetdata(tb_nm, id_nm, t_id, col_list)
        assert res_tpl == expected
