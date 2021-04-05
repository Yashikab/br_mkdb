from datetime import date

import pytest

from domain.model.info import (
    HoldRaceInfo,
    ProgramCommonInfo,
    ProgramPlayerInfo,
)
from infrastructure.repository import MysqlProgramInfoRepositoryImpl

from ._common import CommonMethod


@pytest.mark.run(order=3)
class TestProgramInfoRepository:
    __common = CommonMethod()
    __pir = MysqlProgramInfoRepositoryImpl()
    __common_table_name: str = "raceinfo_tb"
    __player_table_name: str = "program_tb"
    __ri_col_set = {"race_id", "datejyo_id"}.union(
        set(ProgramCommonInfo.__annotations__.keys())
    )

    __pr_col_set = {"waku_id", "race_id"}.union(
        set(ProgramPlayerInfo.__annotations__.keys())
    )

    @pytest.fixture(scope="class", autouse=True)
    def preparation(self):
        self.__pir.create_table_if_not_exists()

    @pytest.mark.parametrize(
        "tb_name, col_set",
        [
            (__common_table_name, __ri_col_set),
            (__player_table_name, __pr_col_set),
        ],
    )
    def test_create_table(self, tb_name, col_set):
        get_set = self.__common.get_columns(tb_name)
        assert get_set == col_set

    # def test_save_data(self):
    #     holdraceinfo_sample = HoldRaceInfo(
    #         date(2020, 1, 1), "サンプル場1", 1, "進行状況", 5
    #     )

    #     self.__rir.save_info([holdraceinfo_sample])
    #     res_tpl = self.__common.get_targetdata(
    #         self.__table_name, "datejyo_id", "2020010101", self.__col_list
    #     )
    #     expected_tpl = (2020010101, date(2020, 1, 1), 1, "サンプル場1", "進行状況", 5)
    #     assert res_tpl == expected_tpl
