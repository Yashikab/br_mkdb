# python 3.7.5
# coding: utf-8
import os

# hostname取得
if os.uname()[1] == 'yashi-E203NA':
    __hostname = os.getenv('MYSQL_HOST_E203')
else:
    __hostname = os.getenv('MYSQL_HOST')

MYSQL_CONFIG = {
    'host': __hostname,
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8'
}
