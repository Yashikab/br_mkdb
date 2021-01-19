# テーブル作成用ドメイン
from abc import ABCMeta, abstractmethod

from domain.sql import SqlCreator, SqlExecuter


class JyoMasterTableCreator(metaclass=ABCMeta):
    sql_executer: SqlExecuter
    tb_name: str = "jyo_master"

    def __init__(self, sql_executer: SqlExecuter):
        self.sql_executer = sql_executer

    def create_table(self) -> None:
        schemas = [
            ("jyo_name", "VARCHAR(100)"),
            ("jyo_cd", "INT", "PRIMARY KEY")
        ]
        query = SqlCreator.sql_for_create_table(
            self.tb_name, schemas)
        self.sql_executer.run_query(query)


class JyoDataTableCreator(metaclass=ABCMeta):
    sql_executer: SqlExecuter
    tb_name: str = "holdjyo_tb"

    def __init__(self, sql_executer: SqlExecuter):
        self.sql_executer = sql_executer

    @abstractmethod
    def create_table(self):
        """開催場情報"""
        schemas = [
            ("datejyo_id", "INT", "PRIMARY KEY"),
            ("holddate", "DATE"),
            ("jyo_cd", "INT"),
            ("jyo_name", "VARCHAR(30)"),
            ("shinko", "VARCHAR(100)"),
            ("ed_race_no", "INT"),

        ]
        foreign_keys = ["jyo_cd"]
        refs = ["jyo_master"]
        query = SqlCreator.sql_for_create_table(
            self.tb_name, schemas, foreign_keys, refs
        )
        self.sql_executer.run_query(query)


class RaceInfoTableCreator(metaclass=ABCMeta):

    @abstractmethod
    def create_commoninfo_table(self):
        """レース共通情報"""
        pass

    @abstractmethod
    def create_playerinfo_table(self):
        """番組表情報"""
        pass


class ChokuzenTableCreator(metaclass=ABCMeta):

    @abstractmethod
    def create_commoninfo_table(self):
        """直前共通情報"""
        pass

    @abstractmethod
    def create_playerinfo_table(self):
        """直前選手情報"""
        pass


class ResultTableCreator(metaclass=ABCMeta):

    @abstractmethod
    def create_commoninfo_table(self):
        """結果共通情報"""
        pass

    @abstractmethod
    def create_playerinfo_table(self):
        """結果選手情報"""
        pass


class OddsTableCreator(metaclass=ABCMeta):

    @abstractmethod
    def create_threerentan_table(self):
        """3連単情報"""
        pass

    @abstractmethod
    def create_threefuku_table(self):
        """3連複情報"""
        pass

    @abstractmethod
    def create_tworentan_table(self):
        """2連単情報"""
        pass

    @abstractmethod
    def create_twofuku_table(self):
        """2連複情報"""
        pass

    @abstractmethod
    def create_tansho_table(self):
        """単勝情報"""
        pass
