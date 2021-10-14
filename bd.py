# Базовые методы работы с mysql

import mysql.connector as mysql
import env


def get_connection():
    connect = mysql.connect(
        host=env.MYSQL_HOST,
        user=env.MYSQL_USER,
        passwd=env.MYSQL_PASSWORD,
        database=env.MYSQL_DATABASE,
        port=env.MYSQL_PORT
    )

    return connect
