# テーブル作成用ドメイン
import copy
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from domain.model.info import (ChokuzenPlayerInfo, ProgramCommonInfo,
                               ProgramPlayerInfo, ResultCommonInfo,
                               ResultPlayerInfo, Tansho, ThreeRenfuku,
                               ThreeRentan, TwoRenfuku, TwoRentan, WeatherInfo)
from domain.sql import SqlCreator, SqlExecuter

# TODO : Run Create Tableはinfraに追いやる


def create_table(sql_executer) -> Optional[Exception]:
    try:
        table_creators = []
        table_creators.append(JyoMasterTableCreator(sql_executer))
        table_creators.append(JyoDataTableCreator(sql_executer))
        table_creators.append(RaceInfoTableCreator(sql_executer))
        table_creators.append(ChokuzenTableCreator(sql_executer))
        table_creators.append(ResultTableCreator(sql_executer))
        table_creators.append(OddsTableCreator(sql_executer))
        for tc in table_creators:
            tc.create_table()
    except Exception as e:
        return e


class TableCreator(metaclass=ABCMeta):
    sql_executer: SqlExecuter
    sql_creator: SqlCreator

    def __init__(self, sql_executer: SqlExecuter):
        self.sql_executer = sql_executer
        self.sql_creator = SqlCreator()

    @abstractmethod
    def create_table(self) -> None:
        raise NotImplementedError()

    def run_create_table(self,
                         tb_name,
                         schema,
                         foreign_keys=None,
                         refs=None) -> None:
        query = self.sql_creator.sql_for_create_table(
            tb_name, schema, foreign_keys, refs
        )
        self.sql_executer.run_query(query)


class JyoMasterTableCreator(TableCreator):

    def create_table(self) -> None:
        tb_name = "jyo_master"
        schema = [
            ("jyo_name", "VARCHAR(100)"),
            ("jyo_cd", "INT", "PRIMARY KEY")
        ]
        super().run_create_table(tb_name, schema)
        sql = f"INSERT IGNORE INTO {tb_name} VALUES"
        insert_value = ', '.join([
            val for val in self._csv2rows_generator()])
        query = ' '.join([sql, insert_value])
        self.sql_executer.run_query(query)

    def _csv2rows_generator(self):
        csv_filepath = Path(__file__).parent\
                                     .joinpath("jyo_master.csv")\
                                     .resolve()
        jyomaster_df = pd.read_csv(csv_filepath, header=0)
        for name, cd in zip(jyomaster_df.jyo_name, jyomaster_df.jyo_cd):
            yield f"(\"{name}\", {cd})"


class JyoDataTableCreator(TableCreator):

    def create_table(self):
        """開催場情報"""
        tb_name: str = "holdjyo_tb"
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
        super().run_create_table(
            tb_name,
            schema,
            foreign_keys,
            refs
        )


class RaceInfoTableCreator(TableCreator):

    def create_table(self) -> None:
        self._create_commoninfo_table()
        self._create_playerinfo_table()
        return None

    def _create_commoninfo_table(self):
        """レース共通情報"""
        tb_name = "raceinfo_tb"
        schema = [
            ("race_id", "BIGINT", "PRIMARY KEY"),
            ("datejyo_id", "INT"),
        ]
        # annotationを使う
        for var_name, var_type in ProgramCommonInfo.__annotations__.items():
            schema.append(
                (var_name,
                 self.sql_creator.get_sqltype_from_pytype(var_type))
            )
        foreign_keys = ["datejyo_id"]
        refs = ["holdjyo_tb"]
        super().run_create_table(
            tb_name,
            schema,
            foreign_keys,
            refs
        )

    def _create_playerinfo_table(self):
        """番組表情報"""
        tb_name = "program_tb"
        schema = [
            ("waku_id", "BIGINT", "PRIMARY KEY"),
            ("race_id", "BIGINT")
        ]
        for var_name, var_type in ProgramPlayerInfo.__annotations__.items():
            schema.append(
                (var_name,
                 self.sql_creator.get_sqltype_from_pytype(var_type)
                 )
            )
        foreign_keys = ["race_id"]
        refs = ["raceinfo_tb"]
        super().run_create_table(
            tb_name,
            schema,
            foreign_keys,
            refs
        )


class ChokuzenTableCreator(TableCreator):

    def create_table(self) -> None:
        self._create_commoninfo_table()
        self._create_playerinfo_table()
        return None

    def _create_commoninfo_table(self):
        """直前共通情報"""
        tb_name = "chokuzen_cond_tb"
        schema = [
            ("race_id", "BIGINT", "PRIMARY KEY"),
            ("datejyo_id", "INT"),
        ]
        # annotationを使う
        for var_name, var_type in WeatherInfo.__annotations__.items():
            schema.append(
                (var_name,
                 self.sql_creator.get_sqltype_from_pytype(var_type))
            )
        foreign_keys = ["race_id"]
        refs = ["raceinfo_tb"]
        super().run_create_table(
            tb_name,
            schema,
            foreign_keys,
            refs
        )

    def _create_playerinfo_table(self):
        """直前選手情報"""
        tb_name = "chokuzen_player_tb"
        schema = [
            ("waku_id", "BIGINT", "PRIMARY KEY"),
            ("race_id", "BIGINT"),
        ]
        # annotationを使う
        for var_name, var_type in ChokuzenPlayerInfo.__annotations__.items():
            schema.append(
                (var_name,
                 self.sql_creator.get_sqltype_from_pytype(var_type))
            )
        foreign_keys = ["waku_id", "race_id"]
        refs = ["program_tb", "chokuzen_cond_tb"]
        super().run_create_table(
            tb_name,
            schema,
            foreign_keys,
            refs
        )


class ResultTableCreator(TableCreator):

    def create_table(self) -> None:
        self._create_commoninfo_table()
        self._create_playerinfo_table()
        return None

    def _create_commoninfo_table(self):
        """結果共通情報"""
        tb_name = "race_result_tb"
        schema = [
            ("race_id", "BIGINT", "PRIMARY KEY"),
            ("datejyo_id", "INT"),
        ]
        # annotationを使う
        for var_name, var_type in ResultCommonInfo.__annotations__.items():
            schema.append(
                (var_name,
                 self.sql_creator.get_sqltype_from_pytype(var_type))
            )
        foreign_keys = ["race_id"]
        refs = ["raceinfo_tb"]
        super().run_create_table(
            tb_name,
            schema,
            foreign_keys,
            refs
        )

    def _create_playerinfo_table(self):
        """結果選手情報"""
        tb_name = "player_result_tb"
        schema = [
            ("waku_id", "BIGINT", "PRIMARY KEY"),
            ("race_id", "BIGINT"),
        ]
        # annotationを使う
        for var_name, var_type in ResultPlayerInfo.__annotations__.items():
            schema.append(
                (var_name,
                 self.sql_creator.get_sqltype_from_pytype(var_type))
            )
        foreign_keys = ["race_id", "waku_id"]
        refs = ["race_result_tb", "program_tb"]
        super().run_create_table(
            tb_name,
            schema,
            foreign_keys,
            refs
        )


class OddsTableCreator(TableCreator):
    __ids: Tuple[str]
    __foreign_keys: List[str]
    __refs: List[str]

    def __init__(self, sql_executer: SqlExecuter):
        super().__init__(sql_executer)
        self.__ids = [("race_id", "BIGINT", "PRIMARY KEY")]
        self.__foreign_keys = ["race_id"]
        self.__refs = ["raceinfo_tb"]

    def create_table(self) -> None:
        self._create_threerentan_table()
        self._create_threefuku_table()
        self._create_tworentan_table()
        self._create_twofuku_table()
        self._create_tansho_table()

        return None

    def _create_threerentan_table(self):
        """3連単情報"""
        tb_name = "odds_3tan_tb"
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in ThreeRentan.__annotations__.items():
            schema.append(
                (var_name, self.sql_creator.get_sqltype_from_pytype(var_type)))

        super().run_create_table(
            tb_name,
            schema,
            self.__foreign_keys,
            self.__refs
        )

    def _create_threefuku_table(self):
        """3連複情報"""
        tb_name = "odds_3fuku_tb"
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in ThreeRenfuku.__annotations__.items():
            schema.append(
                (var_name, self.sql_creator.get_sqltype_from_pytype(var_type)))
        super().run_create_table(
            tb_name,
            schema,
            self.__foreign_keys,
            self.__refs
        )

    def _create_tworentan_table(self):
        """2連単情報"""
        tb_name = "odds_2tan_tb"
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in TwoRentan.__annotations__.items():
            schema.append(
                (var_name, self.sql_creator.get_sqltype_from_pytype(var_type)))
        super().run_create_table(
            tb_name,
            schema,
            self.__foreign_keys,
            self.__refs
        )

    def _create_twofuku_table(self):
        """2連複情報"""
        tb_name = "odds_2fuku_tb"
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in TwoRenfuku.__annotations__.items():
            schema.append(
                (var_name, self.sql_creator.get_sqltype_from_pytype(var_type)))
        super().run_create_table(
            tb_name,
            schema,
            self.__foreign_keys,
            self.__refs
        )

    def _create_tansho_table(self):
        """単勝情報"""
        tb_name = "odds_1tan_tb"
        schema = copy.deepcopy(self.__ids)
        for var_name, var_type in Tansho.__annotations__.items():
            schema.append(
                (var_name, self.sql_creator.get_sqltype_from_pytype(var_type)))
        super().run_create_table(
            tb_name,
            schema,
            self.__foreign_keys,
            self.__refs
        )
