from typing import Iterator

from domain.repository import ChokuzenInfoRepository
from domain.model.info import ChokuzenInfo


class ChokuzenInfoRepositoryImpl(ChokuzenInfoRepository):

    def save_info(self, data_itr: Iterator[ChokuzenInfo]) -> None:
        pass
