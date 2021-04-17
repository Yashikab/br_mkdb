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
    __rir = MysqlResultInfoRepositoryImpl()
    __common_table_name: str = "race_result_tb"
    __player_table_name: str = "player_result_tb"
    __common_cols = ["race_id", "datejyo_id"]

    for var_name, var_type in ResultCommonInfo.__annotations__.items():
        if var_type == WeatherInfo:
            for weather_name in WeatherInfo.__annotations__.keys():
                __common_cols.append(weather_name)
        else:
            __common_cols.append(var_name)
    __common_cols = set(__common_cols)
    __p_cols = {"waku_id", "race_id"}.union(
        set(ResultPlayerInfo.__annotations__.keys())
    )

    @pytest.fixture(scope="class", autouse=True)
    def preparation(self):
        self.__rir.create_table_if_not_exists()

    @pytest.mark.parametrize(
        "tb_name, col_set",
        [
            (__common_table_name, __common_cols),
            (__player_table_name, __p_cols),
        ],
    )
    def test_create_table(self, tb_name, col_set):
        get_set = self.__common.get_columns(tb_name)
        assert get_set == col_set

    def test_save_data(self):
        weather_info = WeatherInfo(23.4, "晴れ", 4, 18.3, 2, 6)
        common_info = ResultCommonInfo(
            weather_info,
            "1, 3",
            True,
            "逃げ",
            "変換艇あり",
            3450,
            14,
            2480,
            3,
            1500,
            3,
            510,
            2,
            150,
        )
        player_info = ResultPlayerInfo(1, 1, "サンプル太郎", 1, 6.54, 1, 0.14)
        result_info = ResultInfo(
            date(2020, 1, 1), 1, 4, common_info, [player_info]
        )

        self.__rir.save_info([result_info])
        common_check_cols = [
            "race_id",
            "datejyo_id",
            "temp",
            "weather",
            "henkantei_list",
            "payout_3tan",
        ]
        res_common_tpl = self.__common.get_targetdata(
            self.__common_table_name,
            "race_id",
            "202001010104",
            common_check_cols,
        )
        ex_common_cols = (202001010104, 2020010101, 23.4, "晴れ", "1, 3", 3450)

        player_check_cols = ["waku_id", "race_id", "rank", "name", "racetime"]
        res_player_tpl = self.__common.get_targetdata(
            self.__player_table_name,
            "waku_id",
            "2020010101041",
            player_check_cols,
        )
        ex_player_cols = (2020010101041, 202001010104, 1, "サンプル太郎", 6.54)

        assert res_common_tpl == ex_common_cols
        assert res_player_tpl == ex_player_cols
