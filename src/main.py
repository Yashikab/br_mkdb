# python 3.7.5
# coding: utf-8
"""
MYSQLへ公式データを格納する
"""
import argparse
from datetime import datetime
from logging import (
    getLogger,
    Formatter,
    StreamHandler,
    INFO,
    WARNING
)
import time

import coloredlogs

from module.const import (
    MODULE_LOG_NAME,
    FMT,
    DATE_FMT,
    CL_FIELD_STYLES,
    CL_LEVEL_STYLES,
)
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
logger = getLogger(__name__)


def main():
    # コマンドライン引数オプション
    parser = argparse.ArgumentParser(description='Insert data to MySQL.')
    parser.add_argument('st_date',
                        type=str,
                        help='start date with y-m-d')
    parser.add_argument('ed_date',
                        type=str,
                        help='end date with y-m-d')
    parser.add_argument('--wait',
                        type=float,
                        default=0.5,
                        help='waiting time')
    parser.add_argument('--table',
                        action='store_true',
                        help='if you want to create table.')
    parser.add_argument(
        '--gcs',
        action='store_true',
        help='if you want to use gcs as MySQL db.'
    )

    args = parser.parse_args()
    st_date = datetime.strptime(args.st_date, '%Y-%m-%d')
    ed_date = datetime.strptime(args.ed_date, '%Y-%m-%d')
    logger.info(f'Insert data between {st_date} and {ed_date}')

    logger.info('Connect MySQL server.')
    if args.gcs:
        logger.debug('use Google Cloud SQL.')
        sql_ctl = CloudSqlController()
    else:
        logger.debug('use local mysql server.')
        sql_ctl = LocalSqlController()
    sql_ctl.build()
    logger.info('Done')

    logger.info(f'Table Creating: {args.table}')
    logger.debug('load classes from dt2sql')
    jm2sql = JyoMaster2sql()
    jd2sql = JyoData2sql()
    rd2sql = RaceData2sql()
    cd2sql = ChokuzenData2sql()
    res2sql = ResultData2sql()
    odds2sql = Odds2sql()
    logger.debug('Completed loading classes.')

    if args.table:
        logger.debug('Create table if it does not exist.')
        jm2sql.create_table_if_not_exists()
        jd2sql.create_table_if_not_exists()
        rd2sql.create_table_if_not_exists()
        cd2sql.create_table_if_not_exists()
        res2sql.create_table_if_not_exists()
        odds2sql.create_table_if_not_exists()
        logger.debug('Completed creating table.')

    for date in dr.daterange(st_date, ed_date):
        try:
            logger.debug(f'target date: {date}')
            jd2sql.insert2table(date)
            # jd2sqlで開催場と最終レース番を取得する
            logger.debug('insert race data: race chokuzen result odds')
            jyo_cd_list = jd2sql.map_raceno_dict.keys()
            start_time = time.time()
            rd2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)
            cd2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)
            res2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)
            odds2sql.insert2table(date, jyo_cd_list, jd2sql.map_raceno_dict)

            elapsed_time = time.time() - start_time
            logger.debug(f'completed in {elapsed_time}sec')
            # for jyo_cd in jd2sql.map_raceno_dict.keys():
            #     ed_race_no = jd2sql.map_raceno_dict[jyo_cd]
            #     start_time = time.time()
            #     for race_no in range(1, ed_race_no + 1):
            #         logger.info(
            #             f'data with date: {date} '
            #             f'jyo_cd: {jyo_cd} race_no: {race_no}')
            #         try:
            #             time.sleep(args.wait)
            #             rd2sql.insert2table(date, jyo_cd, race_no)
            #             cd2sql.insert2table(date, jyo_cd, race_no)
            #             res2sql.insert2table(date, jyo_cd, race_no)
            #             odds2sql.insert2table(date, jyo_cd, race_no)
            #         except Exception as e:
            #             logger.error(f'{e}')
            #     elapsed_time = time.time() - start_time
            #     logger.debug(f'completed in {elapsed_time}sec')
            logger.debug('insert race data completed.')
        except Exception as e:
            logger.error(f'{e}')

    logger.info('Down Server.')
    sql_ctl.clean()

    logger.info('All completed.')


if __name__ == '__main__':
    # logging設定
    # mainのlog設定
    coloredlogs.CAN_USE_BOLD_FONT = True
    coloredlogs.DEFAULT_FIELD_STYLES = CL_FIELD_STYLES
    coloredlogs.DEFAULT_LEVEL_STYLES = CL_LEVEL_STYLES
    coloredlogs.install(
        level='DEBUG',
        logger=getLogger(__name__),
        fmt=FMT,
        datefmt=DATE_FMT)

    # モジュール側の設定(INFOのみ)
    handler = StreamHandler()
    fmt = Formatter(
        fmt=FMT,
        datefmt=DATE_FMT
    )
    handler.setFormatter(fmt)
    getLogger(MODULE_LOG_NAME).addHandler(handler)
    getLogger(MODULE_LOG_NAME).setLevel(WARNING)

    main()
