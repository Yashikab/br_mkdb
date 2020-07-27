# python 3.7.5
# coding: utf-8
'''
google cloud sql proxyを通して, データを格納する
'''
import argparse
import os
import subprocess


def use_cloud_sql():
    "cloud sqlを使う場合"
    pass


def use_local_sql():
    "localを使う場合"
    pwd = os.path.abspath(__file__)
    this_filename = os.path.basename(__file__)
    this_dir = pwd.replace(this_filename, '')
    root_dir_for_sql = 'br_mkdb/src/'
    sql_dir = \
        this_dir.replace(root_dir_for_sql, 'mysql_local/boat/')

    os.chdir(sql_dir)
    try:
        # 先に前のゾンビ達は処理しておく，なければエラー履くのでスキップ
        subprocess.run(["docker-compose", "down"])
        subprocess.run(["docker", "volume", "rm", "boat_mysql"])
    except Exception:
        pass

    subprocess.run(["docker-compose", "up", "-d"])


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
        print('use google cloud sql.')
        use_cloud_sql()
    else:
        print('use default')
        use_local_sql()


if __name__ == '__main__':
    main()
