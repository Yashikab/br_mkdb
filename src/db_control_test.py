# python 3.7.5
# coding: utf-8
'''
google cloud sql proxyを通して, データを格納する
'''
import argparse
from logging import getLogger, DEBUG, basicConfig
from module.dbcontroller import LocalSqlController


# logger
logger = getLogger("DbCtl")
logger.setLevel(DEBUG)


def main():
    msg = \
        "MySQL DB to start.\n" \
        "default : local \n" \
        "if use gcs: add opt \"--gcs\""
    parser = argparse.ArgumentParser(
        description=msg
    )
    parser.add_argument(
        '--gcs',
        action='store_true',
        help='if you want to use gcs as MySQL db.'
    )
    args = parser.parse_args()

    if args.gcs:
        logger.info('use google cloud sql.')

    else:
        logger.info('use default')
        local_sql_ctl = LocalSqlController()
        local_sql_ctl.build()


if __name__ == '__main__':
    # このスクリプトから呼び出されるモジュール全体のログ設定を行う
    basicConfig(
        format='[%(asctime)s] %(name)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    main()
