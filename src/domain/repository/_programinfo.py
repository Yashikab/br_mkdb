from abc import ABCMeta, abstractmethod
from typing import Iterator

from domain.model.info import ProgramInfo


class ProgramInfoRepository(metaclass=ABCMeta):
    @abstractmethod
    def save_info(self, data_itr: Iterator[ProgramInfo]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def create_table_if_not_exists(self) -> None:
        raise NotImplementedError()
