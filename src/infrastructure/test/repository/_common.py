# python 3.7.5
# coding: utf-8
"""
dt2sqlモジュール用単体テストの共通関数
"""
from logging import getLogger
from datetime import date
from pathlib import Path
from typing import Any, List

from infrastructure import const
from infrastructure.connector import MysqlConnector


class CommonMethod:
    logger = getLogger(__name__)

    def get_columns(self, tb_name: str) -> Any:
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
                sql = f"show columns from {tb_name}"
                cursor.execute(sql)
                get_set = set(map(lambda x: x[0], cursor.fetchall()))
                cursor.close()
        except Exception:
            get_set = {}
        finally:
            return get_set

    def get_targetdata(
        self, tb_name: str, id_name: str, target_id: int, col_list: list
    ) -> tuple:
        """
        idのcol_listのデータを取得しタプルで返す
        """
        insert_col_value = ",".join(col_list)
        sql_list = [
            "select",
            insert_col_value,
            "from",
            tb_name,
            "where",
            f"{id_name}={target_id}",
        ]
        sql = " ".join(sql_list)
        try:
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                res_list = cursor.fetchall()
                res_tpl = res_list[0]
        except Exception as e:
            self.logger.error(f"{e}")
            res_tpl = None
        finally:
            return res_tpl

    def get_html_filepath(self, filename: Path) -> Path:
        return Path(__file__).resolve().parent.joinpath("test_html", filename)
