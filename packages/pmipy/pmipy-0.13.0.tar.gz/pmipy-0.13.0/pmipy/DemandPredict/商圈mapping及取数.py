# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 20:40:39 2018

@author: jasonai
"""

import os
import re
import collections
import pandas as pd
from pymongo import MongoClient

# 连接OCM1.6
def conn_ocm16(LAN=True):
    IP_LAN = '192.168.0.21:27017'
    IP_PN = 'www.parramountain.com:47017'
    IP = IP_LAN if LAN else IP_PN   
    uri = 'mongodb://laocheng:laocheng@{0}'.format(IP)
    client = MongoClient(uri)
    db = client['Claudius']
    collection = db['TileData']
    return collection

# 连接OCM1.5
def conn_ocm15(LAN=True):
    IP_LAN = '192.168.0.11:27017'
    IP_PN = 'www.parramountain.com:37017'
    IP = IP_LAN if LAN else IP_PN   
    uri = 'mongodb://liushizhan:liushizhan@{0}'.format(IP)
    client = MongoClient(uri)
    db = client['Claudius3']
    collection = db['TileData']
    return collection



def busi_mapping(province = '湖北省'):
    # 获取指定省份下的商圈名单
    try:
        busiTitle = '具体描述'
        df1 = pd.read_excel('%sKSF各商圈TT&MT出货.xlsx' % province, usecols=[busiTitle])
    except ValueError:
        busiTitle = '商圈'
        df1 = pd.read_excel('%sKSF各商圈TT&MT出货.xlsx' % province, usecols=[busiTitle])
    
    # 指定省份各区县地理因子
    df2 = pd.read_excel('%s各区县特通点数及人口数据.xlsx' % province, index_col='区县')
    
    # 存放OCM区县完整名单
    county_full = collections.Counter(df2.index)
    # 存放OCM区县去尾（市区县）名单
    list_cs = [i[:-1] for i in df2.index]
    county_simple = collections.Counter(list_cs)
    # 存放商圈信息的字典
    busi_dict = {}
    for busi in df1.values[:, 0]:
        district_list = re.split(r'[、，,()（）]', busi)
        # 商圈包含的区县信息
        temp_list = []
        info_list = []
        for index, district in enumerate(district_list):
            # 排除包含'市辖'的字段或空字段
            if ('市辖' not in district) and (district != ''):
                # mapping商圈中提取得到的区县
                if county_full[district] == 1:
                    temp_list.append(district)
                    info_list.append('匹配')
                # 判断是否为县改区或市
                elif county_simple[district[:-1]] == 1:
                    # 获取区县字段所在位置
                    county_index = list_cs.index(district[:-1])
                    temp_list.append(df2.index[county_index])
                    info_list.append('可能级别变动')
                elif (county_full[district]>1) or (county_simple[district]>1) :
                    info_list.append('区县名重复')
                else:
                    info_list.append('匹配失败')
        if ('区县名重复' in info_list) or ('匹配失败' in info_list):
            info2 = '失败'
        else:
            info2 = '成功'
        busi_dict[busi] = [temp_list, info_list, info2]
    df3 = pd.DataFrame(busi_dict).T
    df3.columns = ['匹配区县', '信息描述', '匹配状态']
    # df3.to_excel('%s商圈与OCM区县匹配结果.xlsx' % province, index_label=busiTitle)、
    return df3


df busi_mapping()






