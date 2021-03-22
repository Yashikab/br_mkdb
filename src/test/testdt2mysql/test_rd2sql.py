# python 3.7.5
# coding: utf-8
"""
raceinfo2sqlテスト
"""
import pytest

from domain.model.info import ProgramCommonInfo, ProgramPlayerInfo
from infrastructure.dt2sql import RaceData2sql

from ..common import CommonMethod


@pytest.mark.run(order=3)
class TestRaceInfo2sql(CommonMethod):
    # 先に実行する
    __target_date = 20200512
    __jyo_cd = 21
    __race_no = 1
    __rd2sql = RaceData2sql()

    @pytest.fixture(scope="class", autouse=True)
    def insertdata(self):
        self.__rd2sql.insert2table(
            date=self.__target_date,
            jyo_cd_list=[self.__jyo_cd],
            raceno_dict={
                self.__jyo_cd: range(self.__race_no, self.__race_no + 1)
            },
        )

    ri_col_set = {"race_id", "datejyo_id"}.union(
        set(ProgramCommonInfo.__annotations__.keys())
    )

    pr_col_set = {"waku_id", "race_id"}.union(
        set(ProgramPlayerInfo.__annotations__.keys())
    )

    race_id = f"{__target_date}{__jyo_cd:02}{__race_no:02}"
    race_col_list = ["race_id", "grade", "race_kyori"]
    race_expected = (int(race_id), "is-G1b", 1800)
    waku_id = f"{__target_date}{__jyo_cd:02}{__race_no:02}1"
    waku_col_list = ["waku_id", "id", "all_1rate", "boat_2rate"]
    waku_expected = (int(waku_id), 4713, 6.72, 18.18)

    @pytest.mark.parametrize(
        "tb_nm, id_nm, t_id, col_list, expected",
        [
            ("raceinfo_tb", "race_id", race_id, race_col_list, race_expected),
            ("program_tb", "waku_id", waku_id, waku_col_list, waku_expected),
        ],
    )
    def test_insert2table(self, tb_nm, id_nm, t_id, col_list, expected):
        res_tpl = super().get_targetdata(tb_nm, id_nm, t_id, col_list)
        assert res_tpl == expected
