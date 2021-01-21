from logging import getLogger

from domain.tablecreator import (JyoDataTableCreator, JyoMasterTableCreator,
                                 RaceInfoTableCreator)
from infrastructure.mysql import MysqlExecuter

logger = getLogger(__name__)


class JyoMasterTableCreatorImpl(JyoMasterTableCreator):

    def __init__(self) -> None:
        super().__init__(MysqlExecuter)

    def create_table(self) -> None:
        return super().create_table()


class JyoDataTableCreatorImpl(JyoDataTableCreator):

    def __init__(self) -> None:
        super().__init__(MysqlExecuter)

    def create_table(self) -> None:
        return super().create_table()


class RaceDataTableCreatorImpl(RaceInfoTableCreator):

    def __init__(self) -> None:
        super().__init__(MysqlExecuter)

    def create_commoninfo_table(self) -> None:
        return super().create_commoninfo_table()

    def create_playerinfo_table(self) -> None:
        return super().create_playerinfo_table()
