# python 3.7.5
# coding: utf-8
import os


if os.getenv('MYSQL_ENV') == "TEST":
    MYSQL_CONFIG = {
        'host': "testmysql",
        'user': "test_boat_user",
        'password': "test_pw",
        'database': "test_boat_db",
        'charset': "utf8"
    }
elif os.getenv('MYSQL_ENV') == "LOCALTEST":
    MYSQL_CONFIG = {
        'host': "127.0.0.1",
        'user': "test_boat_user",
        'password': "test_pw",
        'database': "test_boat_db",
        'charset': "utf8"
    }
else:
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST'),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
        'database': os.getenv('MYSQL_DATABASE'),
        'charset': 'utf8'
    }

# logに関するconst
MAIN_LOGNAME = "main"
MODULE_LOG_NAME = 'module'
FMT = '[%(asctime)s] %(name)s %(levelname)s: %(message)s'
DATE_FMT = '%Y-%m-%d %H:%M:%S'

CL_FIELD_STYLES = \
    {'asctime': {'color': 'green'},
        'hostname': {'color': 'green'},
        'levelname': {'color': 'green'},
        'name': {'color': 'green'},
        'programname': {'color': 'green'}}
CL_LEVEL_STYLES = \
    {'critical': {'color': 'red'},
        'error': {'color': 'red'},
        'warning': {'color': 'yellow'},
        'notice': {'color': 'magenta'},
        'info': {'color': 'green'},
        'debug': {},
        'spam': {'color': 'green', 'faint': True},
        'success': {'color': 'green'},
        'verbose': {'color': 'blue'}}
