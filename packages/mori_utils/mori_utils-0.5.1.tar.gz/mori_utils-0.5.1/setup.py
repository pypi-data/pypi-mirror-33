# -*- coding: utf-8 -*-
#
# @Time    : 2018/4/24 上午11:12
# @Author  : Mori
# @Email   : moridisa@moridisa.cn
# @File    : setup.py
# @Software: PyCharm
# @Desc    :

from setuptools import setup, find_packages

setup(
    name='mori_utils',
    version='0.5.1',
    description='Mori Personal Utils',
    author='moridisa',
    author_email='moridisa@moridisa.cn',
    url='https://github.com/moriW/mori_utils',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'pymongo',
        'pymysql',
        'pyodps',
        'kazoo',
        'pyyaml'
    ],
)
