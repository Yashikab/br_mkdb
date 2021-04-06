from typing import Iterator

from domain.model.info import ProgramInfo
from domain.repository import ProgramInfoRepository


class MysqlProgramInfoRepositoryImpl(ProgramInfoRepository):
    def save_info(self, data_itr: Iterator[ProgramInfo]) -> None:
        pass

    def create_table_if_not_exists(self) -> None:
        pass
