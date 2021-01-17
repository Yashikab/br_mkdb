# python 3.7.5
# coding: utf-8
'''
mysql.connector をwith構文で使えるようにする
'''


class MysqlConnector(object):
    def __init__(self, config):
        self.config = config

    def __enter__(self):
        import mysql.connector
        self.connect = mysql.connector.connect(
            **self.config
        )
        return self.connect

    def __exit__(self, exception_type, exception_value, traceback):
        self.connect.commit()
        self.connect.close()
