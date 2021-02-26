from datetime import date
from typing import Iterator

from domain.factory import ProgramInfoFactory
from domain.model.info import ProgramInfo


class ProgramInfoFactoryImpl(ProgramInfoFactory):

    def getinfo(self, target_date: date) -> Iterator[ProgramInfo]:
        pass

    def _get_raceinfo(self, target_date: date, race_no: int) -> ProgramInfo:
        pass
