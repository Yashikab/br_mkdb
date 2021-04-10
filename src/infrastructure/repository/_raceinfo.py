from datetime import date
from logging import getLogger
from typing import Iterable

from domain.model.info import HoldRaceInfo
from domain.repository import RaceInfoRepository
from infrastructure.const import MODULE_LOG_NAME
from infrastructure.mysql.creator import MysqlCreator
from infrastructure.mysql.executer import MysqlExecuter
from ._common import CommonMethod


class MysqlRaceInfoRepositoryImpl(RaceInfoRepository):
    def __init__(self):
        self.tb_name = "holdjyo_tb"
        self.__executer = MysqlExecuter()
        self.__common = CommonMethod()
        self.logger = getLogger(MODULE_LOG_NAME).getChild(
            self.__class__.__name__
        )
        self.schema = [
            ("datejyo_id", "INT", "PRIMARY KEY"),
            ("holddate", "DATE"),
            ("jyo_cd", "INT"),
            ("jyo_name", "VARCHAR(30)"),
            ("shinko", "VARCHAR(100)"),
            ("ed_race_no", "INT"),
        ]

    def create_table_if_not_exists(self):
        foreign_keys = ["jyo_cd"]
        refs = ["jyo_master"]
        sql_creator = MysqlCreator()
        query = sql_creator.sql_for_create_table(
            self.tb_name, self.schema, foreign_keys, refs
        )
        self.__executer.run_query(query)

    def save_info(self, hri_itr: Iterable[HoldRaceInfo]) -> None:
        insert_phrases = list()
        cols = list(map(lambda x: x[0], self.schema))
        for hri in hri_itr:
            holddate = self.__common.to_query_phrase(hri.date)
            datejyo_id = f"{holddate}{hri.jyo_cd:02}"
            inserts = [datejyo_id, holddate]
            inserts += self.__common.get_insertlist(hri, cols[2:])
            insert_phrase = f"(" f"{', '.join(inserts)}" f")"
            insert_phrases.append(insert_phrase)
        phrase = ", ".join(insert_phrases)
        sql = f"INSERT IGNORE INTO {self.tb_name} VALUES"
        query = " ".join([sql, phrase])
        self.logger.debug(query)
        print(query)
        self.__executer.run_query(query)