from typing import Iterator

from domain.model.info import ChokuzenInfo
from domain.repository import ChokuzenInfoRepository


class ChokuzenInfoRepositoryImpl(ChokuzenInfoRepository):
    def save_info(self, data_itr: Iterator[ChokuzenInfo]) -> None:
        pass
