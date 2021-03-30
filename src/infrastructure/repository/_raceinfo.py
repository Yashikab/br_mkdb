from typing import Iterator


from domain.model.info import HoldRaceInfo
from domain.repository import RaceInfoRepository


class MysqlRaceInfoRepositoryImpl(RaceInfoRepository):
    tb_name: str

    def __init__(self):
        self.tb_name = "holdjyo_tb"

    def save_info(self, data_itr: Iterator[HoldRaceInfo]) -> None:
        pass

    def create_table_if_not_exists():
        pass
