from datetime import date
from typing import Iterator

from domain.factory import OddsInfoFactory
from domain.model.info import OddsInfo


class OddsInfoFactoryImpl(OddsInfoFactory):

    def getinfo(self, target_date: date) -> Iterator[OddsInfo]:
        pass

    def _raceinfo(self, target_date: date, race_no: int) -> OddsInfo:
        pass
