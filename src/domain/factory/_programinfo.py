from abc import ABCMeta, abstractmethod
from datetime import date
from typing import Iterator

from domain.model.info import ProgramInfo


class ProgramInfoFactory(metaclass=ABCMeta):
    """番組表情報を取得する"""

    @abstractmethod
    def each_jyoinfo(self, target_date: date, jyo_cd: int) -> Iterator[ProgramInfo]:
        raise NotImplementedError()

    @abstractmethod
    def _raceinfo(self, target_date: date, race_no: int) -> ProgramInfo:
        raise NotImplementedError()
