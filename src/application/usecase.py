from logging import getLogger
import time

from domain.argument import Options, DBType
from module.const import MAIN_LOGNAME
from module.dbcontroller import (
    LocalSqlController,
    CloudSqlController
)
from module.dt2sql import (
    JyoData2sql,
    RaceData2sql,
    ChokuzenData2sql,
    ResultData2sql,
    Odds2sql
)
from module.getdata import DateRange as dr
from module.master2sql import JyoMaster2sql


# logger
logger = getLogger(MAIN_LOGNAME)


def run(op: Options):

    logger.info('Connect MySQL server.')
    if op.db_type == DBType.gcs:
        logger.debug('use Google Cloud SQL.')
        sql_ctl = CloudSqlController()
    elif op.db_type == DBType.local:
        logger.debug('use local mysql server.')
        sql_ctl = LocalSqlController()
    else:
        raise Exception("Couldn't build sql controller")
    sql_ctl.build()
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
        jm2sql.create_table_if_not_exists()
        jd2sql.create_table_if_not_exists()
        rd2sql.create_table_if_not_exists()
        cd2sql.create_table_if_not_exists()
        res2sql.create_table_if_not_exists()
        odds2sql.create_table_if_not_exists()
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
            res2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)
            logger.debug('Start to insert odds data')
            odds2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)

            elapsed_time = time.time() - start_time
            logger.debug(f'completed in {elapsed_time}sec')
            logger.debug('insert race data completed.')
        except Exception as e:
            logger.error(f'{e}')

    # localは実験で落とすと消えてしまうので落とさない
    if op.db_type == DBType.gcs:
        logger.info('Down Server.')
        sql_ctl.clean()

    logger.info('All completed.')
