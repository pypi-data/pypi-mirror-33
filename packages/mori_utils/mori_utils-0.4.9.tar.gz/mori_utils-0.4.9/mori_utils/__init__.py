# -*- coding: utf-8 -*-
#
# @Time    : 2018/4/24 上午11:14
# @Author  : Mori
# @Email   : moridisa@moridisa.cn
# @File    : __init__.py.py

import os

FILE_ROOT = os.getcwd()
LOG_PATH = os.path.join(FILE_ROOT, 'log')
CACHE_PATH = os.path.join(FILE_ROOT, 'caches')
CONFIG_PATH = os.path.join(FILE_ROOT, 'config')

__version__ = (0, 4, 2)
__author__ = "Mori <moridisa@moridisa.cn>"
__status__ = "snapshot"
__date__ = '2018/4/24'
__all__ = []

from .data_operator import *
from .net_works import *
from .utils import *
from .wrapper import *

try:
    __PATHS__ = [LOG_PATH, CACHE_PATH, CONFIG_PATH]
    [os.mkdir(path) for path in __PATHS__ if not os.path.exists(path)]
    load_config(os.path.join(FILE_ROOT, 'config'))
    logger = gen_logger(f'{__package__}')
    logger.info('mori_utils standby')
except Exception as e:
    print(e)
    print('Mori Utils Load Failed')

__all__ += ['FILE_ROOT', 'LOG_PATH', 'CACHE_PATH', 'CONFIG_PATH']
__all__ += data_operator.__all__
__all__ += net_works.__all__
__all__ += wrapper.__all__
__all__ += utils.__all__
