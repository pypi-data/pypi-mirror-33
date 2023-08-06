# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 19:18:05 2018

@author: jasonai
"""

import os
import yaml
import pandas as pd
from pymongo import MongoClient

# 连接OCM1.6
def conn_ocm16(LAN=True):
    IP_LAN = '192.168.0.21:27017'
    IP_PN = 'www.parramountain.com:47017'
    IP = IP_LAN if LAN else IP_PN   
    uri = 'mongodb://laocheng:laocheng@{0}'.format(IP)
    client = MongoClient(uri)
    return client

# 连接OCM1.5
def conn_ocm15(LAN=True):
    IP_LAN = '192.168.0.11:27017'
    IP_PN = 'www.parramountain.com:37017'
    IP = IP_LAN if LAN else IP_PN   
    uri = 'mongodb://liushizhan:liushizhan@{0}'.format(IP)
    client = MongoClient(uri)
    return client


def waimai_update(client, province='湖北省'):
    prov_mapp = yaml.load(open('E:\CloudStation\OCM\省份名单对应表.yaml', encoding='utf-8'))
    def sql_content(region, region_state):
        # 外卖月销量
        sql = [{'$match':{'lv3Name':region_state}},
               {'$group': {'_id' : region, '销量':{'$sum':'$monthSaleCount'}}}]
        return sql
    # 将省名转为英文名
    prov = prov_mapp[province]
    # 美团
    db_meituan = client15['WaimaiMeituan_201711']
    sql_region = sql_content('$lv3Name', {'$ne':None})
    cursor1 = db_meituan[prov].aggregate(sql_region)
    # 提取直辖县，比如神农架林区
    sql_city = sql_content('$lv2Name', None)
    cursor2 = db_meituan[prov].aggregate(sql_city)
    df = pd.DataFrame(list(cursor1))
    df_meituan = df.append(pd.DataFrame(list(cursor2))).set_index('_id')
    # 饿了么
    db_eleme = client15['Eleme_201711']
    sql_region = sql_content('$lv3Name', {'$ne':None})
    cursor1 = db_eleme[prov].aggregate(sql_region)
    sql_city = sql_content('$lv2Name', None)
    cursor2 = db_eleme[prov].aggregate(sql_city)
    df = pd.DataFrame(list(cursor1))
    df_eleme = df.append(pd.DataFrame(list(cursor2))).set_index('_id')
    # 百度外卖
    db_baidu = client15['WaimaiBaidu_201711']
    sql_region = sql_content('$lv3Name', {'$ne':None})
    cursor1 = db_baidu[prov].aggregate(sql_region)
    sql_city = sql_content('$lv2Name', None)
    cursor2 = db_baidu[prov].aggregate(sql_city)
    df = pd.DataFrame(list(cursor1))
    df_baidu = df.append(pd.DataFrame(list(cursor2))).set_index('_id')
    # 合并三大外卖
    df_merge = pd.concat([df_meituan, df_eleme, df_baidu], join='outer', axis=1)
    df_merge.columns = ['美团外卖', '饿了么外卖', '百度外卖']
    df_merge['外卖'] = df_merge.sum(axis=1)
    return df_merge

def factor_update(df_label, client, province='湖北省'):
    collection = client['Claudius']['TileData']
    group_dict = {'_id' : ''}
    for index in df_label.index:
        group_dict[index] = {'$sum' : '${0}.{1}'.format(df_label.loc[index,'一级标签'], df_label.loc[index,'sub'])}
    
    def sql_content(region, region_state):
        group_dict['_id'] = region
        sql = [
            {'$match':{'province':province, 'region':region_state, 'processTime':'201711', 'meters':1000}},
            {'$group' : group_dict},
            ]
        return sql

    # 提取区县通路点数,首先排除region为空的直辖县
    sql_region = sql_content('$region', {'$ne':None})
    cursor1 = collection.aggregate(sql_region)
    # 提取直辖县，比如神农架林区
    sql_city = sql_content('$city', None)
    cursor2 = collection.aggregate(sql_city)

    df = pd.DataFrame(list(cursor1))
    df = df.append(pd.DataFrame(list(cursor2)))
    return df.set_index('_id')

def factor_map_busi(df_factor, df_mapp):
    # 各区县通路点数乘以分配系数，解决一区多商圈的问题
    df_factor2 = df_factor.merge(df_mapp[['具体描述', '区县分配系数']], left_index=True,right_index=True,how='right')
    # 将控制填0
    df_factor2.fillna(0, inplace=True)
    df_factor2[df_factor.columns] = df_factor2[df_factor.columns].apply(lambda x: x * df_factor2['区县分配系数'])
    # 计算各商圈的因子点数
    df_factor3 = df_factor2.groupby('具体描述').sum().drop('区县分配系数', axis=1)
    
    return df_factor3

if __name__ == '__main__':
    path = '.'
    province='湖北省'
    filename = '%s各地区正负因子.xlsx'  % province

    client15 = conn_ocm15() #False)
    client16 = conn_ocm16() #False)
    xlsx = pd.ExcelFile(os.path.join(path, filename))
    # 读取地理因子信息标签，用于OCM取数
    df_label = pd.read_excel(xlsx, '地理因子信息', index_col='因子')
    isWaimai = False
    # 暂时去除外卖
    if '外卖' in df_label.index:
        isWaimai = True
        df_waimai = waimai_update(client15, province)
        df_label.drop(['外卖'], inplace=True)
    df_factor = factor_update(df_label, client16, province)
    if isWaimai:
        df_factor = pd.concat([df_factor, df_waimai['外卖']], axis=1)
    
    df_factor.to_excel('%s各区县地理因子数据.xlsx' % province)
    df_mapp = pd.read_excel('%sKSF各商圈区县分配系数.xlsx' % province, index_col='区县')
    df_factor2 = factor_map_busi(df_factor, df_mapp)
    # 将因子转化为整数
    df_factor2 = df_factor2.astype('int')
    df_factor2.to_excel('%s各商圈地理因子数据.xlsx' % province)
    
    
    
    