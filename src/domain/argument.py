# python 3.7.5
# coding: utf-8
from datetime import date
from enum import Enum

from pydantic import BaseModel


class DBType(str, Enum):
    local = "local"
    gcs = "gcs"


class Options(BaseModel):
    """ユーザーが指定するoption引数"""
    start_date: date
    end_date: date
    wait_time: float
    create_table: bool
    db_type: DBType = DBType.local
