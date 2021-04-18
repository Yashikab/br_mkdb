from typing import Iterator
from logging import getLogger
from infrastructure.const import MODULE_LOG_NAME
from domain.model.info import (
    ResultCommonInfo,
    ResultInfo,
    ResultPlayerInfo,
    WeatherInfo,
)
from domain.repository import ResultInfoRepository
from infrastructure.mysql import MysqlExecuter, MysqlCreator
from ._common import CommonMethod


class MysqlResultInfoRepositoryImpl(ResultInfoRepository):
    def __init__(self) -> None:
        self.logger = getLogger(MODULE_LOG_NAME).getChild(
            self.__class__.__name__
        )
        self.executer = MysqlExecuter()
        self.__creator = MysqlCreator()
        self.__common = CommonMethod()
        self.common_tb_name = "race_result_tb"
        self.player_tb_name = "player_result_tb"
        self.common_schema = [
            ("race_id", "BIGINT", "PRIMARY KEY"),
            ("datejyo_id", "INT"),
        ]
        # annotationを使う
        for var_name, var_type in ResultCommonInfo.__annotations__.items():
            if var_type == WeatherInfo:
                for (
                    weather_name,
                    weather_type,
                ) in WeatherInfo.__annotations__.items():
                    self.common_schema.append(
                        (
                            weather_name,
                            self.__creator.get_sqltype_from_pytype(
                                weather_type
                            ),
                        )
                    )
            else:
                self.common_schema.append(
                    (var_name, self.__creator.get_sqltype_from_pytype(var_type))
                )
        self.player_schema = [
            ("waku_id", "BIGINT", "PRIMARY KEY"),
            ("race_id", "BIGINT"),
        ]
        for var_name, var_type in ResultPlayerInfo.__annotations__.items():
            self.player_schema.append(
                (var_name, self.__creator.get_sqltype_from_pytype(var_type))
            )

    def create_table_if_not_exists(self) -> None:
        self.logger.info("Create table if not exists.")
        self._create_common_table()
        self._create_player_table()

    def _create_common_table(self) -> None:
        self.logger.debug("Create table for common info.")

        foreign_keys = ["race_id"]
        refs = ["raceinfo_tb"]
        query = self.__creator.sql_for_create_table(
            self.common_tb_name, self.common_schema, foreign_keys, refs
        )
        self.executer.run_query(query)

    def _create_player_table(self) -> None:
        self.logger.debug("Create table for player.")

        foreign_keys = ["waku_id", "race_id"]
        refs = ["program_tb", "race_result_tb"]
        query = self.__creator.sql_for_create_table(
            self.player_tb_name, self.player_schema, foreign_keys, refs
        )
        self.executer.run_query(query)

    # TODO この辺なにかのパターン使えそう
    def save_info(self, res_itr: Iterator[ResultInfo]) -> None:
        self.__common.common_player_save_info(
            res_itr,
            self.common_tb_name,
            self.common_schema,
            self.player_tb_name,
            self.player_schema,
            self.executer,
        )
