from logging import getLogger
from typing import List, Optional, Tuple

from domain import const
from domain.tablecreator import JyoDataTableCreator, JyoMasterTableCreator
from infrastructure.connect import MysqlConnector

logger = getLogger(__name__)


class SqlCreator:

    @classmethod
    def sql_for_create_table_if_not_exists(
        cls,
        tb_name: str,
        schemas: List[Tuple[str, ...]]
    ) -> str:
        """テーブル作成のためのクエリ作成

        Parameters
        ----------
        tb_name : str
            テーブル名
        schemas : List[Tuple[str, ...]]
            スキーマのリスト ("変数名", "型", "外部キー(任意)")を1セットとし、
            テーブルに定義するスキーマをリストで入れる。
            各スキーマはスペースでjoinされ、スキーマ間は", \n"でジョインする。

        Returns
        -------
        str
            テーブル作成のためのクエリ
        """
        schemas = ", \n".join(list(map(lambda s: " ".join(s), schemas)))
        sql = f"CREATE TABLE IF NOT EXISTS {tb_name}( {schemas} ) " \
              f"CHARACTER SET utf8;"
        return sql


class Mysql:
    @classmethod
    def run_query(self, query: str) -> Optional[Exception]:
        try:
            logger.debug('connecteng Mysql.')
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                logger.debug('run query.')
                cursor.execute(query)
                # cursor.close()
            logger.debug('query run successfully!')
            return None
        except Exception as e:
            logger.error(f'{e}')
            raise e


class JyoMasterTableCreatorImpl(JyoMasterTableCreator):
    __tb_name = "jyo_master"

    def create_table(self):
        schemas = [
            ("jyo_name", "VARCHAR(100)"),
            ("jyo_cd", "INT", "PRIMARY KEY")
        ]
        query = SqlCreator.sql_for_create_table_if_not_exists(
            self.__tb_name, schemas)
        Mysql.run_query(query)
        # TODO テスト時にまずsqlサーバー立てる


class JyoDataTableCreatorImpl(JyoDataTableCreator):

    def create_table(self):
        pass
