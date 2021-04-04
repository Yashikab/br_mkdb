from typing import Iterable
from logging import getLogger

from domain.model.info import HoldRaceInfo
from domain.repository import RaceInfoRepository
from infrastructure.mysql.creator import MysqlCreator
from infrastructure.mysql.executer import MysqlExecuter
from infrastructure.const import MODULE_LOG_NAME
from ._common import CommonMethod


class MysqlRaceInfoRepositoryImpl(RaceInfoRepository):
    tb_name: str
    __executer: MysqlExecuter

    def __init__(self):
        self.tb_name = "holdjyo_tb"
        self.__executer = MysqlExecuter()
        self.logger = getLogger(MODULE_LOG_NAME).getChild(
            self.__class__.__name__
        )

    def save_info(self, hri_itr: Iterable[HoldRaceInfo]) -> None:
        insert_phrases = list()
        for hri in hri_itr:
            datejyo_id = f"{hri.date.strftime('%Y%m%d')}{hri.jyo_cd:02}"
            holddate = hri.date.strftime("%Y%m%d")
            jyo_cd = str(hri.jyo_cd)
            jyo_name = f"'{hri.jyo_name}'"
            shinko = f"'{hri.shinko}'"
            ed_race_no = str(hri.ed_race_no)
            insert_phrase = (
                f"("
                f"{datejyo_id}, {holddate}, {jyo_cd}, "
                f"{jyo_name}, {shinko}, {ed_race_no}"
                f")"
            )
            insert_phrases.append(insert_phrase)
        phrase = ", ".join(insert_phrases)
        sql = f"INSERT IGNORE INTO {self.tb_name} VALUES"
        query = " ".join([sql, phrase])
        self.logger.debug(query)
        print(query)
        self.__executer.run_query(query)

    def create_table_if_not_exists(self):
        schema = [
            ("datejyo_id", "INT", "PRIMARY KEY"),
            ("holddate", "DATE"),
            ("jyo_cd", "INT"),
            ("jyo_name", "VARCHAR(30)"),
            ("shinko", "VARCHAR(100)"),
            ("ed_race_no", "INT"),
        ]
        foreign_keys = ["jyo_cd"]
        refs = ["jyo_master"]
        sql_creator = MysqlCreator()
        query = sql_creator.sql_for_create_table(
            self.tb_name, schema, foreign_keys, refs
        )
        self.__executer.run_query(query)
