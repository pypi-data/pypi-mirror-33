"""
Created on Sat Apr 21 07:29:46 2018

@author: jasonai
"""

import os
import codecs
import platform
import configparser
import pandas as pd
from pmipy import log
from datetime import datetime
from pymongo import MongoClient
from sqlalchemy import create_engine

"""
函数功能介绍：
checkResult：用于检查网络响应型输出结果，如网络无响应则会循环访问，直至达到指定循环次数
readXlsCsv：输入指定excel文件路径(filePath)，最终可返回一个包含data、path、fileName、file和fileSuffix的字典
"""
_logger = log.createCustomLogger('root') # 单下划线变量防止import * 时导入

def execInfo(arg = True):
    if arg:
        def _deco(func):
            def wrapper(*arg, **kwargs):
                startTime = datetime.now()
                _logger.info("start %s..."%func.__name__)
                func(*arg, **kwargs)
                endTime = datetime.now()
                secs = endTime - startTime
                _logger.info("end {0}--> elapsed time: {1}".format(func.__name__, secs))
            return wrapper
    else:
        def _deco(func):
            return func
    return _deco


def checkResult(keyword, loopTime):
    def _deco(func):
        def wrapper(*arg, **kwargs):
            res2 = keyword
            time = 1
            while res2 == keyword and time <= loopTime:
                res = func(*arg, **kwargs)
                # 目前只考虑函数返回结果为list、字符串和数字这三种类型
                res2 = res[0] if type(res)==list else res 
                time += 1
            return res
        return wrapper
    return _deco


# 输入制定excel文件路径，最终可产出一个包含data、path、fileName、file和fileSuffix的字典
def readXlsCsv(filePath):
    result = {}
    [result['path'], file] = os.path.split(filePath)
    [result['fileName'], fileSuffix] = os.path.splitext(file)
    if fileSuffix == '.xlsx' or fileSuffix == '.xls':
        df = pd.read_excel(filePath)
    elif fileSuffix == '.csv':
        try:
            df = pd.read_csv(filePath, engine='python')
        except pd.errors.ParserError: # csv为tab键分割的情况
            df = pd.read_csv(filePath, sep='\t', engine='python')
    else:
        _logger.error("Please input csv or xlsx file!")
        raise SystemExit
    result['file'] = file
    result['fileSuffix'] = fileSuffix
    result['data'] = df
    return result

# 连接OCM1.6
def connOcm16(LAN=True):
    IP_LAN = '192.168.0.21:27017'
    IP_PN = 'www.parramountain.com:47017'
    IP = IP_LAN if LAN else IP_PN
    uri = 'mongodb://laocheng:laocheng@{0}'.format(IP)
    client = MongoClient(uri)
    return client


# 连接OCM1.5
def connOcm15(LAN=True):
    IP_LAN = '192.168.0.11:27017'
    IP_PN = 'www.parramountain.com:37017'
    IP = IP_LAN if LAN else IP_PN   
    uri = 'mongodb://liushizhan:liushizhan@{0}'.format(IP)
    client = MongoClient(uri)
    return client



# 连接PMI的mysql数据库
class ConnMysql(object):
    def __init__(self, database):
        self.database = database
        # 测试网络是否在局域网
        df_test = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        try:
            _logger.info("使用局域网连接Mysql数据库 ...")
            self.setServer() # 首先尝试内网连接，保证传输速度
            df_test.to_sql('test', self.engine, if_exists="replace", index=False)
        except Exception as e:
            _logger.info("异常信息为:%s" %e)
            self.setServer(False)
            _logger.info("使用局域网连接失败！")
            _logger.info("使用公网连接Mysql数据库 ...")
            
    def __call__(self, tableName, df=''):
        """传入dataframe参数时，程序将执行导入数据表功能,否则默认从数据表中导入数据"""
        
        if len(df):
            try:
                df.to_sql(tableName, self.engine, if_exists="replace", index=False)
                _logger.info("DataFrame导入至{}数据表完成!".format(tableName))
            except ValueError as e:
                _logger.info(e)
        else:
            sql = 'select * from `%s`' % tableName
            df = pd.read_sql(sql, self.engine)
            return df
    
    def getMysql(self, tableName, field='', item=''):
        if field and item:
            sql = """select * from `{0}`
            where `{1}` = '{2}'""".format(tableName, field, item)
            df = pd.read_sql(sql, self.engine)
            # 如果有"更新时间"字段，则程序暂时设置为去除此字段，此外还去除field字段内容
            df = df.drop([field, "更新时间"], axis=1)
            return df
        elif field or item:
            _logger.warining("请检查field或iten是否为空值！")
            raise SystemError
        else:
            df = self.__call__(tableName)
    
    def toMysql(self, tableName, df, updateTime='', exMethod='append'):
        if updateTime:
            df[updateTime] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df[updateTime] = df[updateTime].astype('datetime64[ns]')
            try:
                df.to_sql(tableName, self.engine, if_exists=exMethod, index=False)
            except ValueError as e:
                _logger.warining(e)

        else:
            df = self.__call__(tableName, df)

    def setServer(self, LAN=True):
        IP_LAN = '192.168.0.50'
        IP_PN = 'www.parramountain.com'
        if LAN:
            IP = IP_LAN
            Port = 3306
        else:
            IP = IP_PN
            Port = 4306
        # to_sql引擎设置
        self.engine = create_engine('mysql+mysqldb://root:pmimysql@{}:{}/{}?charset=utf8'.format(IP, Port, self.database))


# 连接PMI的sql数据库
class ConnMssql(object):
    def __init__(self, database):
        self.database = database
        # 测试网络是否在局域网
        df_test = pd.DataFrame(['test'])
        try:
            _logger.info("使用局域网连接Mssql数据库 ...")
            self.setServer() # 首先尝试内网连接，保证传输速度
            df_test.to_sql('test', self.engine, if_exists="replace", index=False)
        except Exception as e:
            _logger.info("异常信息为:%s" %e)
            self.setServer(False)
            _logger.info("使用局域网连接失败！")
            _logger.info("使用公网连接Mysql数据库 ...")

    def __call__(self, tableName, df=''):
        """传入dataframe参数时，程序将执行导入数据表功能,否则默认从数据表中导入数据"""
        
        if len(df):
            df.to_sql(tableName, self.engine, if_exists="replace", index=False)
            _logger.info("DataFrame导入至{}数据表完成!".format(tableName))
        else:
            sql = 'select * from %s' % tableName
            df = pd.read_sql(sql, self.engine)
            return df

    def setServer(self, LAN=True):
        IP_LAN = '192.168.0.50'
        IP_PN = 'www.parramountain.com'
        if LAN:
            IP = IP_LAN
            Port = 1433
        else:
            IP = IP_PN
            Port = 2433
        # to_sql引擎设置
        self.engine = create_engine('mssql+pymssql://sa:pmisql@{}:{}/{}'.format(IP, Port, self.database))


class ConfigHandler(object):
    """docstring for ConfigHandler"""
    '''
    ini example:

    [DEFAULT]
    ip = 192.168.1.3
    dbname = Test

    [WEIBO]
    collection = Weibo
    tactic = 1
    input = /path/file
    output = /path/file
    '''
    def __init__(self, soure_file):
        # super(ConfigHandler, self).__init__()
        self._config = configparser.RawConfigParser()
        self._soure_file = os.path.dirname(os.path.abspath(soure_file))
        #self._default_ini_file = default_ini_file
        #self._crawler_ini_file = crawler_ini_file
        _logger.info('ConfigHandler initialized')
        _logger.info(self._soure_file)

    def read_configure(self, ini_file, section):
        '''
        args: section, like 'WEIBO'
        return dict, like congfig[section]
        use example
        if ini section look like as
            [WEIBO]
            collection = Weibo
            tactic = 1
            input = /path
            output
        it will read all value of [section] and [DEFAULT] of ini file
        '''
        if platform.system() == 'Windows':
            self._config.readfp(codecs.open(self._soure_file+'\\'+ini_file, 'r')) #, 'utf8'))
        elif platform.system() == 'Linux' or platform.system() == 'Darwin': #Linux or Mac
            self._config.readfp(codecs.open(self._soure_file+'/'+ini_file, 'r', 'utf8'))
        return self._config[section]
    


