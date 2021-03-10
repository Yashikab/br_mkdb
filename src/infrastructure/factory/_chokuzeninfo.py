from datetime import date
from typing import Iterator

from domain.factory import ChokuzenInfoFactory
from domain.model.info import ChokuzenInfo


class ChokuzenInfoFactoryImpl(ChokuzenInfoFactory):

    def each_jyoinfo(self,
                     target_date: date,
                     jyo_cd: int,
                     ed_race_no: int) -> Iterator[ChokuzenInfo]:
        pass

    def _raceinfo(self,
                  target_date: date,
                  jyo_cd: int,
                  race_no: int) -> ChokuzenInfo:
        pass
