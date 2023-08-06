# -*- coding: utf-8 -*-
"""
Created on Wed May  2 17:27:05 2018

@author: Administrator
"""
from pmipy import log
import pandas as pd
from sqlalchemy import create_engine

logger = log.createLogger(__name__)

class UploadMysql(object):
    def __init__(self, database, LAN=True):
        self.database = database
        self.engine = self.setServer(LAN)
        
    # 连接PMI的mysql数据库
    def setServer(self, LAN):
        # global engine
        IP_LAN = '192.168.0.50'
        IP_PN = 'www.parramountain.com'
        if LAN:
            IP = IP_LAN
            Port = 3306
        else:
            IP = IP_PN
            Port = 4306

        # to_sql引擎设置
        engine = create_engine('mysql+mysqldb://root:pmimysql@{}:{}/{}?charset=utf8'.format(IP, Port, self.database))
        logger.info("成功连接{}数据库!".format(self.database))
        
        return engine
    
    def dfToMysql(self, df, tableName):
        df.to_sql(tableName,  self.engine, if_exists='append', index=False)

