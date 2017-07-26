# -*- coding: utf-8 -*-

"""
Author: Ted
Date: 2017-07-13

Des:
    generate pipelines / resources / parameters / Trucks / Uld

"""

from sqlalchemy import create_engine
from os.path import realpath, join, split
from datetime import datetime


class RemoteMySQLConfig:
    HOST = "10.0.149.36"
    USER = "developer"
    PASS = "developer"
    DB = "hangzhouhubqa"
    CHARSET = 'utf8'

    engine = create_engine(
        f'mysql+pymysql://{USER}:{PASS}@{HOST}/{DB}?charset={CHARSET}',
        isolation_level="READ UNCOMMITTED", )


class SaveConfig:

    DATA_DIR = join( split(split(realpath(__file__))[0])[0], 'data')
    OUT_DIR = join( split(split(realpath(__file__))[0])[0], 'out')


class TimeConfig:
    ZERO_TIMESTAMP = datetime(2017, 6, 15, 21)


if __name__ == "__main__":
    print(SaveConfig.DATA_DIR)
    print(SaveConfig.OUT_DIR)