# -*- coding: utf-8 -*-
#
# @Time    : 2018/4/24 上午11:14
# @Author  : Mori
# @Email   : moridisa@moridisa.cn
# @File    : __init__.py.py

import os
import time
import pickle
import logging
import hashlib
from typing import List
from . import CACHE_PATH, read_config
from .data_operator import __get_mysql_connection__, __get_mongo_connection__
from functools import wraps

logger = logging.getLogger('mori_utils')

__all__ = ['m_wrap']


def m_wrap(log: bool = True,
           cache: bool = True,
           cache_expire: float = None,
           *cache_args):
    def wrapper(func):
        @wraps(func)
        def __inner_wrapper__(*args, **kwargs):
            if log:
                logger.info(f'{func.__module__}.{func.__name__} - Start')

            if cache:
                cache_file_name = os.path.join(CACHE_PATH, f'{func.__module__}.{func.__name__}')

                # check args & kwargs
                if len(cache_args) > 0:
                    been_cache_args = [args[i] for i in cache_args if isinstance(i, int)]
                    been_cache_kwargs = [kwargs[i] for i in cache_args if isinstance(i, str)]
                    md5 = hashlib.md5()
                    md5.update(f'{been_cache_args}-{been_cache_kwargs}'.encode('utf8'))
                    cache_file_name = f'{cache_file_name}.{md5.hexdigest()[8:-8]}'
                # update cache file name
                cache_file_name = f'{cache_file_name}.cache'

                # check cache file exists
                if os.path.exists(cache_file_name):

                    # cache still work
                    if cache_expire is None or \
                            time.time() - os.path.getmtime(cache_file_name) < cache_expire * 24 * 60 * 60:
                        data = pickle.load(open(cache_file_name, 'rb'))

                    # new cache
                    else:
                        data = func(*args, **kwargs)
                        pickle.dump(data, open(cache_file_name, 'wb'))
                else:
                    data = func(*args, **kwargs)
                    pickle.dump(data, open(cache_file_name, 'wb'))

            else:
                data = func(*args, **kwargs)

            if log:
                logger.info(f'{func.__module__}.{func.__name__} - Finish')
            return data

        return __inner_wrapper__

    return wrapper
