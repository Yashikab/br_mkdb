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


class JyoData2sql:

    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    def create_table_if_not_exists(self) -> None:
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        try:
            self.logger.debug(f'connecteng Mysql.')
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                # holdjyo_tbを作るクエリを読み込む
                # このファイルからの相対パスを実行ファイルの絶対パスに変換する
                self.logger.debug(f'creating table.')
                sql_path = \
                    Path(__file__).parent\
                                  .joinpath('query', 'jyodata_create_tb.sql')\
                                  .resolve()
                with open(sql_path, 'r') as f:
                    sql = f.read()
                    cursor.execute(sql)
                cursor.close()
                self.logger.debug('created table successfully!')
        except Exception:
            self.logger.warning(f'table is already exists.')

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
        sql = ''.join([sql, total_insert_value])

        try:
            self.logger.debug('Connect to MySQL')
            with MysqlConnector(const.MYSQL_CONFIG) as conn:
                cursor = conn.cursor()
                cursor.execute(sql)
                cursor.close()
        except Exception:
            self.logger.warning('Insert was unsucceeded')
