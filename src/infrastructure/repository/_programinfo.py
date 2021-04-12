from logging import getLogger
from typing import Iterator, List

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
        self.__executer = MysqlExecuter()
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
        self.__executer.run_query(query)

    def _create_player_table(self) -> None:
        self.logger.debug("Create table for player.")

        foreign_keys = ["race_id"]
        refs = ["raceinfo_tb"]
        query = self.__creator.sql_for_create_table(
            self.player_tb_name, self.player_schema, foreign_keys, refs
        )
        self.__executer.run_query(query)

    # common とplayer 分ける
    def save_info(self, pi_itr: Iterator[ProgramInfo]) -> None:
        common_insert_phrases = list()
        player_insert_phrases = list()
        common_cols = list(map(lambda x: x[0], self.common_schema))
        player_cols = list(map(lambda x: x[0], self.player_schema))
        for pi in pi_itr:
            holddate = self.__common.to_query_phrase(pi.date)
            datejyo_id = f"{holddate}{pi.jyo_cd:02}"
            race_id = f"{datejyo_id}{pi.race_no:02}"
            common_inserts = [race_id, datejyo_id]
            common_inserts += self.__common.get_insertlist(
                pi.common, common_cols[2:]
            )
            common_insert_phrases.append(f"({', '.join(common_inserts)})")
            player_insert_phrases.append(
                self._player_inserts(race_id, pi.players, player_cols)
            )

        common_phrase = ", ".join(common_insert_phrases)
        player_phrase = ", ".join(player_insert_phrases)
        common_sql = (
            f"INSERT IGNORE INTO {self.common_tb_name} VALUES {common_phrase};"
        )
        player_sql = (
            f"INSERT IGNORE INTO {self.player_tb_name} VALUES {player_phrase};"
        )
        self.logger.debug(common_sql)
        self.logger.debug(player_sql)
        print(player_sql)
        self.__executer.run_query(common_sql)
        self.__executer.run_query(player_sql)

    def _player_inserts(
        self,
        race_id: int,
        players_info: List[ProgramPlayerInfo],
        player_cols: List[str],
    ) -> str:
        players_insert_phrase = list()
        for player_info in players_info:
            waku_id = f"{race_id}{player_info.waku}"
            player_inserts = [waku_id, race_id]
            player_inserts += self.__common.get_insertlist(
                player_info, player_cols[2:]
            )
            players_insert_phrase.append(f"({', '.join(player_inserts)})")

        return ", ".join(players_insert_phrase)
