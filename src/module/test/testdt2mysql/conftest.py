# python 3.7.5
# coding: utf-8
"""
ここでmysqlにテスト用データを格納する
"""
import os
import pytest

from module.master2sql import JyoMaster2sql


# 場コードマスタだけ最初に入れておく
@pytest.fixture(scope="session", autouse=True)
def prepare():
    # 環境変数でmysqlの接続先を入れ替える
    os.environ['MYSQL_HOST'] = "testmysql"
    os.environ['MYSQL_USER'] = "test_boat_user"
    os.environ['MYSQL_PASSWORD'] = "test_pw"
    os.environ['MYSQL_DATABASE'] = "test_boat_db"
