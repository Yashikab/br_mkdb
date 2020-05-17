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


class JyoData2sql(Data2MysqlTemplate):

    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    def create_table_if_not_exists(self) -> None:
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')

        status = super()._run_query_from_path('create_jyodata_tb.sql')
        if status == 0:
            self.logger.debug(f'creating table succeeded!')
        else:
            self.logger.debug(
                f'creating table failed or table has already exists.')

    def insert2table(self, date: int) -> None:
        """
        日付をyyyymmdd型で受けとり，その日のレース情報をMySQLに挿入する

        Parameters
        ----------
            date: int
            日付，yyyymmdd型
        """
        ghp = GetHoldPlacePast(target_date=date)
        hp_str_list = ghp.holdplace2strlist()
        hp_cd_list = ghp.holdplace2cdlist()
        shinkoinfo_dict = ghp.shinkoinfodict()
        holdrace_dict = ghp.holdracedict()
        # 重複時は無視する
        sql = "INSERT IGNORE INTO holdjyo_tb VALUES "
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
        query = ''.join([sql, total_insert_value])
        # 作成したクエリの実行
        status = super()._run_query(query)
        if status == 0:
            self.logger.debug('insert was succeeded!')
        else:
            self.logger.error('insert was failed.')


class RaceData2sql(Data2MysqlTemplate):

    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    def create_table_if_not_exists(self, tb_type: str) -> None:
        """
        外部キーの関係でholdjyo_tbがないとエラーになる
        """
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        if tb_type == 'raceinfo':
            filename = 'create_raceinfo_tb.sql'
        else:
            self.logger.error(f'tb_type: {tb_type} is not available.')
            return None

        status = super()._run_query_from_path(filename)
        if status == 0:
            self.logger.debug(f'creating table succeeded!')
        else:
            self.logger.debug(
                f'creating table failed or table has already exists.')

    def insert2table(self, date: int) -> None:
        pass
    #     """
    #     日付をyyyymmdd型で受けとり，その日のレース情報をMySQLに挿入する

    #     Parameters
    #     ----------
    #         date: int
    #         日付，yyyymmdd型
    #     """
    #     ghp = GetHoldPlacePast(target_date=date)
    #     hp_str_list = ghp.holdplace2strlist()
    #     hp_cd_list = ghp.holdplace2cdlist()
    #     shinkoinfo_dict = ghp.shinkoinfodict()
    #     holdrace_dict = ghp.holdracedict()
    #     # 重複時は無視する
    #     sql = "INSERT IGNORE INTO holdjyo_tb VALUES "
    #     insert_value_list = []
    #     for hp_s, hp_c in zip(hp_str_list, hp_cd_list):
    #         primary_key = int(f'{date}{hp_c:02}')
    #         shinko = shinkoinfo_dict[hp_s]
    #         holdrace_list = holdrace_dict[hp_s]
    #         if not holdrace_list:
    #             ed_race_no = 0
    #         else:
    #             ed_race_no = holdrace_list[-1]
    #         insert_value = f"({primary_key}, {date}, {hp_c}, "\
    #                        f"'{hp_s}', '{shinko}', {ed_race_no})"
    #         insert_value_list.append(insert_value)
    #     total_insert_value = ', '.join(insert_value_list)
    #     sql = ''.join([sql, total_insert_value])

    #     try:
    #         self.logger.debug('Connect to MySQL')
    #         with MysqlConnector(const.MYSQL_CONFIG) as conn:
    #             cursor = conn.cursor()
    #             cursor.execute(sql)
    #             cursor.close()
    #     except Exception as e:
    #         self.logger.error(f'{e}')
    #         self.logger.warning('Insert was unsucceeded')
