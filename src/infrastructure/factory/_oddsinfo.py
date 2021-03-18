from datetime import date
from typing import Iterator

from domain.factory import OddsInfoFactory
from domain.model.info import OddsInfo, ThreeRenfuku, ThreeRentan


class OddsInfoFactoryImpl(OddsInfoFactory):

    def each_jyo(self, target_date: date, jyo_cd: int) -> Iterator[OddsInfo]:
        pass

    def _raceinfo(self,
                  target_date: date,
                  jyo_cd: int,
                  race_no: int) -> OddsInfo:
        pass

    def _three_rentan(self,
                      target_date: date,
                      jyo_cd: int,
                      race_no: int) -> ThreeRentan:
        pass

    def _three_renfuku(self,
                       target_date: date,
                       jyo_cd: int,
                       race_no: int) -> ThreeRenfuku:
        pass
