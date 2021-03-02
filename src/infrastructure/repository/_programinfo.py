from typing import Iterator

from domain.model.info import ProgramInfo
from domain.repository import ProgramInfoRepository


class ProgramInfoRepositoryImpl(ProgramInfoRepository):

    def save_info(self, data_itr: Iterator[ProgramInfo]) -> None:
        pass
