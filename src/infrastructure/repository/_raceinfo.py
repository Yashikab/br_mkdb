from typing import Iterator

from domain.model.info import HoldRaceInfo
from domain.repository import RaceInfoRepository


class RaceInfoRepositoryImpl(RaceInfoRepository):
    def save_info(self, data_itr: Iterator[HoldRaceInfo]) -> None:
        pass
