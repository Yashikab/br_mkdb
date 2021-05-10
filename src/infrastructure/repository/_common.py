from dataclasses import asdict
from datetime import date
from logging import getLogger
from typing import Any, Iterator, List, Union

from domain.model.info import ChokuzenInfo, ProgramInfo, ResultInfo
from infrastructure.const import MODULE_LOG_NAME
from infrastructure.mysql.executer import MysqlExecuter
from tqdm import tqdm


class CommonMethod:
    def __init__(self):
        self.logger = getLogger(MODULE_LOG_NAME).getChild(
            self.__class__.__name__
        )

    def to_query_phrase(self, value: Any) -> str:
        """ valueをsqlに挿入できる形にする"""
        if isinstance(value, str):
            # ''で囲む
            value = f"'{value}'"
        elif isinstance(value, date):
            value = value.strftime("%Y%m%d")
        # weatherinfo用に開発する必要がある(dataclassは再帰的に分岐とか)
        elif value is None:
            value = "null"
        else:
            # "hoge" ならそれで統一する
            value = f"{value}"
        return value

    def get_insertlist(self, data_obj: Any, cols: List[str]) -> str:
        """データ挿入用に文字列を変換し、リストで返す。

        Parameters
        ----------
        data_obj : Any
            受け渡し用型(HoldRaceInfoとか)
        cols : List[str]
            挿入順のカラムリスト

        Returns
        -------
        List[str]
            変換したリスト(挿入順)
        """
        inserts = list()
        data_dict = asdict(data_obj)
        for col in cols:
            inserts.append(self.to_query_phrase(self._unpack(data_dict, col)))
        return inserts

    # weather infoが入れ子構造になっているため必要
    def _unpack(self, dct: dict, col: str):
        if col in dct.keys():
            return dct[col]
        else:
            for k in dct.keys():
                if isinstance(dct[k], dict):
                    return self._unpack(dct[k], col)
            raise KeyError(f"key({col}) does not exist recursively.")

    def common_player_save_info(
        self,
        data_itr: Iterator[Union[ProgramInfo, ChokuzenInfo, ResultInfo]],
        common_tb_name: str,
        common_schema: list,
        player_tb_name: str,
        player_schema: list,
        executer: MysqlExecuter,  # TODO MysqlExecuterのdomainクラスを作る
    ):
        """番組、直前、結果のための挿入用共通メソッド

        Parameters
        ----------
        data_itr : Iterator[Union[ProgramInfo, ChokuzenInfo, ResultInfo]]
            [description]
        """
        common_insert_phrases = list()
        common_cols = list(map(lambda x: x[0], common_schema))
        player_insert_phrases = list()
        player_cols = list(map(lambda x: x[0], player_schema))
        for di in tqdm(data_itr):
            holddate = self.to_query_phrase(di.date)
            datejyo_id = f"{holddate}{di.jyo_cd:02}"
            race_id = f"{datejyo_id}{di.race_no:02}"
            common_inserts = [race_id, datejyo_id]
            common_inserts += self.get_insertlist(di.common, common_cols[2:])
            common_insert_phrases.append(f"({', '.join(common_inserts)})")
            player_insert_phrases.append(
                self._player_inserts(race_id, di.players, player_cols)
            )
        common_phrase = ", ".join(common_insert_phrases)
        common_sql = (
            f"INSERT IGNORE INTO {common_tb_name} VALUES {common_phrase};"
        )
        player_phrase = ", ".join(player_insert_phrases)
        player_sql = (
            f"INSERT IGNORE INTO {player_tb_name} VALUES {player_phrase};"
        )
        self.logger.debug(common_sql)
        executer.run_query(common_sql)
        self.logger.debug(player_sql)
        executer.run_query(player_sql)

    def _player_inserts(
        self,
        race_id: int,
        players_info,
        player_cols,
    ) -> str:
        players_insert_phrase = list()
        for player_info in players_info:
            waku_id = f"{race_id}{player_info.waku}"
            player_inserts = [waku_id, race_id]
            player_inserts += self.get_insertlist(player_info, player_cols[2:])
            players_insert_phrase.append(f"({', '.join(player_inserts)})")

        return ", ".join(players_insert_phrase)
