# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

__author__ = 'JacksonSun'
__date__ = '2018/07/05'


setup(
    name='UtilsCell',                                # 名称
    version='0.0.1',                                 # 版本号
    description='my UtilsCell',                          # 简单描述
    long_description=long_description,               # 详细描述
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    keywords='Utils email ten ssh',                 # 关键字
    author='JacksonSun',                               # 作者
    author_email='306862600@qq.com',                # 邮箱
    url='https://github.com/SunJackson/myutils',      # 包含包的项目地址
    license='MIT',                                  # 授权方式
    packages=find_packages(),                       # 包列表
    install_requires=[],
    include_package_data=True,
    zip_safe=True,
)