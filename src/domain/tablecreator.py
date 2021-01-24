# テーブル作成用ドメイン
from domain.model.info import (
    ChokuzenPlayerInfo, ProgramCommonInfo,
    ProgramPlayerInfo, ResultCommonInfo, ResultPlayerInfo, WeatherInfo,
)
from domain.sql import SqlCreator, SqlExecuter

# TODO クラスごと外部キーで依存してていいのか？


class TableCreator:
    sql_executer: SqlExecuter
    sql_creator: SqlCreator

    def __init__(self, sql_executer: SqlExecuter):
        self.sql_executer = sql_executer
        self.sql_creator = SqlCreator()

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

    def create_commoninfo_table(self):
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

    def create_playerinfo_table(self):
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

    def create_commoninfo_table(self):
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

    def create_playerinfo_table(self):
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

    def create_commoninfo_table(self):
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

    def create_playerinfo_table(self):
        """結果選手情報"""
        tb_name = "p_result_tb"
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


class OddsTableCreator:

    def create_threerentan_table(self):
        """3連単情報"""
        pass

    def create_threefuku_table(self):
        """3連複情報"""
        pass

    def create_tworentan_table(self):
        """2連単情報"""
        pass

    def create_twofuku_table(self):
        """2連複情報"""
        pass

    def create_tansho_table(self):
        """単勝情報"""
        pass
