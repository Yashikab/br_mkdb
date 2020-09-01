# python 3.7.5
# coding: utf-8
"""
fixされたデータをsqlへ保存する。
jyo_masterを入れる
"""
from logging import getLogger
import pandas as pd
from pathlib import Path

from module import const
from module.dt2sql import Data2MysqlTemplate


class JyoMaster2sql(Data2MysqlTemplate):
    __tb_name = 'jyo_master'

    def __init__(self):
        self.logger = \
            getLogger(const.MODULE_LOG_NAME).getChild(self.__class__.__name__)
        super().__init__(
            filename_list=['create_jyocd_master_tb.sql']
        )

    def create_table_if_not_exists(self):
        self.logger.debug('create jyo master tb')
        super().create_table_if_not_exists()
        # TODO csvのinsertもここでやる
        self.logger.debug('insert rows from csv.')
        sql = f"INSERT IGNORE INTO {self.__tb_name} VALUES"
        insert_value = ', '.join([
            val for val in self._csv2rows_generator()])
        query = ' '.join([sql, insert_value])
        self.run_query(query)
        self.logger.debug(f'insert to {self.__tb_name} done.')
        return None

    def _csv2rows_generator(self):
        csv_filepath = Path(__file__).parent\
                                     .joinpath(f'{self.__tb_name}.csv')\
                                     .resolve()
        jyomaster_df = pd.read_csv(csv_filepath, header=0)
        for name, cd in zip(jyomaster_df.jyo_name, jyomaster_df.jyo_cd):
            yield f"(\"{name}\", {cd})"
