import copy
from dataclasses import dataclass
from typing import Iterator, Union
from logging import getLogger


from domain.model.info import OddsInfo
from domain.repository import OddsInfoRepository
from domain.model.info import (
    ThreeRenfuku,
    ThreeRentan,
    TwoRenfuku,
    TwoRentan,
    Tansho,
)
from infrastructure.const import MODULE_LOG_NAME
from infrastructure.mysql import MysqlExecuter, MysqlCreator
from ._common import CommonMethod


class MysqlOddsInfoRepositoryImpl(OddsInfoRepository):
    def __init__(self):
        self.logger = getLogger(MODULE_LOG_NAME).getChild(
            self.__class__.__name__
        )
        self.executer = MysqlExecuter()
        self.__creator = MysqlCreator()
        self.__common = CommonMethod()
        self.__ids = [("race_id", "BIGINT", "PRIMARY KEY")]
        self.__foreign_keys = ["race_id"]
        self.__refs = ["raceinfo_tb"]
        self.__3tan_tb_name = "odds_3tan_tb"
        self.__3fuku_tb_name = "odds_3fuku_tb"
        self.__2tan_tb_name = "odds_2tan_tb"
        self.__2fuku_tb_name = "odds_2fuku_tb"
        self.__tansho_tb_name = "odds_1tan_tb"

    def create_table_if_not_exists(self) -> None:

        self.__3tan_schema = self._create_table_and_get_schema(
            self.__3tan_tb_name, ThreeRentan
        )
        self.__3fuku_schema = self._create_table_and_get_schema(
            self.__3fuku_tb_name, ThreeRenfuku
        )
        self.__2tan_schema = self._create_table_and_get_schema(
            self.__2tan_tb_name, TwoRentan
        )
        self.__2fuku_schema = self._create_table_and_get_schema(
            self.__2fuku_tb_name, TwoRenfuku
        )
        self.__tansho_schema = self._create_table_and_get_schema(
            self.__tansho_tb_name, Tansho
        )

    def _create_table_and_get_schema(self, tb_name: str, data_class: dataclass):
        """3連単情報"""
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in data_class.__annotations__.items():
            schema.append(
                (var_name, self.__creator.get_sqltype_from_pytype(var_type))
            )
        query = self.__creator.sql_for_create_table(
            tb_name, schema, self.__foreign_keys, self.__refs
        )
        self.executer.run_query(query)
        return schema

    def save_info(self, odds_itr: Iterator[OddsInfo]) -> None:
        for odds_info in odds_itr:
            holddate = self.__common.to_query_phrase(odds_info.date)
            race_id = f"{holddate}{odds_info.jyo_cd:02}{odds_info.race_no:02}"
