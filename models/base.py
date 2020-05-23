#! /usr/bin/env python
# -*- coding: utf-8 -*-

from peewee import Model
from playhouse.db_url import connect

from utils import config

username = config.get("mysql", "username")
password = config.get("mysql", "password")
host = config.get("mysql", "host")
port = config.get("mysql", "port")
database = config.get("mysql", "database")

db = connect('mysql://{username}:{password}@{host}:{port}/{database}'.
             format(username=username, password=password, host=host, port=port, database=database))


class BaseModel(Model):
    class Meta:
        database = db
