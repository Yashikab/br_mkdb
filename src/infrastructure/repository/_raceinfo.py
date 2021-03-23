from typing import Iterator

from domain.model.info import HoldRaceInfo
from domain.repository import RaceInfoRepository


class MysqlRaceInfoRepositoryImpl(RaceInfoRepository):
    def __init__(self):
        self.create_table_if_not_exists()

    def save_info(self, data_itr: Iterator[HoldRaceInfo]) -> None:
        pass

    def create_table_if_not_exists():
        pass
