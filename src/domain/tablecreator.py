# テーブル作成用ドメイン
from abc import ABCMeta, abstractmethod

from domain.sql import SqlCreator, SqlExecuter

# TODO: tb nameやcolumnsを外から呼び出せるようにする。
# TODO: カラムはinfoから呼び出す(infoにshemaリストを持っていく)


class JyoMasterTableCreator:
    sql_executer: SqlExecuter
    tb_name: str = "jyo_master"

    def __init__(self, sql_executer: SqlExecuter):
        self.sql_executer = sql_executer

    def create_table(self) -> None:
        schema = [
            ("jyo_name", "VARCHAR(100)"),
            ("jyo_cd", "INT", "PRIMARY KEY")
        ]
        query = SqlCreator.sql_for_create_table(
            self.tb_name, schema)
        self.sql_executer.run_query(query)


class JyoDataTableCreator:
    sql_executer: SqlExecuter
    tb_name: str = "holdjyo_tb"

    def __init__(self, sql_executer: SqlExecuter):
        self.sql_executer = sql_executer

    def create_table(self):
        """開催場情報"""
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
        query = SqlCreator.sql_for_create_table(
            self.tb_name, schema, foreign_keys, refs
        )
        self.sql_executer.run_query(query)


class RaceInfoTableCreator:
    sql_executer: SqlExecuter

    def __init__(self, sql_executer: SqlExecuter):
        self.sql_executer = sql_executer

    def create_commoninfo_table(self):
        """レース共通情報"""
        tb_name = "raceinfo_tb"
        schema = [
            ("race_id", "BIGINT", "PRIMARY KEY"),
            ("datejyo_id", "INT"),
            ("taikai_name", "VARCHAR(100)"),
            ("grade", "VARCHAR(100)"),
            ("race_type", "VARCHAR(100)"),
            ("race_kyori", "INT"),
            ("is_antei", "BOOLEAN"),
            ("is_shinnyukotei", "BOOLEAN"),
        ]
        foreign_keys = ["datejyo_id"]
        refs = ["holdjyo_tb"]
        query = SqlCreator.sql_for_create_table(
            tb_name, schema, foreign_keys, refs)
        self.sql_executer.run_query(query)

    def create_playerinfo_table(self):
        """番組表情報"""
        tb_name = "program_tb"
        schema = [
            ("waku_id", "BIGINT", "PRIMARY KEY"),
            ("race_id", "BIGINT"),
            ("p_name", "VARCHAR(100)"),
            ("p_id", "INT"),
            ("p_level", "VARCHAR(30)"),
            ("p_home", "VARCHAR(30)"),
            ("p_birthplace", "VARCHAR(30)"),
            ("p_age", "INT"),
            ("p_weight", "FLOAT"),
            ("p_num_f", "INT"),
            ("p_num_l", "INT"),
            ("p_avg_st", "FLOAT"),
            ("p_all_1rate", "FLOAT"),
            ("p_all_2rate", "FLOAT"),
            ("p_all_3rate", "FLOAT"),
            ("p_local_1rate", "FLOAT"),
            ("p_local_2rate", "FLOAT"),
            ("p_local_3rate", "FLOAT"),
            ("motor_no", "INT"),
            ("motor_2rate", "FLOAT"),
            ("motor_3rate", "FLOAT"),
            ("boat_no", "INT"),
            ("boat_2rate", "FLOAT"),
            ("boat_3rate", "FLOAT")
        ]
        foreign_keys = ["race_id"]
        refs = ["raceinfo_tb"]
        query = SqlCreator.sql_for_create_table(
            tb_name, schema, foreign_keys, refs)
        self.sql_executer.run_query(query)


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
