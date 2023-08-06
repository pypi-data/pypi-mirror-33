"""
Created on Sat Apr 21 07:29:46 2018

@author: jasonai
"""

import logging


def createLogger(name):
    # 获取logger实例，如果参数为空则返回root logger
    logger = logging.getLogger(name)
    
    # 指定logger输出格式
    formatter = logging.Formatter('[%(asctime)s][%(module)s][line:%(lineno)d][%(levelname)s]: %(message)s')
    
    # 文件日志
    file_handler = logging.FileHandler(name + ".log")
    file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
    
    # 控制台日志
    console_handler = logging.StreamHandler() #sys.stdout)
    console_handler.formatter = formatter  # 也可以直接给formatter赋值
     
    # 为logger添加的日志处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
     
    # 指定日志的最低输出级别，默认为WARN级别
    logger.setLevel(logging.INFO)
    return logger


def createCustomLogger(name):
    formatter = logging.Formatter(fmt='[%(asctime)s][%(levelname)s][%(module)s] %(message)s', 
                                        datefmt='%m/%d %I:%M:%S%p')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    return logger


