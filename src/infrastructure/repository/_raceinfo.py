from typing import Iterable


from domain.model.info import HoldRaceInfo
from domain.repository import RaceInfoRepository
from infrastructure.mysql.creator import MysqlCreator
from infrastructure.mysql.executer import MysqlExecuter


class MysqlRaceInfoRepositoryImpl(RaceInfoRepository):
    tb_name: str

    def __init__(self):
        self.tb_name = "holdjyo_tb"

    def save_info(self, data_itr: Iterable[HoldRaceInfo]) -> None:
        pass

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
        sql_executer = MysqlExecuter()
        sql_executer.run_query(query)