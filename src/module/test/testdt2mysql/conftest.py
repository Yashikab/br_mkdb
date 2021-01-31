# python 3.7.5
# coding: utf-8
"""
ここでmysqlにテスト用データを格納する
"""
import os

import pytest

from infrastructure.dbcontroller import LocalSqlController
from domain.tablecreator import create_table
from infrastructure.mysql import MysqlExecuter

# 場コードマスタだけ最初に入れておく


@pytest.fixture(scope="session", autouse=True)
def prepare():
    # 環境変数でmysqlの接続先を入れ替える
    os.environ['MYSQL_HOST'] = "testmysql"
    os.environ['MYSQL_USER'] = "test_boat_user"
    os.environ['MYSQL_PASSWORD'] = "test_pw"
    os.environ['MYSQL_DATABASE'] = "test_boat_db"

    # local実行の場合はdb立てる
    if not os.getenv("DRONE_COMMIT"):
        sql_ctl = LocalSqlController()
        sql_ctl.build()
        # データが消えるので落とさない

    create_table(MysqlExecuter())
