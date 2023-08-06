# -*- coding: utf-8 -*-
"""
Created on Tue May 29 22:02:27 2018

@author: Administrator
"""

import codecs
import grading
import pandas as pd
import volumeEstimate
from pmipy import log
from pmipy import pmi
from configparser import ConfigParser

fp = 'Manifest.ini'
try:
    config = pmi.ConfigHandler(__file__)
except NameError:
    config = pmi.ConfigHandler('calKSFshipment.py')
mt = config.read_configure(fp, 'tag')
dbName = mt['dbName']
ksfSales = mt['ksfSales']
tyjmlSales = mt['tyjmlSales']
infoName = mt['infoName']
regionFactor = mt['regionFactor']
areaFactor = mt['areaFactor']
predVsReal = mt['predVsReal']
allManuShare = mt['allManuShare']
marketVolume = mt['marketVolume']

factorTime = mt['factorTime']
province = mt['province']
city = mt['city']
region = mt['region']
businessArea = mt['businessArea']
partitionName = mt['partitionName']
priceType = mt['priceType']
sale = mt['sale']
unit = mt['unit']
channel = mt['channel']
factorType = mt['factorType']
factorNum = mt['factorNum']
timeCol = mt['timeCol']
marketingCompany = mt['marketingCompany']
salesDepartment = mt['salesDepartment']
manufacturer = mt['manufacturer']
predRealRatio = mt['predRealRatio']
scopeAC = mt['scopeAC']
channelAC = mt['channelAC']
typeAC = mt['typeAC']
potential = mt['potential']
shareAC = mt['shareAC']
capacityAC = mt['capacityAC']
ksfShareAC = mt['ksfShareAC']
top3ShareAC = mt['top3ShareAC']
category_list1 = eval(mt['category_list1'])
packetNoodle_list = eval(mt['packetNoodle_list'])
top3List = eval(mt['top3List'])
top3ListEN = eval(mt['top3ListEN'])
channelList = eval(mt['channelList'])
# 区分不同商圈商圈名相同的额外信息
busAdInfo1 = [marketingCompany, salesDepartment, businessArea]
busAdInfo2 = [marketingCompany, province, salesDepartment, businessArea]
# 内容
updateTime = mt['updateTime']
periodTag = mt['periodTag'] # 1705-1804

cm = pmi.ConnMysql(dbName)
exMethod = mt['exMethod']
associationAnnouncement = {'容器面':109.3, '袋面':272.1} # wina
logger = log.createLogger(__name__)

def updateConf(periodTag):
    conf = ConfigParser()   #实例化
    conf.read_file(codecs.open(fp,'r'))     # 打开conf
    conf.set('tag', 'periodTag', periodTag)
    conf.set('tag', 'exMethod', exMethod)
    fh = open(fp ,'w')
    conf.write(fh)#把要修改的节点的内容写到文件中
    fh.close()
    
    #os.system('python updateFactor.py')
    #os.system('python machineLearning.py')



def structRatio(filePath1, filePath2, periodTag):
    # 标准列名顺序
    colSt = ['高端容器','高端袋','容器面','高价袋','中价袋','平低价','干脆面']
    colSt2 = ['整体'] + colSt
    df1 = pd.read_excel(filePath1, index_col=0,header=[0,1],sheetname='结构占比')
    # 读取市占模板
    df1_sz = pd.read_excel(filePath1, index_col=0,header=[0,1],sheetname='市占')
    
    # 读取推估得到的数据
    df2 = pd.read_excel(filePath2, index_col=0)
    df2_jg = df2[[i for i in list(df2) if '总市场量（潜力市场量）_千包_' in i]]
    df2_jg.columns = [i.split('_')[-1] for i in list(df2_jg)]
    df2_jg = df2_jg.rename(columns={'五品类整体':'整体'})
    # 计算结构占比
    df2_jg2 = df2_jg.apply(lambda x: x / df2_jg['整体'])
    df2_jg2 = df2_jg2[colSt]
    df1['推估版结构占比'] = df2_jg2
    df1['推估版总市场结构占比与即食面结构占比的比值'] = df1['推估版结构占比'] / df1['即食面结构占比']
    df1['推估版总市场结构占比与康师傅出货(业绩表数据)结构占比的比值'] = df1['推估版结构占比']/df1['康师傅出货(业绩表数据)结构占比']
    
    # 读取并计算市占比值
    df2_sz = df2[[i for i in list(df2) if 'KSF业绩市场占比_千箱_' in i]]
    df2_sz.columns = [i.split('_')[-1] for i in list(df2_jg)]
    df2_sz = df2_sz.rename(columns={'五品类整体':'整体'})
    df2_sz2 = df2_sz[colSt2]
    df1_sz['推估版KSF市占'] = df2_sz2
    df1_sz['推估版KSF市占与尼尔森KSF市占的比值'] = df2_sz2 / df1_sz['尼尔森KSF市占']
    col_temp = list(df1_sz['1516地方版商圈分级市占'])
    df1_sz['推估版KSF市占与1516地方版商圈分级市占的比值'] = df2_sz2[col_temp] / df1_sz['1516地方版商圈分级市占']
    df1_sz['推估版KSF市占与三甲KSF市占的比值'] = df2_sz2 / df1_sz['KSF三甲中的占比']
    
    writer = pd.ExcelWriter('产出数据\结构占比和市占分析_%s.xlsx' % periodTag)
    df1.to_excel(writer, '结构占比')
    df1_sz.to_excel(writer, '市占')
    

def run(periodTag, exMethod):
    df_vol = volumeEstimate.market_estimate(cm, associationAnnouncement)
    df_vol2 = df_vol[(df_vol[typeAC].isin(['总市场量（潜力市场量）','人均包']))&(df_vol[manufacturer]=='总市场量')]
    df_vol2 = df_vol2[busAdInfo1+[priceType, sale, unit]]
    
    # 结构验证
    filePath1 = '原始数据/结构占比和市占分析-模板.xlsx'
    filePath2 = '产出数据/全国商圈分级--%s市场量推算--by省.xlsx'%periodTag
    structRatio(filePath1, filePath2, periodTag)
     
     # 2018年分级标准
    VPT = {
           '总市场量1':180,'高价面人均包1':20,'人口1':50,
           '总市场量2':100,'高价面人均包2':13,'人口2':0,'通路点数2':750,
           '总市场量3':60,'高价面人均包3':8,'人口3':40,
           '总市场量4':50,'高价面人均包4':0,'人口4':0,
           '总市场量5':30,'高价面人均包5':0,'人口5':0,
           }
    
    # 不考虑直营二阶
    grading.grading2(VPT, False, df_vol2)
    # 考虑直营二阶
    df_grade = grading.grading2(VPT, True, df_vol2)
    df_grade2 = df_grade[busAdInfo1+['建议等级']]
    df_grade2 = df_grade2.rename(columns={'建议等级':'business_level'})
    # 导入至market_volume数据表中的最终版
    df_final = df_vol.merge(df_grade2, on=busAdInfo1, how='left')
    cm.toMysql(marketVolume, df_final, updateTime, exMethod)
    
if __name__ == '__main__':
    run(periodTag, exMethod='replace')
    




