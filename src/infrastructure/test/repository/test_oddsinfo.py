from datetime import date
import enum

import pytest

from domain.model.info import (
    ResultCommonInfo,
    ResultInfo,
    ResultPlayerInfo,
    WeatherInfo,
    ThreeRentan,
    ThreeRenfuku,
    TwoRentan,
    TwoRenfuku,
    Tansho,
)
from infrastructure.repository import MysqlOddsInfoRepositoryImpl

from ._common import CommonMethod


@pytest.mark.run(order=6)
class TestOddsInfoRepository:
    __common = CommonMethod()
    __oir = MysqlOddsInfoRepositoryImpl()
    __3tan_table_name = "odds_3tan_tb"
    __3fuku_table_name = "odds_3fuku_tb"
    __2tan_table_name = "odds_2tan_tb"
    __2fuku_table_name = "odds_2fuku_tb"
    __tansho_table_name = "odds_1tan_tb"

    key_set = {"race_id"}
    three_rentan_key = key_set.union(set(ThreeRentan.__annotations__.keys()))
    three_renfuku_key = key_set.union(set(ThreeRenfuku.__annotations__.keys()))
    two_rentan_key = key_set.union(set(TwoRentan.__annotations__.keys()))
    two_renfuku_key = key_set.union(set(TwoRenfuku.__annotations__.keys()))
    one_rentan_key = key_set.union(set(Tansho.__annotations__.keys()))

    @pytest.fixture(scope="class", autouse=True)
    def preparation(self):
        self.__oir.create_table_if_not_exists()

    @pytest.mark.parametrize(
        "tb_name, col_set",
        [
            (__3tan_table_name, three_rentan_key),
            (__3fuku_table_name, three_renfuku_key),
            (__2tan_table_name, two_rentan_key),
            (__2fuku_table_name, two_renfuku_key),
            (__tansho_table_name, one_rentan_key),
        ],
    )
    def test_create_table(self, tb_name, col_set):
        get_set = self.__common.get_columns(tb_name)
        assert get_set == col_set

    def test_save_info(self):
        three_tan_dict = dict()
        for i, k in enumerate(list(self.three_rentan_key)):
            three_tan_dict[k] = 0.1 * i
        three_tan_dict.pop("race_id")
        print(ThreeRentan(**three_tan_dict))
