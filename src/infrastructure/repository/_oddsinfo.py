import copy
from typing import Iterator
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

    def create_table_if_not_exists(self) -> None:
        self.__ids = [("race_id", "BIGINT", "PRIMARY KEY")]
        self.__foreign_keys = ["race_id"]
        self.__refs = ["raceinfo_tb"]
        self._create_threerentan_table()
        self._create_threefuku_table()
        self._create_tworentan_table()
        self._create_twofuku_table()
        self._create_tansho_table()

    def _create_threerentan_table(self):
        """3連単情報"""
        tb_name = "odds_3tan_tb"
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in ThreeRentan.__annotations__.items():
            schema.append(
                (var_name, self.__creator.get_sqltype_from_pytype(var_type))
            )
        query = self.__creator.sql_for_create_table(
            tb_name, schema, self.__foreign_keys, self.__refs
        )
        self.executer.run_query(query)

    def _create_threefuku_table(self):
        """3連複情報"""
        tb_name = "odds_3fuku_tb"
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in ThreeRenfuku.__annotations__.items():
            schema.append(
                (var_name, self.__creator.get_sqltype_from_pytype(var_type))
            )
        query = self.__creator.sql_for_create_table(
            tb_name, schema, self.__foreign_keys, self.__refs
        )
        self.executer.run_query(query)

    def _create_tworentan_table(self):
        """2連単情報"""
        tb_name = "odds_2tan_tb"
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in TwoRentan.__annotations__.items():
            schema.append(
                (var_name, self.__creator.get_sqltype_from_pytype(var_type))
            )
        query = self.__creator.sql_for_create_table(
            tb_name, schema, self.__foreign_keys, self.__refs
        )
        self.executer.run_query(query)

    def _create_twofuku_table(self):
        """2連複情報"""
        tb_name = "odds_2fuku_tb"
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in TwoRenfuku.__annotations__.items():
            schema.append(
                (var_name, self.__creator.get_sqltype_from_pytype(var_type))
            )
        query = self.__creator.sql_for_create_table(
            tb_name, schema, self.__foreign_keys, self.__refs
        )
        self.executer.run_query(query)

    def _create_tansho_table(self):
        """単勝情報"""
        tb_name = "odds_1tan_tb"
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in Tansho.__annotations__.items():
            schema.append(
                (var_name, self.__creator.get_sqltype_from_pytype(var_type))
            )
        query = self.__creator.sql_for_create_table(
            tb_name, schema, self.__foreign_keys, self.__refs
        )
        self.executer.run_query(query)

    def save_info(self, odds_itr: Iterator[OddsInfo]) -> None:
        pass
