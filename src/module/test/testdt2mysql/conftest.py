# python 3.7.5
# coding: utf-8
"""
ここでmysqlにテスト用データを格納する
"""
import pytest

from module.master2sql import JyoMaster2sql


# 場コードマスタだけ最初に入れておく
@pytest.fixture(scope="session", autouse=True)
def jyomaster():
    # jyomaster
    jm2sql = JyoMaster2sql()
    jm2sql.create_table_if_not_exists()
