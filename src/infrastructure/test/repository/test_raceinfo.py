import pytest

from ._common import CommonMethod
from infrastructure.repository import MysqlRaceInfoRepositoryImpl


@pytest.mark.run(order=2)
class TestRaceInfoRepository:
    __common = CommonMethod()
    __table_name: str = "holdjyo_tb"

    @pytest.fixture(scope="class", autouse=True)
    def preparation(self):
        self.rir = MysqlRaceInfoRepositoryImpl()
        self.rir.create_table_if_not_exists()

    def test_create_table(self):
        get_set = self.__common.get_columns(self.__table_name)
        expected_set = {
            "datejyo_id",
            "holddate",
            "jyo_cd",
            "jyo_name",
            "shinko",
            "ed_race_no",
        }
        assert get_set == expected_set
