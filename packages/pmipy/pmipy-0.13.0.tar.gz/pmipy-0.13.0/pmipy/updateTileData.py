# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 16:03:02 2018

@author: Administrator
"""

import os
from pmipy import log
from pmipy import pmi
from tqdm import tqdm
import pandas as pd
#from pmipy.support import prov_mapp
from pmipy import getPeopleFlow as gpf


logger = log.createLogger(__name__)

MongoDB = 'Claudius'
collection = 'TileData'
testDB = 'ClaudiusTest'

client16 = pmi.connOcm16()

coll = client16[testDB][collection]
# 创建grid
def createNewClaudius(meter):
    collOld = client16[MongoDB][collection]
    collNew = coll
    cursor = collOld.find({'meters': meter, 'processTime':'201711'},{'tileName': 1,'province':1, 
                       'city': 1, 'region': 1, 'polygon': 1, 'meters': 1, '_id': 0}, no_cursor_timeout=True)
    for document in cursor:
        collNew.insert_one(document)

# 更新宜出行文档
@pmi.execInfo()
def updateYCX(cityList=['厦门市', '莆田市'], dbName='ycx', ycxTable='ycx_scale', meter=1000):
    # 按城市更新--思路：先获取已有宜出行数据的城市名单
    cm = pmi.ConnMysql(dbName)
    city_name = 'city_name'
    logger.info('准备从{}数据库的{}数据表中获取宜出行数据...'.format(dbName, ycxTable))
    sql_info = "select distinct {}, time from `{}`".format(city_name, ycxTable)
    df_info = pd.read_sql(sql_info, cm.engine).set_index(city_name)
    if not len(cityList):
        cityList = list(df_info.index.drop_duplicates())
    logger.info('准备处理如下城市的宜出行数据：\n{}'.format(cityList))
    def getCityYCX(city):
        sql = "SELECT  count / max_data as count, lng, lat FROM `{}` where {}='{}'".format(ycxTable, city_name, city)
        df_city = pd.read_sql(sql, cm.engine)
        return df_city
    
    def getCityPoint(city):
        cursor = coll.find({'meters': meter,'city':city},{'tileName': 1, 'polygon': 1, '_id': 0}, no_cursor_timeout=True)
        _list = []
        for document in cursor:
            ploygon = eval(document['polygon'])
            document['lng1'] = ploygon[0][0]
            document['lng2'] = ploygon[3][0]
            document['lat1'] = ploygon[0][1]
            document['lat2'] = ploygon[2][1]
            _list.append(document)
        return pd.DataFrame(_list)

    for city in cityList:
        logger.info('准备更新{}的数据...'.format(city))
        ycxCityFileName = '_{}_{}人流指数.xlsx'.format(meter,city)
        timeList = list(df_info.loc[city]['time'])
        df_city = getCityYCX(city)
        logger.info('获取/处理宜出行数据...')
        if os.path.exists('./'+ycxCityFileName):
            logger.info('{}宜出行数据已在本地存储，跳过处理阶段！'.format(city))
            df_ycx = pd.read_excel(ycxCityFileName)
        else:
            df_point = getCityPoint(city)
            df_ycx = gpf.getPeopleFlow(df_point, df_city, ycxStoreType='df', city=city, grid=True, 
                                       lnglat=('lng1','lng2','lat1','lat2'), meter=meter)
        # 更新城市宜出行...
        logger.info('更新/插入宜出行移动人口指数...')
        for index in tqdm(df_ycx.index):
            tn = df_ycx.loc[index]['tileName']
            ycx = df_ycx.loc[index]['人流指数']
            coll.update_one({'tileName': tn}, {'$set': {'ycx': {'moveIndex': ycx,'time': str(timeList)}}})
        logger.info('完成{}的宜出行数据更新！\n'.format(city))


if __name__== '__main__':
    updateYCX()
