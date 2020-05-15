# python 3.7.5
# coding: utf-8
"""
getdataモジュール用単体テスト
"""
from module.dt2sql import JyoData2sql
from module import const
import mysql.connector


class TestJyoData2sql:
    # クラスのcreate_table_if_not_existsを読んでから

    def test_exist_table(self):
        jd2sql = JyoData2sql()
        jd2sql.create_table_if_not_exists()
        # カラム名の一致でテスト
        try:
            conn = mysql.connector.connect(**const.MYSQL_CONFIG)
            cursor = conn.cursor()
            sql = 'show columns from holdjyo_tb'
            cursor.execute(sql)
            get_set = set(map(lambda x: x[0], cursor.fetchall()))
        except mysql.connector.errors.ProgrammingError:
            get_set = {}
        finally:
            cursor.close()
            conn.close()
        expected_set = {'datejyo_id', 'holddate', 'jyo_cd', 'jyo_name'}
        assert get_set == expected_set
