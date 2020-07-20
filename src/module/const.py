# python 3.7.5
# coding: utf-8
import os


MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
    'charset': 'utf8'
}

PROJECT_ID = os.getenv('PROJECT_ID')
