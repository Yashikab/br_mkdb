# python 3.7.5
# coding: utf-8
"""
MYSQLへ公式データを格納する
"""
import argparse
from datetime import datetime, timedelta
from logging import basicConfig, getLogger, DEBUG

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
logger.setLevel(DEBUG)


def main():
    # コマンドライン引数オプション
    parser = argparse.ArgumentParser(description='Insert data to MySQL.')
    parser.add_argument('st_date',
                        type=str,
                        help='start date with y-m-d')
    parser.add_argument('ed_date',
                        type=str,
                        help='end date with y-m-d')
    parser.add_argument('--table',
                        action='store_true',
                        help='if you want to create table.')
    # parser.add_argument('-t', '--table')

    args = parser.parse_args()
    st_date = datetime.strptime(args.st_date, '%Y-%m-%d')
    ed_date = datetime.strptime(args.ed_date, '%Y-%m-%d')
    logger.info(f'Insert table between {st_date} and {ed_date}')
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
        logger.debug(f'insert date at {date}')
        # TODO: ここからつづき


if __name__ == '__main__':
    # このスクリプトから呼び出されるモジュール全体のログ設定を行う
    basicConfig(
        format='[%(asctime)s] %(name)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main()
