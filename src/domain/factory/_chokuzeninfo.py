from abc import ABCMeta, abstractmethod
from datetime import date
from typing import Iterator

from domain.model.info import ChokuzenInfo


class ChokuzenInfoFactory(metaclass=ABCMeta):
    """直前情報を取得する"""

    @abstractmethod
    def getinfo(self, target_date: date) -> Iterator[ChokuzenInfo]:
        raise NotImplementedError()

    @abstractmethod
    def _get_raceinfo(self, target_date: date, race_no: int) -> ChokuzenInfo:
        raise NotImplementedError()
