# -*- coding: utf-8 -*-
"""
Created on Sun Apr 15 22:01:21 2018

@author: jasonai

以LinxData数据为例，解释定位高德坐标的关键点：
地址匹配使用高德匹配和百度匹配两种匹配方式，高德返回的经纬度值转换为百度标准的经纬度
高德使用三种匹配方式，三种方式都会返回定位点的地址信息、经纬度、定位的地址类型，
地址类型按精确度依次为兴趣点、道路交叉路口、道路、区县
1、省市区+附近标志+门店名
优点：精确定位。 缺点：准确度不高，容易定位到其他地址的同名门店
2、省市区+附近标志
优点：附近标志多为道路交叉口描述，高德容易模糊匹配出交叉口，有时也会精确定位到门店
缺点：大部分情况下只能定位到交叉口，经纬度有偏差
3、省市区+道路（使用正则从附近标志词条中拆分出两条道路名，未能拆分的用原始数据的路名列值替代）
返回的经纬度用来检验方式2的返回值
百度匹配与高德第三种方式相同，因为百度模糊匹配准确度不高，所以只采用“省市区+道路”的方式，
返回的经纬度与高德方式3的返回值对比

返回经纬度距离对比，返回两点之间的距离
OCM-高德1、OCM-高德2、高德1-高德2、高德2-高德3、高德3-百度
OCM-高德1、OCM-高德2分别用来验证高德1、高德2的准确度
高德1-高德2的值小于1000米，则以高德1为准，若高德1-高德2的值大于1000米，则用高德2-高德3、
高德3-百度并结合地址类型判断是否选择高德2
"""
import os
import sys
import json
import urllib
import math
import requests
import numpy as np
import pandas as pd
from pmipy import pmi
from tqdm import tqdm
from random import choice
from threading import Thread


gd_url = 'http://restapi.amap.com/v3/geocode/geo?' #高德地理编码api服务地址
keys_list = ['f7b56c52e26bf98164a8b06ed1a3c90b', 
             '4337cece3405f7495de78902fff69dc9', 
             'b7eb3425b1d5597e1fc29894e420f9f4', 
             '3e5ffa2677a079ca18529207517ff2c2', 
             '4e49937dc1527aa4ade3b21ee2577f8e', 
             'cae4213a875c0923ac134187ada841f6',]

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626  # π
a = 6378245.0  # 长半轴
ee = 0.00669342162296594323  # 偏心率平方


class Geocoding:
    def __init__(self, api_key):
        self.api_key = api_key

    def geocode(self, address):
        """
        利用高德geocoding服务解析地址获取位置坐标
        :param address:需要解析的地址
        :return:
        """
        geocoding = {'s': 'rsv3',
                     'key': self.api_key,
                     'city': '全国',
                     'address': address}
        geocoding = urllib.urlencode(geocoding)
        ret = urllib.urlopen("%s?%s" % ("http://restapi.amap.com/v3/geocode/geo", geocoding))

        if ret.getcode() == 200:
            res = ret.read()
            json_obj = json.loads(res)
            if json_obj['status'] == '1' and int(json_obj['count']) >= 1:
                geocodes = json_obj['geocodes'][0]
                lng = float(geocodes.get('location').split(',')[0])
                lat = float(geocodes.get('location').split(',')[1])
                return [lng, lat]
            else:
                return None
        else:
            return None


def gcj02_to_bd09(lng, lat):
    """
    火星坐标系(GCJ-02)转百度坐标系(BD-09)
    谷歌、高德——>百度
    :param lng:火星坐标经度
    :param lat:火星坐标纬度
    :return:
    """
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return [bd_lng, bd_lat]


def bd09_to_gcj02(bd_lon, bd_lat):
    """
    百度坐标系(BD-09)转火星坐标系(GCJ-02)
    百度——>谷歌、高德
    :param bd_lat:百度坐标纬度
    :param bd_lon:百度坐标经度
    :return:转换后的坐标列表形式
    """
    x = bd_lon - 0.0065
    y = bd_lat - 0.006
    z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)
    theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)
    gg_lng = z * math.cos(theta)
    gg_lat = z * math.sin(theta)
    return [gg_lng, gg_lat]


def wgs84_to_gcj02(lng, lat):
    """
    WGS84转GCJ02(火星坐标系)
    :param lng:WGS84坐标系的经度
    :param lat:WGS84坐标系的纬度
    :return:
    """
    if out_of_china(lng, lat):  # 判断是否在国内
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [mglng, mglat]


def gcj02_to_wgs84(lng, lat):
    """
    GCJ02(火星坐标系)转GPS84
    :param lng:火星坐标系的经度
    :param lat:火星坐标系纬度
    :return:
    """
    if out_of_china(lng, lat):
        return lng, lat
    dlat = _transformlat(lng - 105.0, lat - 35.0)
    dlng = _transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return [lng * 2 - mglng, lat * 2 - mglat]


def bd09_to_wgs84(bd_lon, bd_lat):
    lon, lat = bd09_to_gcj02(bd_lon, bd_lat)
    return gcj02_to_wgs84(lon, lat)


def wgs84_to_bd09(lon, lat):
    lon, lat = wgs84_to_gcj02(lon, lat)
    return gcj02_to_bd09(lon, lat)


def _transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def _transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


def out_of_china(lng, lat):
    """
    判断是否在国内，不在国内不做偏移
    :param lng:
    :param lat:
    :return:
    """
    return not (lng > 73.66 and lng < 135.05 and lat > 3.86 and lat < 53.55)


#======== 以下进行高德地址编码====================================
# 第一次返回结果，很有可能包含网络无响应的数据;checkResult装饰器可判断网络相应情况，如无响应则继续循环执行gd_geocode函数
@pmi.checkResult(keyword=2.0, loopTime=30) 
@pmi.checkResult(keyword=1.0, loopTime=30) 
def gd_geocode(address): #根据地址获取高德经纬度后转化为百度经纬度\
    # 解决高德API日访问次数限制问题
    key = choice(keys_list)
    gd_parm1 = {'key': key, 'address': address, 'city': '',} #高德key
    try:
        response = requests.get(url=gd_url, params=gd_parm1, timeout=10).json()
        if response['status'] == '1':
            # 获取第一个返回地址信息
            geocode = response['geocodes'][0]
            lng = float(geocode['location'].split(',')[0])
            lat = float(geocode['location'].split(',')[1])
            f_address = geocode['formatted_address']
            province = geocode['province']
            city = geocode['city']
            district = geocode['district']
            level = geocode['level']
            result = [lng, lat, f_address, province, city, district, level]
        else:
            result = [2.0,2.0,'','','','',''] # 请求失败使用2.0表示
    except:
        print("地址为：", address)
        result = [1.0,1.0,'','','','',''] # 网络无响应使用1.0表示
    print('===>',result)
    return result


def run_thread(df, adr_search):
    res_list = []
    for adr in df[list(adr_search)].sum(axis=1):
        res_list.append(gd_geocode(adr))
    df2 = pd.DataFrame(res_list,columns=['经度','纬度','返回地址','省','市','区','地址类型'],index=df.index)
    # df[['new1', 'new2', 'new3', 'new4','new5', 'new6','new7']] = df.apply(gd_geocode)
    return pd.concat([df,df2],axis=1)


# 多线程
class MyThread(Thread):
    def __init__(self, df, adr_search):
        Thread.__init__(self)
        self.df = df
        self.adr_search = adr_search

    def run(self):
        self.result = run_thread(self.df, self.adr_search)

    def get_result(self):
        return self.result


def transform(df, lnglat, initial_coordinate, target_coordinate):
    res_list =[]
    for lng, lat in tqdm(df[list(lnglat)].values):
        if initial_coordinate == 'gaode':
            if target_coordinate == 'baidu': # 高德转百度
                res_list.append(gcj02_to_bd09(lng, lat))
            elif target_coordinate == 'global': # 高德转国际
                res_list.append(gcj02_to_wgs84(lng, lat))
            else:
                sys.exit('{0}转{1}尚未开发，如有需求，请邮件jasonai！'.format(initial_coordinate, target_coordinate))
        elif initial_coordinate == 'baidu':
            if target_coordinate == 'gaode': # 百度转高德
                res_list.append(bd09_to_gcj02(lng, lat))
            elif target_coordinate == 'global': # 百度转国际
                res_list.append(bd09_to_wgs84(lng, lat))
            else:
                sys.exit('{0}转{1}尚未开发，如有需求，请邮件jasonai！'.format(initial_coordinate, target_coordinate))
        elif initial_coordinate == 'global':
            if target_coordinate == 'gaode': # 国际转高德
                res_list.append(wgs84_to_gcj02(lng, lat))
            elif target_coordinate == 'baidu': # 国际转百度
                res_list.append(wgs84_to_bd09(lng, lat))
            else:
                sys.exit('{0}转{1}尚未开发，如有需求，请邮件jasonai！'.format(initial_coordinate, target_coordinate))
        else:
            sys.exit('{0}转{1}尚未开发，如有需求，请邮件jasonai！'.format(initial_coordinate, target_coordinate))
    res_df = pd.DataFrame(res_list, columns=[target_coordinate+'经度',target_coordinate+'纬度'],index=df.index)
    
    return pd.concat([df, res_df], axis=1)
   
    
@pmi.execInfo()
def coordinateTransform(filepath, file_ouput, lnglat, initial_coordinate, target_coordinate):
    path = os.path.split(filepath)[0]
    filename = os.path.splitext(os.path.split(filepath)[1])[0]
    filesuffix = os.path.splitext(os.path.split(filepath)[1])[1]
    # 读取文件
    if filesuffix == '.csv':
        df = pd.read_csv(filepath, engine='python')
    elif filesuffix == '.xlsx':
        df = pd.read_excel(filepath)
    else:
        sys.exit('Please input csv or xlsx file!')
    
    df_res = transform(df, lnglat, initial_coordinate, target_coordinate)
    if file_ouput:
        filename = file_ouput
    outfile = filename + '_转' + target_coordinate + '坐标.xlsx'
    df_res.to_excel(os.path.join(path, outfile), index=False)
    

@pmi.execInfo()
def getTargetCoordinate(filepath, adr_search, thread=20, target_coordinate='gaode',file_ouput=''):
    path = os.path.split(filepath)[0]
    filename = os.path.splitext(os.path.split(filepath)[1])[0]
    filesuffix = os.path.splitext(os.path.split(filepath)[1])[1]
    # 读取文件
    if filesuffix == '.csv':
        df = pd.read_csv(filepath, engine='python')
    elif filesuffix == '.xlsx':
        df = pd.read_excel(filepath)
    else:
        sys.exit('Please input csv or xlsx file!')
    
    try:
        thread = int(thread)
    except ValueError:
        sys.exit('请输入正确的线程数(整数值)！')
    # df = df.head(50)
    # 如果线程数小于数据框长度的1/2
    if thread < len(df) / 2:
        df_split = np.array_split(df, thread)
    else:
        df_split = np.array_split(df, 2)

    # 构建多线程
    thd_list = []
    for df in df_split:
        thd = MyThread(df, adr_search)
        thd.start()
        thd_list.append(thd)
    
    for t in thd_list: # 等待所有线程执行完毕
        t.join()
    
    res_list = []
    for t in thd_list:
        res = t.get_result()
        # print(t.get_result())
        res_list.append(res)
    
    df_res = pd.concat(res_list) 
    
    if target_coordinate != 'gaode':
        df_res = transform(df_res, ['经度','纬度'], 'gaode', target_coordinate)
    if file_ouput:
        filename = file_ouput
    outfile = filename + '_' + target_coordinate + '坐标.xlsx'
    df_res.to_excel(os.path.join(path, outfile), index=False)


if __name__ == '__main__':
    filepath = r'E:\CloudStation\康饮商圈分析\零售饮料\江苏省linxdata_经纬度匹配最终版V1.xlsx'
    adr_search = ['省份','城市名称','附近标志']
    getTargetCoordinate(filepath, adr_search)
    