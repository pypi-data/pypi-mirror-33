# -*- coding: utf-8 -*-
"""
Created on Wed Jun 27 10:01:43 2018

@author: Administrator
"""

import pandas as pd
from pmipy import pmi


def parseJson_old(record):
    row = {}
    for tier1 in record.keys():
        if type(record[tier1])==dict:
            for tier2 in record[tier1].keys():
                if type(record[tier1][tier2])==dict:
                    for tier3 in record[tier1][tier2].keys():
                        if type(record[tier1][tier2][tier3])==dict: 
                            for tier4 in record[tier1][tier2][tier3].keys():
                                if type(record[tier1][tier2][tier3][tier4])==dict: 
                                    for tier5 in record[tier1][tier2][tier3][tier4].keys():
                                        row[tier1+'.'+tier2+'.'+tier3+'.'+tier4+'.'+tier5] = record[tier1][tier2][tier3][tier4][tier5]
                                else:
                                    row[tier1+'.'+tier2+'.'+tier3+'.'+tier4] = record[tier1][tier2][tier3][tier4]
                        else:
                            row[tier1+'.'+tier2+'.'+tier3] = record[tier1][tier2][tier3]
                else:
                    row[tier1+'.'+tier2] = record[tier1][tier2]
        else:
            row[tier1] = record[tier1]
    return row


# 拆解字典对象的key需要配合 fieldNamesFormat 函数使用 -> .a.b.c等
def parseJson(record: dict):
    def _process(record: dict, fieldnames={}, key=''):
        """
        提取要生成csv文件的标题字段
        :param record: dict对象
        :param fieldnames: 存字段的字典{}
        :param key:
        """
        for each in record.keys():
            if isinstance(record[each], dict):
                 _process(record[each], fieldnames,key + '.' + each)
            else:
                key2 =  key + '.' + each
                fieldnames[key2[1:]] = record[each]
        
        return fieldnames
    return _process(record)


def getDataFrame(cursor): 
    rowList = []
    for record in cursor:
        row = parseJson(record)
        rowList.append(row)
    df = pd.DataFrame(rowList)
    return df


# 去除“其他”
def removeOther(df): 
    col =  [i for i in list(df) if '其他' not in i]
    return df[col]

# 去除列名中的指定字段，比如'categories'
def removeTag(df, tagList=['categories.']):
    col = list(df)
    for tag in tagList:
        col = [i.replace(tag, '') for i in col]
    df.columns = col
    return df


class getDataByTileName(object):
    def __init__(self, tagList=['poi','dianping','population','anjuke','anjukeRent','segmentation'], 
                 MongoDB='Claudius', collection='TileData'):
        client16 = pmi.connOcm16()
        self.collection = client16[MongoDB][collection]
        self.showDict = {'province':1, 'city': 1, 'tileName': 1, '_id': 0}
        for tag in tagList:
            self.showDict[tag] = 1

    def commom(self, tileName): # poi、dianping
        cursor = self.collection.find_one({'tileName': tileName, 'meters': 1000, 'processTime':'201711'},
                                          self.showDict, no_cursor_timeout=True)
        try:
            _dict = parseJson(cursor)
        except AttributeError:
            _dict = {'tileName': tileName}
          
        return _dict


if __name__ == '__main__':
    # 测试
    gd = getDataByTileName()
    c=gd.commom('4767-1475')


