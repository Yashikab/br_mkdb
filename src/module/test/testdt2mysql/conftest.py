# python 3.7.5
# coding: utf-8
"""
ここでmysqlにテスト用データを格納する
"""
import pytest

from module.dt2sql import (
    JyoData2sql,
    RaceData2sql,
    ChokuzenData2sql,
    ResultData2sql,
    Odds2sql
)
from module.master2sql import JyoMaster2sql


@pytest.fixture(scope="session", autouse=True)
def a_jyomaster():
    # jyomaster
    jm2sql = JyoMaster2sql()
    jm2sql.create_table_if_not_exists()


@pytest.fixture(scope="session", autouse=True)
def b_jyodata():
    # jyodata
    jd2sql = JyoData2sql()
    jd2sql.create_table_if_not_exists()
    target_date = 20200512
    jd2sql.insert2table(target_date)
    return jd2sql
