from typing import Iterator

from domain.repository import OddsInfoRepository
from domain.model.info import OddsInfo


class ProtramInfoRepositoryImpl(OddsInfoRepository):

    def save_info(self, data_itr: Iterator[OddsInfo]) -> None:
        pass
