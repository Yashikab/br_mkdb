from datetime import date
from typing import List
import pytest

from domain.model.info import HoldRaceInfo

from ._common import CommonMethod
from infrastructure.repository import MysqlRaceInfoRepositoryImpl


@pytest.mark.run(order=2)
class TestRaceInfoRepository:
    __common = CommonMethod()
    __rir = MysqlRaceInfoRepositoryImpl()
    __table_name: str = "holdjyo_tb"
    __col_list: List[str] = [
        "datejyo_id",
        "holddate",
        "jyo_cd",
        "jyo_name",
        "shinko",
        "ed_race_no",
    ]

    @pytest.fixture(scope="class", autouse=True)
    def preparation(self):
        self.__rir.create_table_if_not_exists()

    def test_create_table(self):
        get_set = self.__common.get_columns(self.__table_name)
        expected_set = set(self.__col_list)
        assert get_set == expected_set

    def test_save_data(self):
        holdraceinfo_sample = HoldRaceInfo(
            date(2020, 1, 1), "サンプル場1", 1, "進行状況", 5
        )

        self.__rir.save_info([holdraceinfo_sample])
        res_tpl = self.__common.get_targetdata(
            self.__table_name, "datejyo_id", "2020010101", self.__col_list
        )
        expected_tpl = (2020010101, date(2020, 1, 1), 1, "サンプル場1", "進行状況", 5)
        assert res_tpl == expected_tpl
