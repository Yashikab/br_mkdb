from datetime import date
from typing import Iterator

from domain.factory import ChokuzenInfoFactory
from domain.model.info import ChokuzenInfo


class ChokuzenInfoFactoryImpl(ChokuzenInfoFactory):

    def getinfo(self, target_date: date) -> Iterator[ChokuzenInfo]:
        pass

    def _raceinfo(self, target_date: date, race_no: int) -> ChokuzenInfo:
        pass
