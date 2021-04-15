from datetime import date

import pytest

from domain.model.info import ChokuzenInfo, ChokuzenPlayerInfo, WeatherInfo
from infrastructure.repository import MysqlChokuzenInfoRepositoryImpl

from ._common import CommonMethod


@pytest.mark.run(order=4)
class TestChokuzenInfoRepository:
    __common = CommonMethod()
    __cir = MysqlChokuzenInfoRepositoryImpl()
    __common_table_name: str = "chokuzen_cond_tb"
    __player_table_name: str = "chokuzen_player_tb"
    __cond_col_set = {"race_id", "datejyo_id"}.union(
        set(WeatherInfo.__annotations__.keys())
    )

    __p_col_set = {"waku_id", "race_id"}.union(
        set(ChokuzenPlayerInfo.__annotations__.keys())
    )

    @pytest.fixture(scope="class", autouse=True)
    def preparation(self):
        self.__cir.create_table_if_not_exists()

    @pytest.mark.parametrize(
        "tb_name, col_set",
        [
            (__common_table_name, __cond_col_set),
            (__player_table_name, __p_col_set),
        ],
    )
    def test_create_table(self, tb_name, col_set):
        get_set = self.__common.get_columns(tb_name)
        assert get_set == col_set

    def test_save_data(self):
        cond_info = WeatherInfo(22.5, "晴", 3, 14.2, 2, 5)
        player1_info = ChokuzenPlayerInfo(
            1,
            "さんぷる太郎",
            54.2,
            0.1,
            6.74,
            -0.5,
            5,
            0.12,
        )
        program_info = ChokuzenInfo(
            date(2020, 1, 1), 1, 4, cond_info, [player1_info]
        )

        self.__cir.save_info([program_info])
        cond_check_cols = [
            "race_id",
            "datejyo_id",
            "weather",
            "wave",
        ]
        res_common_tpl = self.__common.get_targetdata(
            self.__common_table_name,
            "race_id",
            "202001010104",
            cond_check_cols,
        )
        ex_common_cols = (202001010104, 2020010101, "晴", 2)

        player_check_cols = ["waku_id", "race_id", "tilt", "tenji_st"]
        res_player1_tpl = self.__common.get_targetdata(
            self.__player_table_name,
            "waku_id",
            "2020010101041",
            player_check_cols,
        )
        ex_player1_cols = (2020010101041, 202001010104, -0.5, 0.12)

        assert res_common_tpl == ex_common_cols
        assert res_player1_tpl == ex_player1_cols
