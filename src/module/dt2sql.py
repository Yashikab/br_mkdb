# python 3.7.5
# coding: utf-8
"""
一定期間の過去のデータを取得．
最新データ取得用プログラムではない．
スクレイピングを行い, mysqlにデータを格納
"""
import sys
from abc import ABCMeta, abstractmethod
from logging import getLogger
# from datetime import datetime
from pathlib import Path

from module import const
from module.connect import MysqlConnector
from module.getdata import GetHoldPlacePast
from module.getdata import OfficialProgram


class Data2MysqlTemplate(metaclass=ABCMeta):

    @abstractmethod
    def create_table_if_not_exists(self):
        '''
        テーブルがなければ作成する
        '''
        pass

    @abstractmethod
    def insert2table(self):
        '''
        データを挿入する
        '''
        pass

    def _run_query(self, query: str) -> int:
        """
        クエリを実行する

        Parameters
        ----------
            query :str
                クエリ文

        Return
        ------
            status :int
                成功したら0，失敗したら1
        """
        try:
            self.logger.debug(f'connecteng Mysql.')
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                self.logger.debug(f'run query.')
                cursor.execute(query)
                cursor.close()
                self.logger.debug('query run successfully!')
            status = 0
        except Exception as e:
            self.logger.error(f'{e}')
            status = 1
        return status

    def _run_query_from_path(self, filename: str) -> int:
        """
        queryフォルダ内のファイル名を指定してクエリを実行する

        Parameters
        ----------
            filename : str
                クエリのファイル名

        Returns
        -------
            status : int
                成功したら0，失敗したら1
        """
        # パスの指定
        query_filepath = \
            Path(__file__).parent\
                          .joinpath('query', filename)\
                          .resolve()
        self.logger.debug(f'run query from {query_filepath}')
        with open(query_filepath, 'r') as f:
            query = f.read()
            status = self._run_query(query)

        return status

    def _info2insertvalue(self,
                          id_list: list,
                          info_dict: dict,
                          ommit_list: list = []) -> str:
        """
        選手の情報の辞書からsqlへインサートするvalueを作成する
        注意：テーブルのカラムの順番とinfo_dict.keys()の順番が一致していること

        Parameters
        ----------
            id_list : list
                insertするidたち
            info_dict: dict
                getdataから得られたdict
            ommit_list: list = []
                insertしない要素

        Returns
        -------
            insert_value : str
        """
        # idを格納する
        insert_value_list = list(map(lambda x: f"{x}", id_list))
        # python3.7から辞書型で順序を保持する
        for i_key in info_dict.keys():
            i_value = info_dict[i_key]
            if type(i_value) is str:
                # ''で囲む
                i_value = f"'{i_value}'"
            else:
                # "hoge" ならそれで統一する
                i_value = f"{i_value}"
            if i_value not in ommit_list:
                insert_value_list.append(i_value)

        insert_value_content = ', '.join(insert_value_list)
        insert_value = "(" + insert_value_content + ")"
        return insert_value


class JyoData2sql(Data2MysqlTemplate):

    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    def create_table_if_not_exists(self) -> int:
        """
        テーブルの作成

        Returns
        -------
            status: int
                成功したら0, 失敗したら1
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')

        status = super()._run_query_from_path('create_jyodata_tb.sql')
        return status

    def insert2table(self, date: int) -> int:
        """
        日付をyyyymmdd型で受けとり，その日のレース情報をMySQLに挿入する

        Parameters
        ----------
            date: int
            日付，yyyymmdd型

        Returns
        -------
            status: int
                成功したら0, 失敗したら1
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        ghp = GetHoldPlacePast(target_date=date)
        hp_str_list = ghp.holdplace2strlist()
        hp_cd_list = ghp.holdplace2cdlist()
        shinkoinfo_dict = ghp.shinkoinfodict()
        holdrace_dict = ghp.holdracedict()
        # 重複時は無視する
        sql = "INSERT IGNORE INTO holdjyo_tb VALUES"
        insert_value_list = []
        for hp_s, hp_c in zip(hp_str_list, hp_cd_list):
            primary_key = int(f'{date}{hp_c:02}')
            shinko = shinkoinfo_dict[hp_s]
            holdrace_list = holdrace_dict[hp_s]
            if not holdrace_list:
                ed_race_no = 0
            else:
                ed_race_no = holdrace_list[-1]
            insert_value = f"({primary_key}, {date}, {hp_c}, "\
                           f"'{hp_s}', '{shinko}', {ed_race_no})"
            insert_value_list.append(insert_value)
        total_insert_value = ', '.join(insert_value_list)
        query = ' '.join([sql, total_insert_value])
        # 作成したクエリの実行
        status = super()._run_query(query)
        return status


class RaceData2sql(Data2MysqlTemplate):

    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    def create_table_if_not_exists(self, tb_type: str = 'all') -> int:
        """
        外部キーの関係でholdjyo_tbがないとエラーになる

        Returns
        -------
            status: int
                成功したら0, 失敗したら1
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        filename_list = []
        if tb_type == 'raceinfo' or 'all':
            filename_list.append('create_raceinfo_tb.sql')
        elif tb_type == 'program' or 'all':
            filename_list.append('create_program_tb.sql')
        else:
            self.logger.error(f'tb_type: {tb_type} is not available.')
            return None

        for filename in filename_list:
            status = super()._run_query_from_path(filename)
        return status

    def insert2table(self, date: int, jyo_cd: int, race_no: int) -> int:
        """
        日付，会場コード，レース番号を受取る \n
        レース情報を挿入し続けて，番組表情報を挿入する \n
        create_tableのようにタイプ分けはしない
        （opを一回の読み込みで終わらせたい）

        Parameters
        ----------
            date: int
                日付，yyyymmdd型
            jyo_cd : int
                会場コード
            race_no : int
                レース番号

        Returns
        -------
            status: int
                成功したら0, 失敗したら1
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        self.logger.info(f'args: {date}, {jyo_cd}, {race_no}')
        self.logger.debug(f'start insert raceinfo')
        op = OfficialProgram(race_no=race_no, jyo_code=jyo_cd, date=date)

        # 各種id
        raceinfo_id = int(f"{date}{jyo_cd:02}{race_no:02}")
        datejyo_id = int(f"{date}{jyo_cd:02}")
        # 重複時は無視する
        sql = "INSERT IGNORE INTO raceinfo_tb VALUES"
        insert_value = super()._info2insertvalue(
            id_list=[raceinfo_id, datejyo_id, date, jyo_cd, race_no],
            info_dict=op.raceinfo2dict()
        )
        query = ' '.join([sql, insert_value])
        # 作成したクエリの実行
        status = super()._run_query(query)
        self.logger.debug(f'insert raceinfo done.')

        self.logger.debug(f'start insert program info.')
        # 1~6枠でループ，データ取得でエラーの場合はインサートされない
        sql = "INSERT IGNORE INTO program_tb VALUES"
        for waku in range(1, 7):
            wakuinfo_id = int(f"{raceinfo_id}{waku}")
            try:
                insert_value = super()._info2insertvalue(
                    id_list=[wakuinfo_id, raceinfo_id],
                    info_dict=op.getplayerinfo2dict(waku)
                )
                query = ' '.join([sql, insert_value])
                super()._run_query(query)
            except Exception as e:
                self.logger.error(f'waku[{waku}]: {e}')

        return status


class ChokuzenData2sql(Data2MysqlTemplate):
    """大部分がRaceInfoと似ているが，
    リアルタムデータ取得時のため別クラスにする"""

    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    def create_table_if_not_exists(self, tb_type: str = 'all') -> int:
        """
        外部キーの関係でholdjyo_tbがないとエラーになる

        Returns
        -------
            status: int
                成功したら0, 失敗したら1
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        filename_list = []
        if tb_type == 'condition' or 'all':
            filename_list.append('create_chokuzen_cond_tb.sql')
        else:
            self.logger.error(f'tb_type: {tb_type} is not available.')
            return None

        for filename in filename_list:
            status = super()._run_query_from_path(filename)
        return status

    def insert2table(self):
        pass
