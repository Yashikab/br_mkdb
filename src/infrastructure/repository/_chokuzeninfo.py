from typing import Iterator

from domain.model.info import ChokuzenInfo
from domain.repository import ChokuzenInfoRepository


class MysqlChokuzenInfoRepositoryImpl(ChokuzenInfoRepository):
    def create_table_if_not_exists(self) -> None:
        pass

    def save_info(self, data_itr: Iterator[ChokuzenInfo]) -> None:
        pass
