# python 3.7.5
# coding: utf-8
"""
MYSQLへ公式データを格納する
"""
import argparse
from datetime import datetime
import coloredlogs
from logging import (
    getLogger,
    Formatter,
    StreamHandler,
    DEBUG,
    INFO
)
import time

from module.const import MODULE_LOG_NAME
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
        # NOTE: メソッド未実装なので接続できない
        sql_ctl = CloudSqlController()
    else:
        logger.debug('use local mysql server.')
        sql_ctl = LocalSqlController()
    sql_ctl.build()
    logger.info('Done')

    # 気持ち空けておく
    time.sleep(1)

    logger.info(f'Table Creating: {args.table}')
    logger.debug('load classes from dt2sql')
    jd2sql = JyoData2sql()
    rd2sql = RaceData2sql()
    cd2sql = ChokuzenData2sql()
    res2sql = ResultData2sql()
    odds2sql = Odds2sql()
    logger.debug('Completed loading classes.')

    if args.table:
        logger.debug('Create table if it does not exist.')
        jd2sql.create_table_if_not_exists()
        rd2sql.create_table_if_not_exists()
        cd2sql.create_table_if_not_exists()
        res2sql.create_table_if_not_exists()
        odds2sql.create_table_if_not_exists()
        logger.debug('Completed creating table.')

    for date in dr.daterange(st_date, ed_date):
        try:
            logger.debug(f'target date: {date}')
            logger.debug('insert jyodata')
            jd2sql.insert2table(date)
            logger.debug('done')

            # jd2sqlで開催場と最終レース番を取得する
            logger.debug('insert race data: race chokuzen result odds')
            for jyo_cd in jd2sql.dict_for_other_tb.keys():
                ed_race_no = jd2sql.dict_for_other_tb[jyo_cd]
                logger.debug(f'data with jyo_cd: {jyo_cd}')
                start_time = time.time()
                for race_no in range(1, ed_race_no + 1):
                    try:
                        time.sleep(args.wait)
                        rd2sql.insert2table(date, jyo_cd, race_no)
                        cd2sql.insert2table(date, jyo_cd, race_no)
                        res2sql.insert2table(date, jyo_cd, race_no)
                        odds2sql.insert2table(date, jyo_cd, race_no)
                    except Exception as e:
                        logger.error(f'{e}')
                elapsed_time = time.time() - start_time
                logger.debug(f'completed in {elapsed_time}sec')
            logger.debug('insert race data completed.')
        except Exception as e:
            logger.error(f'{e}')

    logger.info('Down Server.')
    sql_ctl.clean()

    logger.info('All completed.')


if __name__ == '__main__':
    # logging設定
    coloredlogs.DEFAULT_FIELD_STYLES = \
        {'asctime': {'color': 'green'},
         'hostname': {'color': 'magenta'},
         'levelname': {'color': 'black', 'bold': True},
         'name': {'color': 'blue'},
         'programname': {'color': 'cyan'}}
    coloredlogs.DEFAULT_LEVEL_STYLES = \
        {'critical': {'color': 'red', 'bold': True},
         'error': {'color': 'red'},
         'warning': {'color': 'yellow'},
         'notice': {'color': 'magenta'},
         'info': {},
         'debug': {'color': 'green'},
         'spam': {'color': 'green', 'faint': True},
         'success': {'color': 'green', 'bold': True},
         'verbose': {'color': 'blue'}}
    coloredlogs.install(
        level='INFO',
        logger=getLogger(__name__),
        fmt='[%(asctime)s] %(name)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    handler = StreamHandler()
    fmt = Formatter(
        fmt='[%(asctime)s] %(name)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(fmt)
    getLogger(__name__).addHandler(handler)
    getLogger(__name__).setLevel(DEBUG)
    # モジュール側の設定(INFOのみ)
    getLogger(MODULE_LOG_NAME).addHandler(handler)
    getLogger(MODULE_LOG_NAME).setLevel(INFO)

    main()
