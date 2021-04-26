from logging import getLogger
from typing import Iterator

from domain.model.info import ProgramCommonInfo, ProgramInfo, ProgramPlayerInfo
from domain.repository import ProgramInfoRepository
from infrastructure.const import MODULE_LOG_NAME
from infrastructure.mysql import MysqlCreator, MysqlExecuter

from ._common import CommonMethod


class MysqlProgramInfoRepositoryImpl(ProgramInfoRepository):
    def __init__(self):
        self.logger = getLogger(MODULE_LOG_NAME).getChild(
            self.__class__.__name__
        )
        self.executer = MysqlExecuter()
        self.__creator = MysqlCreator()
        self.__common = CommonMethod()
        self.common_tb_name = "raceinfo_tb"
        self.player_tb_name = "program_tb"
        self.common_schema = [
            ("race_id", "BIGINT", "PRIMARY KEY"),
            ("datejyo_id", "INT"),
        ]
        # annotationを使う
        for var_name, var_type in ProgramCommonInfo.__annotations__.items():
            self.common_schema.append(
                (var_name, self.__creator.get_sqltype_from_pytype(var_type))
            )
        self.player_schema = [
            ("waku_id", "BIGINT", "PRIMARY KEY"),
            ("race_id", "BIGINT"),
        ]
        for var_name, var_type in ProgramPlayerInfo.__annotations__.items():
            self.player_schema.append(
                (var_name, self.__creator.get_sqltype_from_pytype(var_type))
            )

    def create_table_if_not_exists(self) -> None:
        self.logger.info("Create table if not exists.")
        self._create_common_table()
        self._create_player_table()

    def _create_common_table(self) -> None:
        self.logger.debug("Create table for common info.")

        foreign_keys = ["datejyo_id"]
        refs = ["holdjyo_tb"]
        query = self.__creator.sql_for_create_table(
            self.common_tb_name, self.common_schema, foreign_keys, refs
        )
        self.executer.run_query(query)

    def _create_player_table(self) -> None:
        self.logger.debug("Create table for player.")

        foreign_keys = ["race_id"]
        refs = ["raceinfo_tb"]
        query = self.__creator.sql_for_create_table(
            self.player_tb_name, self.player_schema, foreign_keys, refs
        )
        self.executer.run_query(query)

    def save_info(self, pi_itr: Iterator[ProgramInfo]) -> None:

        self.__common.common_player_save_info(
            pi_itr,
            self.common_tb_name,
            self.common_schema,
            self.player_tb_name,
            self.player_schema,
            self.executer,
        )
