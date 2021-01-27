import time
from logging import getLogger
from typing import List

from application.argument import DBType, Options
from domain.const import MAIN_LOGNAME
from domain.dbcontroller import DatabaseController
from domain.sql.executer import SqlExecuter
from domain.tablecreator import create_table
from module.dt2sql import (ChokuzenData2sql, JyoData2sql, Odds2sql,
                           RaceData2sql, ResultData2sql)
from module.getdata import DateRange as dr
from module.master2sql import JyoMaster2sql

# logger
logger = getLogger(MAIN_LOGNAME)


class BoatRaceUsecase:
    __dbctl: DatabaseController
    __sql_executer: SqlExecuter

    def __init__(self,
                 dbctl: DatabaseController,
                 sql_executer: SqlExecuter):
        self.__dbctl = dbctl
        self.__sql_executer

    def run(self, op: Options):
        logger.info('Connect MySQL server.')
        self.__dbctl.build()
        logger.info('Done')

        logger.info(f'Table Creating: {op.create_table}')
        logger.debug('load classes from dt2sql')
        jm2sql = JyoMaster2sql()
        jd2sql = JyoData2sql()
        rd2sql = RaceData2sql()
        cd2sql = ChokuzenData2sql()
        res2sql = ResultData2sql()
        odds2sql = Odds2sql()
        logger.debug('Completed loading classes.')

        if op.create_table:
            logger.debug('Create table if it does not exist.')
            create_table(self.__sql_executer)
            logger.debug('Completed creating table.')

        for date in dr.daterange(op.start_date, op.end_date):
            try:
                logger.debug(f'target date: {date}')
                jd2sql.insert2table(date)
                # jd2sqlで開催場と最終レース番を取得する
                logger.debug('insert race data: race chokuzen result odds')
                jyo_cd_list = jd2sql.map_raceno_dict.keys()
                start_time = time.time()
                logger.debug('Start to insert race data')
                rd2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)
                logger.debug('Start to insert chokuzen data')
                cd2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)
                logger.debug('Start to insert result data')
                res2sql.insert2table(date, jyo_cd_list,
                                     jd2sql.map_raceno_dict)
                logger.debug('Start to insert odds data')
                odds2sql.insert2table(
                    date, jyo_cd_list, jd2sql.map_raceno_dict)

                elapsed_time = time.time() - start_time
                logger.debug(f'completed in {elapsed_time}sec')
                logger.debug('insert race data completed.')
            except Exception as e:
                logger.error(f'{e}')

        # localは実験で落とすと消えてしまうので落とさない
        if op.db_type == DBType.gcs:
            logger.info('Down Server.')
            self.__dbctl.clean()

        logger.info('All completed.')

    @classmethod
    def localmysql(cls):
        from infrastructure.dbcontroller import LocalSqlController
        return BoatRaceUsecase(LocalSqlController())

    @classmethod
    def gcpmysql(cls):
        from infrastructure.dbcontroller import CloudSqlController
        return BoatRaceUsecase(CloudSqlController())
