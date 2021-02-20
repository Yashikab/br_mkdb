from abc import ABCMeta, abstractmethod
from datetime import date


class ChokuzenInfoFactory(metaclass=ABCMeta):
    """直前情報を取得する"""

    @abstractmethod
    def getinfo(self, target_date: date):
        raise NotImplementedError()

    @abstractmethod
    def _get_raceinfo(self, target_date: date, race_no: int):
        raise NotImplementedError()
