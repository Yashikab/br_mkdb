from abc import ABCMeta, abstractmethod
from typing import Iterator

from domain.model.info import ProgramInfo


class ProgramInfoRepository(metaclass=ABCMeta):
    @abstractmethod
    def save_info(self, data_itr: Iterator[ProgramInfo]) -> None:
        """1会場ごとに考えるならこれでいいと思う"""
        raise NotImplementedError()

    @abstractmethod
    def create_table_if_not_exists(self) -> None:
        raise NotImplementedError()
