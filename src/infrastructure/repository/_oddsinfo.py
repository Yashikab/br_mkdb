from typing import Iterator

from domain.model.info import OddsInfo
from domain.repository import OddsInfoRepository


class MysqlOddsInfoRepositoryImpl(OddsInfoRepository):
    def create_table_if_not_exists(self) -> None:
        pass

    def save_info(self, odds_itr: Iterator[OddsInfo]) -> None:
        pass
