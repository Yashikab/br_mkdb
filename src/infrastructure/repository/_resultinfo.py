from typing import Iterator

from domain.model.info import ResultInfo
from domain.repository import ResultInfoRepository


class ProtramInfoRepositoryImpl(ResultInfoRepository):
    def save_info(self, data_itr: Iterator[ResultInfo]) -> None:
        pass
