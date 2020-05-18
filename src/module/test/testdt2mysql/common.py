# python 3.7.5
# coding: utf-8
"""
dt2sqlモジュール用単体テストの共通関数
"""
from module import const
from module.connect import MysqlConnector


class CommonMethod:
    def get_columns2set(self, tb_name: str) -> set:
        """テーブル名のカラムを取得

        Parameters
        ----------
            tb_name: str
                テーブル名

        Returns
        -------
            get_set: set
                カラムのset
        """
        try:
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                sql = f'show columns from {tb_name}'
                cursor.execute(sql)
                get_set = set(map(lambda x: x[0], cursor.fetchall()))
                cursor.close()
        except Exception:
            get_set = {}
        finally:
            return get_set
