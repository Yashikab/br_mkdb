# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""

import pytest

from module import const
import mysql.connector
from module.dt2mysql import JyoData2Mysql


class TestJyoData2Mysql:
    # クラスのcreate_table_if_not_existsを読んでから

    def test_exist_table(self):
        jd2m = JyoData2Mysql()
        jd2m.create_table_if_not_exists()
        conn = mysql.connector.connect(**const.MYSQL_CONFIG)
        cursor = conn.cursor(buffered=True)
        # sql叩いてテーブルが存在すればOK
        sql = \
            """
            show columns from {tb_name}
            """
        cursor.execute(sql.format(tb_name='holdjyo_tb'))
        col_name_set = set(map(lambda x: x[0], cursor.fetchall()))
        cursor.close()
        conn.close()
        expected_set = {'datejyo_id', 'holddate', 'jyo_cd', 'jyo_name'}
        assert col_name_set == expected_set
