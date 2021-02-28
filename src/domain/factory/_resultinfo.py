from abc import ABCMeta, abstractmethod
from datetime import date
from typing import Iterator

from domain.model.info import ResultInfo


class ResultInfoFactory(metaclass=ABCMeta):
    """結果情報を取得する"""

    @abstractmethod
    def getinfo(self, target_date: date) -> Iterator[ResultInfo]:
        raise NotImplementedError()

    @abstractmethod
    def _raceinfo(self, target_date: date, race_no: int) -> ResultInfo:
        raise NotImplementedError()
