from datetime import date
import enum

import pytest

from domain.model.info import (
    OddsInfo,
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
        for i, k in enumerate(list(ThreeRentan.__annotations__.keys())):
            three_tan_dict[k] = 0.1 * (i + 1)
        three_tan = ThreeRentan(**three_tan_dict)
        three_fuku_dict = dict()
        for i, k in enumerate(list(ThreeRenfuku.__annotations__.keys())):
            three_fuku_dict[k] = 0.1 * (i + 1)
        three_fuku = ThreeRenfuku(**three_fuku_dict)
        two_tan_dict = dict()
        for i, k in enumerate(list(TwoRentan.__annotations__.keys())):
            two_tan_dict[k] = 0.1 * (i + 1)
        two_tan = TwoRentan(**two_tan_dict)
        two_fuku_dict = dict()
        for i, k in enumerate(list(TwoRenfuku.__annotations__.keys())):
            two_fuku_dict[k] = 0.1 * (i + 1)
        two_fuku = TwoRenfuku(**two_fuku_dict)
        tansho_dict = dict()
        for i, k in enumerate(list(Tansho.__annotations__.keys())):
            tansho_dict[k] = 0.1 * (i + 1)
        tansho = Tansho(**tansho_dict)

        odds_info = OddsInfo(
            date(2020, 1, 1),
            1,
            4,
            three_tan,
            three_fuku,
            two_tan,
            two_fuku,
            tansho,
        )
        self.__oir.save_info([odds_info])
        three_tan_actual = self.__common.get_targetdata(
            self.__3tan_table_name,
            "race_id",
            "202001010104",
            ["comb_123", "comb_654"],
        )
        three_tan_ex = (0.1, 0.1 * (len(self.three_rentan_key) - 1))

        three_fuku_actual = self.__common.get_targetdata(
            self.__3fuku_table_name,
            "race_id",
            "202001010104",
            ["comb_123", "comb_456"],
        )
        three_fuku_ex = (0.1, 0.1 * (len(self.three_renfuku_key) - 1))

        two_tan_actual = self.__common.get_targetdata(
            self.__2tan_table_name,
            "race_id",
            "202001010104",
            ["comb_12", "comb_65"],
        )
        two_tan_ex = (0.1, 0.1 * (len(self.two_rentan_key) - 1))

        two_fuku_actual = self.__common.get_targetdata(
            self.__2fuku_table_name,
            "race_id",
            "202001010104",
            ["comb_12", "comb_56"],
        )
        two_fuku_ex = (0.1, 0.1 * (len(self.two_renfuku_key) - 1))

        tansho_actual = self.__common.get_targetdata(
            self.__tansho_table_name,
            "race_id",
            "202001010104",
            ["comb_1", "comb_6"],
        )
        tansho_ex = (0.1, 0.6)
        assert three_tan_actual == three_tan_ex
        assert three_fuku_actual == three_fuku_ex
        assert two_tan_actual == two_tan_ex
        assert two_fuku_actual == two_fuku_ex
        assert tansho_actual == tansho_ex
