from datetime import date
from typing import Iterator

from domain.factory import ResultInfoFactory
from domain.model.info import ResultInfo


class ResultInfoFactoryImpl(ResultInfoFactory):

    def getinfo(self, target_date: date) -> Iterator[ResultInfo]:
        pass

    def _raceinfo(self, target_date: date, race_no: int) -> ResultInfo:
        pass
