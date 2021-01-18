from logging import getLogger

from domain import const
from infrastructure.connector import MysqlConnector

logger = getLogger(__name__)


class Mysql:
    @classmethod
    def run_query(self, query: str) -> None:
        try:
            logger.debug('connecteng Mysql.')
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                logger.debug('run query.')
                cursor.execute(query)
                # cursor.close()
            logger.debug('query run successfully!')
        except Exception as e:
            logger.error(f'{e}')
            raise e
