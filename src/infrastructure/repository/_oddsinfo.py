import copy
from functools import singledispatchmethod
from dataclasses import asdict, dataclass
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

        self._create_table_and_get_schema(self.__3tan_tb_name, ThreeRentan)
        self._create_table_and_get_schema(self.__3fuku_tb_name, ThreeRenfuku)
        self._create_table_and_get_schema(self.__2tan_tb_name, TwoRentan)
        self._create_table_and_get_schema(self.__2fuku_tb_name, TwoRenfuku)
        self._create_table_and_get_schema(self.__tansho_tb_name, Tansho)

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

    def save_info(self, odds_itr: Iterator[OddsInfo]) -> None:
        self.__save_info_each(odds_itr, ThreeRentan)
        self.__save_info_each(odds_itr, ThreeRenfuku)
        self.__save_info_each(odds_itr, TwoRentan)
        self.__save_info_each(odds_itr, TwoRenfuku)
        self.__save_info_each(odds_itr, Tansho)

    def __save_info_each(
        self,
        odds_itr: Iterator[OddsInfo],
        odds_type: Union[
            ThreeRentan, ThreeRenfuku, TwoRentan, TwoRenfuku, Tansho
        ],
    ) -> None:
        common_insert_phrases = list()
        for odds_info in odds_itr:
            holddate = self.__common.to_query_phrase(odds_info.date)
            race_id = f"{holddate}{odds_info.jyo_cd:02}{odds_info.race_no:02}"
            common_inserts = [race_id]
            common_inserts += self.__common.get_insertlist(
                self._value_of_info(odds_type, odds_info),
                list(odds_type.__annotations__.keys()),
            )
            common_insert_phrases.append(f"({', '.join(common_inserts)})")
        common_phrase = ", ".join(common_insert_phrases)
        common_sql = (
            f"INSERT IGNORE INTO {self._value_of_tb(odds_type)} "
            f"VALUES {common_phrase};"
        )
        print(common_sql)
        self.logger.debug(common_sql)
        self.executer.run_query(common_sql)

    def _value_of_info(
        self,
        odds_type: Union[
            ThreeRentan, ThreeRenfuku, TwoRentan, TwoRenfuku, Tansho
        ],
        odds_info: OddsInfo,
    ):
        if odds_type is ThreeRentan:
            return odds_info.three_rentan

        elif odds_type is ThreeRenfuku:
            return odds_info.three_renfuku

        elif odds_type is TwoRentan:
            return odds_info.two_rentan

        elif odds_type is TwoRenfuku:
            return odds_info.two_renfuku

        elif odds_type is Tansho:
            return odds_info.tansho

    def _value_of_tb(
        self,
        odds_type: Union[
            ThreeRentan, ThreeRenfuku, TwoRentan, TwoRenfuku, Tansho
        ],
    ):
        if odds_type is ThreeRentan:
            return self.__3tan_tb_name

        elif odds_type is ThreeRenfuku:
            return self.__3fuku_tb_name

        elif odds_type is TwoRentan:
            return self.__2tan_tb_name

        elif odds_type is TwoRenfuku:
            return self.__2fuku_tb_name

        elif odds_type is Tansho:
            return self.__tansho_tb_name
