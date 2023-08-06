# -*- coding: utf-8 -*-
"""
Created on Tue May  8 12:25:03 2018

@author: Administrator
"""

import pandas as pd
from pmipy import pmi
from pmipy.support import prov_mapp


def waimai_update(client, province, time):
    provm = prov_mapp.prov_dist
    sql = [{'$group' : {'_id' : {'city':'$lv2Name','region':'$lv3Name'}, 
                       '销量':{'$sum':'$monthSaleCount'}}}]

    # 将省名转为英文名
    prov = provm[province]
    # 美团
    db_meituan = client['WaimaiMeituan_{}'.format(time)]
    cursor = db_meituan[prov].aggregate(sql)
    df_meituan = pd.DataFrame(list(cursor))
    df_meituan['市'] = df_meituan['_id'].apply(lambda x: x['city'])
    df_meituan['行政区'] = df_meituan['_id'].apply(lambda x: x['region'])
    df_meituan.drop('_id', axis=1, inplace=True)
    df_meituan.set_index(['市', '行政区'], inplace=True)
    # 饿了么
    db_eleme = client['Eleme_{}'.format(time)]
    cursor = db_eleme[prov].aggregate(sql)
    df_eleme = pd.DataFrame(list(cursor))
    df_eleme['市'] = df_eleme['_id'].apply(lambda x: x['city'])
    df_eleme['行政区'] = df_eleme['_id'].apply(lambda x: x['region'])
    df_eleme.drop('_id', axis=1, inplace=True)
    df_eleme.set_index(['市', '行政区'], inplace=True)
    # 百度外卖
    db_baidu = client['WaimaiBaidu_{}'.format(time)]
    cursor = db_baidu[prov].aggregate(sql)
    df_baidu = pd.DataFrame(list(cursor))
    df_baidu['市'] = df_baidu['_id'].apply(lambda x: x['city'])
    df_baidu['行政区'] = df_baidu['_id'].apply(lambda x: x['region'])
    df_baidu.drop('_id', axis=1, inplace=True)
    df_baidu.set_index(['市', '行政区'], inplace=True)
    # 合并三大外卖
    df_merge = pd.concat([df_meituan, df_eleme, df_baidu], join='outer', axis=1)
    df_merge.columns = ['美团外卖', '饿了么外卖', '百度外卖']
    df_merge['外卖销量'] = df_merge.sum(axis=1)
    df_merge.reset_index(inplace=True)
    df_merge['省'] = province
    # 处理直辖市问题
    if province in ['上海市', '北京市', '重庆市', '天津市']:
        if len(df_merge['行政区'].isnull()) > len(df_merge) * 0.5:
            df_merge['行政区'] = df_merge['市']
            df_merge['市'] = df_merge['省']
    df_merge.set_index(['省', '市', '行政区'], inplace=True)

    return df_merge


def factor_update(df_label, client, province):
    collection = client['Claudius']['TileData']
    group_dict = {'_id' : {'city':'$city','region':'$region'}}
    for index in df_label.index:
        group_dict[index] = {'$sum' : '${0}.{1}'.format(df_label.loc[index,'数据源'], 
                  df_label.loc[index,'sub'])}
    
    sql = [
        {'$match':{'province':province, 'processTime':'201711', 'meters':1000}},
        {'$group' : group_dict},
        ]

    cursor = collection.aggregate(sql)

    df = pd.DataFrame(list(cursor))
    # 标注省、市、行政区县信息
    df['省'] = province
    df['市'] = df['_id'].apply(lambda x: x['city'])
    df['行政区'] = df['_id'].apply(lambda x: x['region'])
    cols = list(df)
    cols = cols[-3:] + cols[1:-3]
    df = df[cols]
    df.set_index(['省', '市', '行政区'], inplace=True)
    return df


# 因子名称应设为索引
def update(df_manifest, province, time, LAN):
    client16 = pmi.connOcm16(LAN)
    isWaimai = False
    # 暂时去除外卖
    if '外卖' in df_manifest.index:
        isWaimai = True
        df_waimai = waimai_update(client16, province, time)
        df_manifest = df_manifest[~df_manifest.index.str.contains('外卖')]
    df_factor = factor_update(df_manifest, client16, province)
    if isWaimai:
        df_factor = pd.concat([df_factor, df_waimai], axis=1)
    
    # 对缺失值进行填0处理
    df_factor = df_factor.fillna(0)
    return df_factor


if __name__ == '__main__':
    # df_manifest = 'manifest.xlsx'
    tt = update(df_manifest,'甘肃省', 201712, False)