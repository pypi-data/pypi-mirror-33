# -*- coding: utf-8 -*-
"""
Created on Sun May 13 10:22:30 2018

@author: jasonai
"""

import os
import pandas as pd
from pmipy import pmi
from pmipy import log
from pmipy.support import prov_mapp
from pmipy.OCM import updateRegionFactor

try:
    config = pmi.ConfigHandler(__file__)
except NameError:
    config = pmi.ConfigHandler('calShipment.py')
mt = config.read_configure('Manifest.ini', 'tag')
# 数据库或数据表名称
dbName = mt['dbName']
regionFactor = mt['regionFactor']
areaFactor = mt['areaFactor']
factorTime = mt['factorTime']
province = mt['province']
city = mt['city']
region = mt['region']
businessArea = mt['businessArea']
partitionName = mt['partitionName']
factorType = mt['factorType']
factorNum = mt['factorNum']
timeCol = mt['timeCol']
marketingCompany = mt['marketingCompany']
salesDepartment = mt['salesDepartment']
# 区分不同商圈商圈名相同的额外信息
busAdInfo1 = [marketingCompany, salesDepartment, businessArea]
# 内容
updateTime = mt['updateTime']
periodTag = mt['periodTag'] # 1705-1804
logger = log.createLogger(__name__)
cm = pmi.ConnMysql(dbName)


## 开个接口解决无行政区县的地级市<东莞、中山>
def citytoregion(df, filePath='东莞中山2017常住人口.xlsx'):
    df_supp = pd.read_excel(filePath)[[province, city, region, '人口']]
    cityList = list(df_supp[city].drop_duplicates())
    for i, c in enumerate(cityList):
        df_supp2 = df_supp[df_supp[city]==c]
        # 计算各镇人口比例
        df_supp2['人口'] = df_supp2['人口'] / df_supp2['人口'].sum()
        df2 = df[df['city']==c].drop(region, axis=1)
        df_megre = df2.merge(df_supp2, on=[province, city], how='left')
        df_megre[factorNum] = df_megre[factorNum] * df_megre['人口']  # 此过程可使用随机数
        df_megre[factorNum] = df_megre[factorNum].astype('int') # 个数为整数
        df_megre.drop('人口', axis=1,inplace=True)
        df = df[df[city] != c]
        df = pd.concat([df,df_megre])
        
    return df

# 更新各省各区县的因子数据，time为外卖数据的爬取时间
def regionFactorUpdate(factorManifest, exMethod, LAN=True):
    manifest_info= pmi.readXlsCsv(factorManifest)
    df_manifest = manifest_info['data']
    # 必须步骤，设索引：
    df_manifest.set_index('因子', inplace=True)
    # 从prov_mapp中获取省名单信息
    for index, province in enumerate(prov_mapp.prov_dist):
        try:
            if not index:
                df_factor = updateRegionFactor.update(df_manifest, province, factorTime, LAN)
            else:
                df_factor = df_factor.append(updateRegionFactor.update(df_manifest, province, factorTime, LAN))
        except Exception as e:
            logger.warning("<{}>取数失败！异常信息为:{}！".format(province, e))
        else:
            logger.info("完成<{}>各行政区的地理/商业环境因子取数！".format(province))
    # stack并上传至数据库
    df_factor2 = df_factor.stack().reset_index()
    # 特殊格式要求：商圈分级项目需将行政区的列名修正
    df_factor2.rename(columns={'省': province,'市': city, '行政区': region, 
                               'level_3': factorType, 0:factorNum}, inplace=True)
    df_factor2 = citytoregion(df_factor2) # 解决无行政区县的地级市<东莞、中山>
    df_factor2[timeCol] = factorTime
    cm.toMysql(regionFactor, df_factor2, updateTime, exMethod)
    logger.info("成功将各行政区的地理/商业环境因子数据长传至%s数据表！" % regionFactor)


def areaFactorUpdate(factorManifest, exMethod='replace'):
    # 获取特定时间段更新的地理因子
    sql_factor = "select {},{},{},{},{} from {} where {}={}".format(province,
                         city, region, factorType, factorNum, regionFactor, timeCol, factorTime)
    try:
        df_factor = pd.read_sql(sql_factor, cm.engine)
    except:
        regionFactorUpdate(factorManifest, exMethod)
        df_factor = pd.read_sql(sql_factor, cm.engine)
        
    # 修改人口数据
    def changePopulation(df, filePath='原始数据/各省市人口2016年末常住人口数据.xlsx'):
        df_p = pd.read_excel(filePath, sheetname='常住人口')
        # 去除不含常住人口，或者OCM缺失行政区划的数据
        df_p = df_p[(df_p['常住人口'].notnull())&(df_p[province].notnull())].drop('num',axis=1)
        df_merge = df.merge(df_p, on=[province,city, region], how='left')
        #pl = len(df_merge[(df_merge['省'].notnull())&(df_merge[factorType]=='人口')])
        #logger.info("总共更新了{}个行政区的常住人口数据!".format(pl))
        df_merge.loc[(df_merge[factorType]=='人口')&(df_merge['常住人口'].notnull()), factorNum] = df_merge['常住人口']
        df_merge = df_merge[list(df)]
        
        return df_merge
        
    # 修改部分不匹配的行政区划名称
    def changeRegionName(df, filePath='原始数据/区县不匹配对应表.xlsx'):
        df_map = pd.read_excel(filePath)
        df_map = df_map.drop_duplicates(['省_db', '市_db', '行政区划_db'])
        df_merge = df.merge(df_map, left_on=[province,city, region], 
                            right_on=['省_db', '市_db', '行政区划_db'], how='left')
        #length = len(df_merge[df_merge['省'].notnull()].drop_duplicates([province,city, region]))
        #logger.info("总共更换了{}个行政区的名称!".format(length))
        df_merge.loc[df_merge['省'].notnull(), city] = df_merge['市']
        df_merge.loc[df_merge['省'].notnull(), region] = df_merge['行政区划']
        df_merge.drop(list(df_map), axis=1, inplace=True)
        
        return df_merge


    # 修改/更新OCM缺失的region98*--+
    def createRegion(df, filePath='原始数据/OCM缺失的行政区.xlsx'):
        df2 = df.copy()
        df_o = pd.read_excel(filePath) # ['province', 'city', 'region', 'district', 'population', 'level']
        # 省份水平
        if len(df_o[df_o['level']==province]):
            df_op = df_o[df_o['level']==province][[province, city, region, 'population']]
            df_prov = df2.groupby([province, factorType], as_index=False).sum()
            df_prov2 = df_prov.merge(df_prov[df_prov[factorType]=='人口'][[province,factorNum]],on=province)
            df_prov2['人均点数'] = df_prov2[factorNum+'_x'] / df_prov2[factorNum+'_y']
            df_op2 = df_op.merge(df_prov2[[province,factorType,'人均点数']],on=province)
            df_op2[factorNum] = df_op2['人均点数'] * df_op2['population']
            df_op2[factorNum] = df_op2[factorNum].astype('int')
            df2 = pd.concat([df2, df_op2],join='inner')
        # 城市水平
        if len(df_o[df_o['level']==city]):
            df_oc = df_o[df_o['level']==city][[province, city, region, 'population']]
            df_city = df2.groupby([province, city, factorType], as_index=False).sum()
            df_city2 = df_city.merge(df_city[df_city[factorType]=='人口'][[province,city,factorNum]],on=[province,city])
            df_city2['人均点数'] = df_city2[factorNum+'_x'] / df_city2[factorNum+'_y']
            df_oc2 = df_oc.merge(df_city2[[province,city,factorType,'人均点数']],on=[province,city])
            df_oc2[factorNum] = df_oc2['人均点数'] * df_oc2['population']
            df_oc2[factorNum] = df_oc2[factorNum].astype('int')
            df2 = pd.concat([df2, df_oc2],join='inner')
        
        """# region水平
        if len(df_o[df_o['level']=='region']):
            df_or = df_o[df_o['level']=='region'][[province, city, region, 'population']]"""
        
        return df2
    
    df_factor = changePopulation(df_factor)
    df_factor = changeRegionName(df_factor)
    df_factor = createRegion(df_factor)
    
    # 各区县通路点数乘以分配系数，解决一区多商圈的问题
    sql_coef = "select {},{},{},{},{},{},partitionCoefficient from {} where {}='{}'".format(marketingCompany, province, 
                       salesDepartment, city, region, businessArea, partitionName, timeCol, periodTag)
                       
    df_coef = pd.read_sql(sql_coef, cm.engine)
    # mapping
    df_merge = df_coef.merge(df_factor, on=[province, city, region], how='left')
    # 获取因子list
    df_merge[factorNum] = df_merge[factorNum] * df_merge['partitionCoefficient']
    ## 输出未匹配的行政区划
    df_check1 = df_merge.groupby([marketingCompany, province, salesDepartment, city, region, businessArea]).sum()
    df_merge2 = df_check1.reset_index()
    df_check1 = df_check1[df_check1[factorNum].isnull()].reset_index()
    df_check1['problem'] = '疑似行政区划匹配失败'
    df_check1.loc[df_check1['partitionCoefficient'].isnull(), 'problem'] = '疑似商圈缺失数据'
    ## '省', '市', '区', '商圈'都一样的情况
    df_check2 = df_merge2[df_merge2.duplicated([marketingCompany, salesDepartment, region, businessArea])]
    df_check2['problem'] = '疑似商圈名有重复'
    df_check = df_check1.append(df_check2)
    # 去除大部分因子，保留第一个和最后一个因子
    """df_check = df_check.drop(factorCols[1:-1], axis=1)
    df_check.ix[df_check[factorCols[-1]]==0, '问题'] = '区县无数据'"""
    if not os.path.exists('产出数据'):
        os.makedirs('产出数据')
    df_check.to_excel('产出数据/未匹配的行政区划_%s.xlsx'%periodTag, index=False)
    # 去除tm.regionFactor、区县分销量、 区县总销量和分配系数
    # 计算商圈的因子数量
    df_merge3 = df_merge.groupby(busAdInfo1 + [factorType], as_index=False).sum()
    # 去除无因子信息的商圈
    df_area_factor = df_merge3[df_merge3[factorNum].notnull()]
    df_area_factor = df_area_factor.drop('partitionCoefficient', axis=1)
    """df_area_factor_total = df_merge3.groupby(busAdInfo1, as_index=False).sum()
    # 为保证后续机器学习计算。此处将商圈各因子总和为0的情况去除
    df_area_factor_total = df_area_factor_total[df_area_factor_total[factorNum]!=0]
    
    df_area_factor = df_merge3.merge(df_area_factor_total.drop(factorNum, axis=1), 
                                     on=busAdInfo1, how='right')
    # 去除partitionCoefficient
    cols = [i for i in list(df_area_factor) if 'partitionCoefficient' not in i]
    df_area_factor = df_area_factor[cols]"""
    # 将因子转化为整数
    df_area_factor[factorNum] = df_area_factor[factorNum].astype('int')
    df_area_factor[timeCol] = periodTag
    cm.toMysql(areaFactor, df_area_factor, updateTime, exMethod)

    return df_area_factor


if __name__ == '__main__':
    manifest='原始数据/地理因子信息.xlsx'
    #regionFactor(manifest, 201712)
    exMethod = mt['exMethod']
    exMethod2 = 'append'
    areaFactorUpdate(manifest, exMethod)
    
