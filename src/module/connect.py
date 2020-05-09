# python 3.7.5
# coding: utf-8
import mysql.connector


class MySQL():
    def __init__(self, config):
        u"""
        :param config: 接続設定を格納した辞書
        """
        self.config = config
        self.conn = None
        if config is not None:
            self.connect()

    def connect(self, config=None):
        u"""
        MySQLに接続する。
        :return:
        """
        if config is None:
            config = self.config
        conn = mysql.connector.connect(**config)
        self.conn = conn
        return conn
