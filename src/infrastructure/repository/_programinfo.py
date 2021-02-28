from typing import Iterator

from domain.repository import ProgramInfoRepository
from domain.model.info import ProgramInfo


class ProgramInfoRepositoryImpl(ProgramInfoRepository):

    def save_info(self, data_itr: Iterator[ProgramInfo]) -> None:
        pass
