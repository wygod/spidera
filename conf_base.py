#-*- encoding:utf-8 -*-
import os
import logging
from logging import config
from configparser import ConfigParser


def read_config(path):
    '''
    读取配置文件
    :param path: 配置文件路径
    :return: 配置文件对象
    '''
    spider_wechat_config = ConfigParser()
    spider_wechat_config.read(path)
    return spider_wechat_config


def log_config(conf_arg):
    '''
    此函数用于链接日志文件
    :param conf_arg:
    :return:
    '''
    path = conf_arg.get("logHandler", "log_conf_path")
    if os.path.exists(path):
        with open(path,"r",encoding = 'utf-8') as f:
            logging.config.fileConfig(f)

    rotating_logger = logging.getLogger(name="rotatingFileLogger")
    return rotating_logger