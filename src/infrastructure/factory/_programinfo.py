from datetime import date
from typing import Iterator

from domain.factory import ProgramInfoFactory
from domain.model.info import ProgramInfo


class ProgramInfoFactoryImpl(ProgramInfoFactory):

    def each_jyoinfo(self,
                     target_date: date,
                     jyo_cd: int) -> Iterator[ProgramInfo]:
        pass

    def _raceinfo(self, target_date: date,
                  target_jyo: int,
                  race_no: int) -> ProgramInfo:
        pass
