from typing import Iterator

from domain.repository import ResultInfoRepository
from domain.model.info import ResultInfo


class ProtramInfoRepositoryImpl(ResultInfoRepository):

    def save_info(self, data_itr: Iterator[ResultInfo]) -> None:
        pass
