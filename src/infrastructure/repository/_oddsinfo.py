from typing import Iterator

from domain.model.info import OddsInfo
from domain.repository import OddsInfoRepository


class ProtramInfoRepositoryImpl(OddsInfoRepository):

    def save_info(self, data_itr: Iterator[OddsInfo]) -> None:
        pass
