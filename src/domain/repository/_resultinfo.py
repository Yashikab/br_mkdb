from abc import ABCMeta, abstractmethod
from typing import Iterator

from domain.model.info import ResultInfo


class ResultInfoRepository(metaclass=ABCMeta):

    @abstractmethod
    def save_info(self, data_itr: Iterator[ResultInfo]) -> None:
        raise NotImplementedError()
