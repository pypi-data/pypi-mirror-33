# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 22:04:45 2018

@author: jasonai
"""

import sys
import math
from pmipy import pmi
from pmipy import log
import numpy as np
import pandas as pd
from tqdm import tqdm
import multiprocessing as mp


logger = log.createLogger(__name__)

def haversine(lng1, lat1, lng2, lat2): # 根据经纬度计算两点距离  
    lng1, lat1, lng2, lat2 = map(math.radians, [lng1, lat1, lng2, lat2])  
    dlng = lng2 - lng1   
    dlat = lat2 - lat1   
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2 
    c = 2 * math.asin(math.sqrt(a))   
    r = 6371 # 地球平均半径，单位为公里  
    d = c * r * 1000
    return d


# 从mysql中取数
def ycxFromMysql(dbName, tableName, city):
    cm = pmi.ConnMysql(dbName)
    sql = """
    SELECT count / max_data as count, lng, lat, time FROM `{}`
    where city_name = '{}'""".format(tableName, city)
    df = pd.read_sql(sql, cm.engine)
    logger.info('成功从{}数据库的{}数据表中读取{}的宜出行数据！'.format(dbName, tableName, city))
    return df

# 此函数速度太慢，放弃使用
# 需输入点位经纬度数据，宜出行数据，其中宜出行的数据表头格式是标准格式
# df_ycx['distance'] = df_ycx.apply(lambda row: haversine(lng1, lat1,row['lng'], row['lat']), axis=1)此代码更耗时
def yichuxing_backup1(df_point, df_ycx, lnglat, meter=500):
    PF = []
    for lng1, lat1 in tqdm(df_point.loc[:, [lnglat]].values):
        peo_flow = 0 # 人流指数
        for lng2, lat2, count in df_ycx.loc[:,['lng', 'lat', 'count']].values:
            if haversine(lng1, lat1, lng2, lat2) <= meter:
                peo_flow += count
        PF.append(peo_flow)
        
    df_point['人流指数'] = PF
    return df_point

def run_task(df,df_ycx, lnglat, meter):
    PF = []
    for lng1, lat1 in tqdm(df.loc[:, lnglat].values):
        peo_flow = 0 # 人流指数
        for lng2, lat2, count in df_ycx.loc[:,['lng', 'lat', 'count']].values:
            #print(peo_flow)

            if haversine(lng1, lat1, lng2, lat2) <= meter:
                peo_flow += count
        PF.append(peo_flow)
    df['人流指数'] = PF
    return df
    #print('Task {0} end.'.format(name))


# 计算网格人流指数
def run_task2(df, df_ycx, lnglat):
    PF = []
    for lng1, lng2, lat1, lat2 in tqdm(df[lnglat].values):
        peo_flow = 0 # 人流指数
        # print(1)
        for lng, lat, count in df_ycx.loc[:,['lng', 'lat', 'count']].values:
            if (lng1<lng<lng2) & (lat1<lat<lat2) : # 判断点落在网格内
                peo_flow += count
        PF.append(peo_flow)
    df['人流指数'] = PF
    return df
    #print('Task {0} end.'.format(name))


# 读取店铺点数文件
def getPointData(pointFile):
    if pointFile[-4:] == '.csv':
        df_point = pd.read_csv(pointFile, engine='python')
    elif pointFile[-5:] == '.xlsx':
        df_point = pd.read_excel(pointFile)
    else:
        sys.exit('Please input csv or xlsx file!')
    return df_point


# @pmi.execInfo()
def getPeopleFlow(pointFile, ycxTable, dbName='ycx', ycxStoreType='mysql', city='上海市', grid=False, lnglat=('经度','纬度'), 
                  meter='500', core_num='max', outputFile=''):
    
    # 读取店铺点数文件
    if type(pointFile) == str:
        df_point = getPointData(pointFile)
    elif type(pointFile) == pd.DataFrame:
        df_point = pointFile
        pointFile = ''
    else:
        logger.info('请输入存放点位经纬度信息文件的文件路径或DataFrame！')
    # 读取宜出行数据文件，获取人流
    if ycxStoreType == 'localfile':
        if ycxTable[-4:] == '.csv':
            df_ycx = pd.read_csv(ycxTable, engine='python')
        elif ycxTable[-5:] == '.xlsx':
            df_ycx = pd.read_excel(ycxTable)
        else:
            logger.warning('Please input csv or xlsx file!')
    elif ycxStoreType == 'mysql':
        try:
            df_ycx = ycxFromMysql(dbName, ycxTable, city)
        except Exception as e:
            logger.warning(e)
            raise SystemExit
    elif ycxStoreType == 'df':
        df_ycx = ycxTable
    else: 
        logger.info('目前尚不能支持{}数据类型，请检查yst输入是否正确！'%ycxStoreType)
    # 输出文件名
    if not outputFile:
        outFile = pointFile + '_{}_{}人流指数'.format(meter,city)
        outFile = outFile.replace('.csv', '')
        outFile = outFile.replace('.xlsx', '')
    # 获取经纬度表头列表
    lnglat = list(lnglat)
    meter = int(meter)
    # 确定并发使用的CPU线程数
    core_max = mp.cpu_count()
    if core_num != 'max':
        try:
            ncore = int(core_num)
            core_num = ncore if ncore <= core_max else core_max
        except ValueError:
            sys.exit('请输入正确的线程数(整数值)！')
    else:
        core_num = core_max
    df_split = np.array_split(df_point, core_num)
    p = mp.Pool(processes=core_num)
    funcList = []
    if grid:
        for df in df_split:
            f = p.apply_async(run_task2, args=(df, df_ycx, lnglat,))
            funcList.append(f)
    else:
        for df in df_split:
            f = p.apply_async(run_task, args=(df, df_ycx, lnglat, meter,))
            funcList.append(f)
    logger.info('Waiting for all subprocesses done...')
    p.close()
    p.join()
    resList = []
    for f in funcList:
        resList.append(f.get(timeout=0.5))
    df_all = pd.concat(resList)
    # 添加时间信息
    # df_all['爬取时间'] = ycxTable.split('.')[0][-19:-3] # '南京2018-04-05-11-16-34.csv'格式
    logger.info('完成人流指数的计算！')
    df_all.to_excel(outFile+'.xlsx', index=False)
    return df_all


if __name__ == '__main__':
    pointFile = '江苏省linxdata_经纬度匹配最终版V1.xlsx'
    ycxTable = '南京2018-04-01-17-40-57.csv'
    getPeopleFlow(pointFile, ycxTable, lnglat, 500, 12, 'ts')

    
    