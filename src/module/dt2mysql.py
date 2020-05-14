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
import mysql.connector
# from module.getdata import DateList as dtl
# from module.getdata import GetHoldPlacePast


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


class JyoData2Mysql(Data2MysqlTemplate):

    def __init__(self):
        self.logger = getLogger(__class__.__name__)

    def create_table_if_not_exists(self):
        self.logger.info(f'called {sys._getframe().f_code.co_name}.')
        conn = mysql.connector.connect(**const.MYSQL_CONFIG)
        cursor = conn.cursor(buffered=True)
        try:
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
            self.logger.debug('created table successfully!')
        except FileExistsError:
            self.logger.warning(f'table is already exists.')
        cursor.close()
        conn.close()

    def insert2table(self):
        pass
