from logging import getLogger

from domain.tablecreator import JyoDataTableCreator, JyoMasterTableCreator
from infrastructure.mysql import MysqlExecuter

logger = getLogger(__name__)


class JyoMasterTableCreatorImpl(JyoMasterTableCreator):

    def __init__(self):
        super().__init__(MysqlExecuter)

    def create_table(self) -> None:
        return super().create_table()


class JyoDataTableCreatorImpl(JyoDataTableCreator):

    def __init__(self):
        super().__init__(MysqlExecuter)

    def create_table(self) -> None:
        return super().create_table()
