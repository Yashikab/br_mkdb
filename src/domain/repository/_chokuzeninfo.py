from abc import ABCMeta, abstractmethod
from typing import Iterator

from domain.model.info import ChokuzenInfo


class ChokuzenInfoRepository(metaclass=ABCMeta):
    @abstractmethod
    def save_info(self, data_itr: Iterator[ChokuzenInfo]) -> None:
        raise NotImplementedError()
