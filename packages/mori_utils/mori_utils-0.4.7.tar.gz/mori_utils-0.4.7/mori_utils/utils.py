# -*- coding: utf-8 -*-
#
# @Time    : 2018/4/24 上午11:14
# @Author  : Mori
# @Email   : moridisa@moridisa.cn
# @File    : __init__.py.py

import os
import sys
import yaml
import logging
from typing import Dict
from . import LOG_PATH

__GLOBAL_CONFIGS__ = dict()

__all__ = ['gen_logger', 'read_config', 'load_config']


def gen_logger(logger_name: str) -> logging.Logger:
    """
    generator a logger

    :param logger_name: logger name
    :return: logger
    """
    logger = logging.getLogger(logger_name)
    if len(logger.handlers) == 0:
        logger.propagate = False
        logging_format = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s', '%Y-%m-%d %H:%M:%S')

        file_log = logging.FileHandler(os.path.join(LOG_PATH, f'{logger_name}.log'))
        console_log = logging.StreamHandler(sys.stdout)

        file_log.setFormatter(logging_format)
        console_log.setFormatter(logging_format)

        logger.setLevel(logging.INFO)

        logger.addHandler(file_log)
        logger.addHandler(console_log)
    return logger


logger = gen_logger(__name__)


def load_config(root_path: str):
    """
    load all config files

    :param root_path: root path
    """

    for file in filter(lambda x: x.endswith('.yaml'), os.listdir(root_path)):
        logger.info('Read Config From %s, %s' % (root_path, file))
        config = yaml.load(open(os.path.join(root_path, file), 'r'))
        for k in config:
            sub_config = config[k]
            if sub_config.get('need_mysql_extract', None) is not None:
                logger.info(f"{k} need mysql extract")
                host = sub_config['host']
                host = host.replace('jdbc:mysql://', '')
                host, db = host.split('/')
                db = db.split('?')[0]
                host, port = host.split(':')
                sub_config.pop('host')
                sub_config['host'] = host
                sub_config['port'] = port
                sub_config['db'] = db
                config[k] = sub_config
        __GLOBAL_CONFIGS__.update(config)
        # logger.info(f"{__GLOBAL_CONFIGS__}")


def read_config(config_name: str) -> Dict[str, str]:
    """"
    read a config from yaml name

    :param config_name: config dict
    :return:
    """
    return __GLOBAL_CONFIGS__[config_name]
