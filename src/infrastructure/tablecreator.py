from logging import getLogger

from domain.tablecreator import JyoDataTableCreator, JyoMasterTableCreator
from infrastructure.mysql import Mysql, SqlCreator

logger = getLogger(__name__)


class JyoMasterTableCreatorImpl(JyoMasterTableCreator):
    __tb_name = "jyo_master"

    def create_table(self):
        schemas = [
            ("jyo_name", "VARCHAR(100)"),
            ("jyo_cd", "INT", "PRIMARY KEY")
        ]
        query = SqlCreator.sql_for_create_table(
            self.__tb_name, schemas)
        Mysql.run_query(query)
        # TODO テスト時にまずsqlサーバー立てる


class JyoDataTableCreatorImpl(JyoDataTableCreator):

    def create_table(self):
        pass
