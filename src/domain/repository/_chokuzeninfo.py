from abc import ABCMeta, abstractmethod
from typing import Iterator

from domain.model.info import ChokuzenInfo


class ChokuzenInfoRepository(metaclass=ABCMeta):
    @abstractmethod
    def save_info(self, ci_itr: Iterator[ChokuzenInfo]) -> None:
        raise NotImplementedError()

    @abstractmethod
    def create_table_if_not_exists(self) -> None:
        raise NotImplementedError()
