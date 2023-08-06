# -*- coding: utf-8 -*-
"""
Created on Mon Apr  2 21:38:10 2018

@author: jasonai
"""


from pmipy import log
from pmipy import pmi
from tqdm import tqdm
import pandas as pd
import copy
import os
import shelve
#from pmipy.support import prov_mapp
from pmipy.OCM import updateTileFactor as utf


logger = log.createLogger(__name__)


class MyMongoOperator(object):
    def __init__(self,):
        self.client = pmi.connOcm16()

    # 指定数据库和集合
    def connect2DB_COLL(self, dbname, collection):
        self.collection = self.client[dbname][collection]
        return self.collection

    def find(self, *args, **kwargs):
        return self.collection.find(*args, **kwargs)

    def findOne(self, query):
        return self.collection.find_one(query)

    def closeConn(self):
        self.client.close()


class OCMLatLng(object):
    def __int__(self):
        pass

    def getEWSN(self, lv1Name=None, lv2Name=None, lv3Name=None):
        '''
        获得指定地区的临界坐标, 全为None则返回中国的临界坐标,此函数只是为了得到中国最东南西北的经纬度
        :param lv1Name: 省
        :param lv2Name: 市
        :param lv3Name: 区
        :return: (e,w,s,n) 边界经纬度
        '''
        mongo = MyMongoOperator()
        mongo.connect2DB_COLL(dbname='Claudius', collection='GeoBoundary')
        result = mongo.find({"lv1Name": lv1Name, "lv2Name": lv2Name, "lv3Name": lv3Name}, {'boundaries': 1})
        try:
            each = result.__next__()
            each = each['boundaries']
            # 经度
            e_lng = map(lambda item: float(item['lng']), each)
            w_lng = copy.deepcopy(e_lng)
            # 纬度
            s_lat = map(lambda item: float(item['lat']), each)
            n_lat = copy.deepcopy(s_lat)
            e = max(e_lng)  # 东
            w = min(w_lng)  # 西
            s = min(s_lat)  # 南
            n = max(n_lat)  # 北
        except:
            raise
        finally:
            mongo.closeConn()
        return e, w, s, n

    def getMatrix(self, meters=1000):
        '''
        对全国进行划分
        :param meters: 网格宽度,默认是一公里
        :return: 格子
        '''
        e, w, s, n = self.getEWSN()
        # 以上海作為長寬的基準距離(不同經緯度的長寬其實不同)
        width = 0.00001 * meters  # 即1网格宽度（米）转化为经度
        height = 0.000009 * meters

        def TernaryOperator(op1, op2, refer, res1, res2):
            if op1 % op2 > refer:
                return res1
            else:
                return res2

        lngSize = int((e - w) / width) + TernaryOperator((e - w), width, 0, 1, 0) + 1 # 计算横向的网格数
        latSize = int((n - s) / height) + TernaryOperator((n - s), height, 0, 1, 0) + 1 # lngSize*latSize = 24278280

        self.lngs = []
        for i in range(lngSize):
            self.lngs.append(w + (i * width))
        self.lats = []
        for i in range(latSize):
            self.lats.append(s + (i * height))

        return self.lngs, self.lats


    def getTileName(self, lng, lat):
        '''
        根据经纬度获得tileName
        :param lng: 经度
        :param lat: 纬度
        :return: 成功: tileName
                 失败: None
        '''
        if not isinstance(lng,float) or not isinstance(lat, float):
            logger.warning("{}或{}不是数值型，将返回空值！".format(lng,lat)) # raise TypeError('lng or lat must "float"')
            return ''
        if not hasattr(self, 'lngs'):
            raise AttributeError("'{}' object has no attribute '{}'".format('LatLng', 'lngs'))
        if not hasattr(self, 'lats'):
            raise AttributeError("'{}' object has no attribute '{}'".format('LatLng', 'lats'))

        for i in range(len(self.lngs) - 1):  # 0-9,只遍历0-8
            if self.lngs[i] <= lng and lng < self.lngs[i + 1]:
                for j in range(len(self.lats) - 1):
                    if self.lats[j] <= lat and lat < self.lats[j + 1]:
                        return '{}-{}'.format(i, j)

    def getTileNames(self, lng, lat, tileNum):
        tileName = self.getTileName(lng, lat)
        centerPoint = self.getCenterPoint(tileName)
        deflection = self.getDeflection(lng, lat, centerPoint)
        if tileNum == 4:
            tileNames = self.getContigeousTileName_4(tileName, deflection)
        elif tileNum == 9:
            tileNames = self.getContigeousTileName_9(tileName, deflection)
        else:
            logger.info('目前{}取数未开发！'.format(tileNum))
            raise SystemExit
        tileNameList = tileNames.split(',')
        return tileNameList

    # 获得中心点
    def getCenterPoint(self, tileName):
        '''
        获得给定位置的中心点位置
        :param tileName
        :return: 中心点的经纬度
        '''
        tmp = tileName.split('-')
        lng_index = int(tmp[0])
        lat_index = int(tmp[1])
        return (self.lngs[lng_index] + self.lngs[lng_index + 1]) / 2, \
               (self.lats[lat_index] + self.lats[lat_index + 1]) / 2


    # 判断坐标的格子偏向
    def getDeflection(self, lng, lat, centerPoint):
        '''
        获得当前经纬度在格子中的偏向
        :param lng: 经度
        :param lat: 纬度
        :param centerPoint: 中心点
        :return: 0 ↖
                 1 ↗
                 2 ↘
                 3 ↙
                 ↖↗
                 ↙↘
        '''
        if lat > centerPoint[1]:
            if lng < centerPoint[0]:
                return 0
            else:
                return 1
        else:
            if lng > centerPoint[0]:
                return 2
            else:
                return 3

    def getContigeousTileName_4(self, tileName, deflection):
        '''
        根据经纬度的索引获得相邻四格的tileName
        :param tileName: '4798-1461'
        :param deflection: 偏离方向
        :return: 相邻四格的tileName
        '''
        tmp = tileName.split('-')
        x = int(tmp[0])
        y = int(tmp[1])
        if deflection == 0:
            # {}-{},{}-{},{}-{},{}-{} 按getDeflection编号
            return '{}-{},{}-{},{}-{},{}-{}'.format(
                x - 1, y + 1,
                x, y + 1,
                x, y,
                x - 1, y
            )
        elif deflection == 1:
            return '{}-{},{}-{},{}-{},{}-{}'.format(
                x, y + 1,
                   x + 1, y + 1,
                   x + 1, y,
                x, y,
            )
        elif deflection == 2:
            return '{}-{},{}-{},{}-{},{}-{}'.format(
                x, y,
                x + 1, y,
                x + 1, y - 1,
                x, y - 1,
            )
        else:
            return '{}-{},{}-{},{}-{},{}-{}'.format(
                x - 1, y,
                x, y,
                x, y - 1,
                x - 1, y - 1,
            )

    def getContigeousTileName_9(self, tileName):
        '''
        根据经纬度的索引获得相邻九格的tileName
        :param tileName: '4798-1461'
        :return: 相邻九格的tileName
                            0 1 2
                            5 4 3
                            6 7 8
        '''
        tmp = tileName.split('-')
        x = int(tmp[0])
        y = int(tmp[1])
        return '{}-{},{}-{},{}-{},{}-{},{}-{},{}-{},{}-{},{}-{},{}-{}'.format(
            x - 1, y + 1, x, y + 1, x + 1, y + 1,
            x + 1, y, x, y, x - 1, y,
            x - 1, y - 1, x, y - 1, x + 1, y - 1
        )

    def getContigeousTileName_1(self, tileName, deflection):
        return tileName


    def serialize(self):
        '''
        数据序列化与反序列化
        :return:
        '''
        tempPath = os.path.join(os.path.split(utf.__file__)[0],'_temp_')
        if os.path.isfile(os.path.join(tempPath,'geo.dat')):
            # 读数据
            logger.info('反序列化经纬度信息')
            with shelve.open(os.path.join(tempPath,'geo')) as db:
                for key, value in db.items():
                    if key == 'lngs':
                        self.lngs = value
                    else:
                        self.lats = value
        else:
            # 写数据
            logger.info('程序初次执行,序列化经纬度信息')
            if not os.path.exists(tempPath):
                os.makedirs(tempPath)
            self.getMatrix(1000)
            with shelve.open(os.path.join(tempPath,'geo')) as db: # shelve可使保存的数据的数据结构不变
                db['lngs'] = self.lngs
                db['lats'] = self.lats


def readXlsCsv(filePath):
    [path, file] = os.path.split(filePath)
    [fileName, fileSuffix] = os.path.splitext(file)
    if fileSuffix == '.xlsx' or fileSuffix == '.xls':
        df = pd.read_excel(filePath)
    elif fileSuffix == '.csv':
        try:
            df = pd.read_csv(filePath, engine='python')
        except pd.errors.ParserError: # csv为tab键分割的情况
            df = pd.read_csv(filePath, sep='\t', engine='python')
    else:
        logger.error("Please input csv or xlsx file!")
        raise SystemExit(1) 
        
    return df, path, fileName


@pmi.execInfo()
def getOcmDataByLngLat(filePath, lnglat, tileNum=4, outputFile=''):
    ll = OCMLatLng()
    ll.serialize()
    gbt = utf.getDataByTileName()
    logger.info("成功连接数据库！")
    df, path, fileName = readXlsCsv(filePath)
    df_ll = df[list(lnglat)]
    recordList = []
    if tileNum == 1:
        for lng, lat in tqdm(df_ll.values):
            tileName = ll.getTileName(lng, lat)
            recordList.append(gbt.commom(tileName))
    else:  # 获取邻近多个网格数据
        for lng, lat in tqdm(df_ll.values):
            tileNameList = ll.getTileNames(lng, lat, tileNum)
            tempList = []
            for tileName in tileNameList:
                tempList.append(gbt.commom(tileName))
            df_temp = pd.DataFrame(tempList)
            df_temp = df_temp.sum()
            recordList.append(dict(df_temp))

    df2 = pd.DataFrame(recordList)
    df = pd.concat([df, df2], axis=1)
    # 输出文件名
    if not outputFile:
        outputFile = fileName + '_ocm.xlsx'
    else:
        outputFile = outputFile + '.xlsx'
    output = os.path.join(path, outputFile)
    df.to_excel(output, index=False)
    logger.info("输出文件路径为:%s" % output)
    return df


"""
def getOcmDataByRegion(province):
    if province == '全国':
        pass
    else:
        if not province in prov_mapp.prov_dist2.values():
            try:
                province = prov_mapp.prov_dist2[province]
            except KeyError:
                logger.info('请输入正确的省份名称！')
                raise SystemExit
"""


if __name__ == '__main__':
    filePath = '深圳网吧_转baidu坐标.xlsx'
    lnglat = ['经度', '纬度']
    getOcmDataByLngLat(filePath, lnglat)




