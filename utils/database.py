#!/usr/bin/python
# -*- coding=utf-8 -*-
import config
from sqlalchemy import create_engine
from redis import StrictRedis

username = config.get("mysql", "username")
password = config.get("mysql", "password")
host = config.get("mysql", "host")
port = config.get("mysql", "port")
database = config.get("mysql", "database")
engine = create_engine('mysql+pymysql://%s:%s@%s:%s/%s?charset=utf8' %
                       (username, password, host, port, database),
                       encoding='utf-8', echo=False, pool_size=50, max_overflow=0, pool_recycle=60)

redis_host = config.get('redis', 'host')
redis_port = config.get('redis', 'port')
redis_cli = StrictRedis(redis_host, redis_port)
