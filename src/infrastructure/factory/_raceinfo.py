from datetime import date
from typing import Iterator

from domain.factory import RaceInfoFactory
from domain.model.info import HoldRaceInfo


class RaceInfoFactoryImpl(RaceInfoFactory):

    def getinfo(self, target_date: date) -> Iterator[HoldRaceInfo]:
        pass
