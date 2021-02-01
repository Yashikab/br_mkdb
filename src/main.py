# python 3.7.5
# coding: utf-8
"""
MYSQLへ公式データを格納する
"""
import argparse
from logging import INFO, Formatter, StreamHandler, getLogger

import coloredlogs

from application.argument import Options
from application.usecase import BoatRaceUsecase
from domain.const import (CL_FIELD_STYLES, CL_LEVEL_STYLES, DATE_FMT, FMT,
                          MAIN_LOGNAME, MODULE_LOG_NAME)
from module.log import TqdmLoggingHandler

if __name__ == '__main__':
    # logging設定
    # mainのlog設定
    main_logger = getLogger(MAIN_LOGNAME)
    main_logger.addHandler(TqdmLoggingHandler())
    coloredlogs.CAN_USE_BOLD_FONT = True
    coloredlogs.DEFAULT_FIELD_STYLES = CL_FIELD_STYLES
    coloredlogs.DEFAULT_LEVEL_STYLES = CL_LEVEL_STYLES
    coloredlogs.install(
        level='DEBUG',
        logger=main_logger,
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
    getLogger(MODULE_LOG_NAME).setLevel(INFO)

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
    if args.gcs:
        db = "gcs"
    else:
        db = "local"

    op = Options(
        start_date=args.st_date,
        end_date=args.ed_date,
        wait_time=args.wait,
        create_table=args.table,
        db_type=db
    )
    main_logger.debug(f"options: {op}")
    main_logger.info(f'Insert data between {op.start_date} and {op.end_date}')

    if op.db_type == "gcs":
        main_logger.info('use Google Cloud SQL.')
        usecase = BoatRaceUsecase.gcpmysql()
    elif op.db_type == "local":
        main_logger.info('use local mysql server.')
        usecase = BoatRaceUsecase.localmysql()
    else:
        raise Exception("Couldn't build sql controller")

    usecase.run(op)
