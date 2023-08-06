# -*- coding: utf-8 -*-
#
# @Time    : 2018/4/27 下午4:25
# @Author  : Mori
# @Email   : moridisa@moridisa.cn
# @File    : data_operator.py
# @Software: PyCharm
# @Desc    : data operator

import odps
import pymysql
import pymongo
from pymysql.connections import Cursor as MysqlCursor
from pymongo.collection import Collection as MongoCollection
from typing import List
from .utils import read_config

__all__ = [
    'MysqlCursor',
    'MongoCollection',
    'execute_mysql',
    'query_mysql',
    'query_mongo',
    'query_odps',
    'get_mysql_db_name',
    'get_zookeeper_host',
    'conn_mysql',
    'conn_mongo'
]


def __get_odps_connection__(config_name: str) -> odps.ODPS:
    """
    make odps connection instance

    :param config_name: config name
    :return: odps connection_instance
    """
    config = read_config(config_name)
    return odps.ODPS(config['access_key_id'], config['access_key_secret'], config['project_name'], config['end_point'])


def __get_mysql_connection__(config_name: str) -> pymysql.Connection:
    """
    load mysql config & make a mysql connection

    :param config_name: config name in yaml
    """

    return pymysql.connect(**read_config(config_name))


def __get_mongo_connection__(config_name: str) -> pymongo.MongoClient:
    """
    connection to mongo

    :param config_name: config name in yaml
    :return: mongo client
    """
    config = read_config(config_name)
    client = pymongo.MongoClient('mongodb://' + config['host'])
    client[config['auth']].authenticate(config['username'], config['password'])

    return client


def get_zookeeper_host(config_name: str) -> str:
    """
    get zookeeper host

    :param config_name: config name in yaml
    :return: zookeeper host
    """
    return read_config(config_name)['keeper_list'].split(',')[0]


def get_mysql_db_name(config_name: str) -> str:
    """
    get mysql db name in config

    :param config_name: config name in yaml
    :return: 'db' in yaml
    """
    return read_config(config_name)['db']


def query_mysql(config_name: str, sql: str, use_dict: bool = False) -> List:
    """
    query on mysql

    :param config_name: config name in yaml
    :param sql: sql
    :param use_dict: use dict data
    :return: query result
    """
    conn = __get_mysql_connection__(config_name)
    with conn:
        if use_dict:
            cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        else:
            cursor = conn.cursor()
        with cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
    return result


def query_odps(config_name: str, sql: str, use_dict: bool = False) -> List:
    """
    query on odps

    :param config_name: config name in yaml
    :param sql: sql
    :param use_dict: use dict data
    :return: query result
    """
    instance = __get_odps_connection__(config_name)
    result = []
    with instance.execute_sql(sql).open_reader(use_tunnel=True, limit_enabled=False) as reader:
        if use_dict:
            for record in reader:
                result.append(dict(record))
        else:
            for record in reader:
                result.append(record.values)
    return result


def query_mongo(config_name: str, condition: dict, collection_name: str = None) -> List:
    """
    query on mongo

    :param config_name: config name in yaml
    :param condition: query condition
    :param collection_name: collection name in mongo
    :return: query result
    """
    config = read_config(config_name)
    result = []
    with __get_mongo_connection__(config_name) as mongo_client:
        db = mongo_client.get_database(config['db'])
        collection = db.get_collection(
            collection_name if collection_name is not None else config['collection'])
        cursor = collection.find(condition)
        for record in cursor:
            result.append(record)
        cursor.close()
    return result


def execute_mysql(config_name: str, sql: str) -> int:
    """
    :param config_name: config name in yaml
    :param sql: sql
    :return: return id if sql.startwith('insert') else effect_row
    """
    conn = __get_mysql_connection__(config_name)
    with conn:
        cursor = conn.cursor()
        with cursor:
            effect_row = cursor.execute(sql)
            if sql.lower().startswith('insert'):
                effect_row = cursor.lastrowid
        conn.commit()
    return effect_row


conn_mysql = __get_mysql_connection__
conn_mongo = __get_mongo_connection__
