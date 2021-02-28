from abc import ABCMeta, abstractmethod
from datetime import date
from typing import Iterator

from domain.model.info import HoldRaceInfo


class RaceInfoFactory(metaclass=ABCMeta):
    """当日の開催情報を取得する"""

    @abstractmethod
    def getinfo(self, target_date: date) -> Iterator[HoldRaceInfo]:
        raise NotImplementedError()
