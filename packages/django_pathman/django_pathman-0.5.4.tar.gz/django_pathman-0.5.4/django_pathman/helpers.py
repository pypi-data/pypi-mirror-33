# coding: utf-8
import os

SQL_DIRNAME = 'sql'
SQL_DIRPATH = os.path.join(os.path.dirname(__file__), SQL_DIRNAME)


def read_sql(filename):
    sql_file_path = os.path.join(SQL_DIRPATH, filename)
    with open(sql_file_path, 'r') as rf:
        return rf.read()
