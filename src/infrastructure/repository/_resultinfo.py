from typing import Iterator

from domain.model.info import ResultInfo
from domain.repository import ResultInfoRepository


class MysqlResultInfoRepositoryImpl(ResultInfoRepository):
    def create_table_if_not_exists(self) -> None:
        pass

    def save_info(self, data_itr: Iterator[ResultInfo]) -> None:
        pass
