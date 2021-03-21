from abc import ABCMeta, abstractmethod
from datetime import date
from typing import Iterator

from domain.model.info import ResultInfo


class ResultInfoFactory(metaclass=ABCMeta):
    """結果情報を取得する"""

    @abstractmethod
    def each_jyoinfo(
        self, target_date: date, jyo_cd: int, ed_race_no: int
    ) -> Iterator[ResultInfo]:

        raise NotImplementedError()

    @abstractmethod
    def _raceinfo(self, target_date: date, jyo_cd: int, race_no: int) -> ResultInfo:
        raise NotImplementedError()
