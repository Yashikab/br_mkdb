from datetime import date

import pytest

from domain.model.info import (
    ResultCommonInfo,
    ResultInfo,
    ResultPlayerInfo,
    WeatherInfo,
)
from infrastructure.repository import MysqlResultInfoRepositoryImpl

from ._common import CommonMethod


@pytest.mark.run(order=5)
class TestResultInfoRepository:
    __common = CommonMethod()
    __pir = MysqlResultInfoRepositoryImpl()
    __common_table_name: str = "race_result_tb"
    __player_table_name: str = "player_result_tb"
    __common_cols = ["race_id", "datejyo_id"]

    for var_name, var_type in ResultCommonInfo.__annotations__.keys():
        if var_type == WeatherInfo:
            for weather_name in WeatherInfo.__annotations__.keys():
                __common_cols.append(weather_name)


#
#    __pr_col_set = {"waku_id", "race_id"}.union(
#        set(ProgramPlayerInfo.__annotations__.keys())
#    )
#
#    @pytest.fixture(scope="class", autouse=True)
#    def preparation(self):
#        self.__pir.create_table_if_not_exists()
#
#    @pytest.mark.parametrize(
#        "tb_name, col_set",
#        [
#            (__common_table_name, __ri_col_set),
#            (__player_table_name, __pr_col_set),
#        ],
#    )
#    def test_create_table(self, tb_name, col_set):
#        get_set = self.__common.get_columns(tb_name)
#        assert get_set == col_set
#
#    def test_save_data(self):
#        p_common_info = ProgramCommonInfo(
#            "さんぷる大会", "is-G1b", "予選", 1800, False, True
#        )
#        p_player_info = ProgramPlayerInfo(
#            1,
#            "サンプル太郎",
#            8400,
#            "B1",
#            "宮城",
#            "宮城",
#            48,
#            84.5,
#            1,
#            0,
#            0.25,
#            0.20,
#            0.30,
#            0.40,
#            0.25,
#            0.35,
#            0.45,
#            50,
#            0.40,
#            0.5,
#            41,
#            0.41,
#            0.42,
#        )
#        program_info = ProgramInfo(
#            date(2020, 1, 1), 1, 4, p_common_info, [p_player_info]
#        )
#
#        self.__pir.save_info([program_info])
#        common_check_cols = [
#            "race_id",
#            "datejyo_id",
#            "taikai_name",
#            "grade",
#            "is_shinnyukotei",
#        ]
#        res_common_tpl = self.__common.get_targetdata(
#            self.__common_table_name,
#            "race_id",
#            "202001010104",
#            common_check_cols,
#        )
#        ex_common_cols = (202001010104, 2020010101, "さんぷる大会", "is-G1b", 1)
#
#        player_check_cols = ["waku_id", "race_id", "name", "age"]
#        res_player_tpl = self.__common.get_targetdata(
#            self.__player_table_name,
#            "waku_id",
#            "2020010101041",
#            player_check_cols,
#        )
#        ex_player_cols = (2020010101041, 202001010104, "サンプル太郎", 48)
#
#        assert res_common_tpl == ex_common_cols
#        assert res_player_tpl == ex_player_cols
#