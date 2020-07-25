# python 3.7.5
# coding: utf-8
'''
google cloud sql proxyを通して, データを格納する
'''
import argparse


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
        print('use gcs.')
    else:
        print('use default')


if __name__ == '__main__':
    main()
