from abc import ABCMeta, abstractmethod
from typing import Iterator

from domain.model.info import OddsInfo


class OddsInfoRepository(metaclass=ABCMeta):

    @abstractmethod
    def save_info(self, data_itr: Iterator[OddsInfo]) -> None:
        raise NotImplementedError()
