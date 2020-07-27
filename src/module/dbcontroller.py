# python 3.7.5
# coding: utf-8
'''
google cloud sql proxyを通して, データを格納する
'''
from logging import getLogger
import os
import subprocess
from abc import ABCMeta, abstractmethod


class DatabaseController(metaclass=ABCMeta):
    @abstractmethod
    def build(self):
        """build DB"""
        pass

    @abstractmethod
    def clean(self):
        """del DB"""
        pass


class CloudSqlController(DatabaseController):
    """use cloud sql mysql"""

    def build(self):
        # TODO: Google cloud Mysql接続
        pass

    def clean(self):
        # TODO: Google cloud Mysql接続解除
        pass


class LocalSqlController(DatabaseController):
    """use local mysql db"""
    def __init__(self):
        self.logger = getLogger("DbCtl").getChild(self.__class__.__name__)

    def build(self):
        pwd = os.path.abspath(__file__)
        this_filename = os.path.basename(__file__)
        this_dir = pwd.replace(this_filename, '')
        diff_dir_for_sql = 'br_mkdb/src/module'
        sql_dir = \
            this_dir.replace(diff_dir_for_sql, 'mysql_local/boat')

        self.logger.debug(f'sql dir is {sql_dir}')
        os.chdir(sql_dir)
        try:
            # 先に前のゾンビ達は処理しておく，なければエラー履くのでスキップ
            subprocess.run(["docker-compose", "down"])
            subprocess.run(["docker", "volume", "rm", "boat_mysql"])
        except Exception as e:
            self.logger.warning(e)

        subprocess.run(["docker-compose", "up", "-d"])

    def clean(self):
        # TODO: 接続解除記述
        pass
