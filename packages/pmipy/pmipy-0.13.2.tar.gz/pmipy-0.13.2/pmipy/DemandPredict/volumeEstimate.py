# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 15:43:50 2018

@author: Administrator
"""

# import random
import numpy as np
import pandas as pd
from pmipy import log
from pmipy import pmi


try:
    config = pmi.ConfigHandler(__file__)
except NameError:
    config = pmi.ConfigHandler('calKSFshipment.py')
mt = config.read_configure('Manifest.ini', 'tag')
# 数据库或数据表名称
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
logger = log.createLogger(__name__)



fiveItem = ['容器面','高价袋','中价袋','平低价','干脆面']


# 处理尼尔森市场量得到业绩市场占比，最终将量和业绩市场占比都输入到数据表中
# 注：原表中“即食面”对应的销量数据是指所有厂商的的方便面销量之和
def marketShareAC(filePath='原始数据\各厂商规格数据(销量)-Nielsen2.xlsx', exMethod='replace'):
    df_mapAC = pd.read_excel("尼尔森scope与行销公司名称对应表.xlsx")
    df = pd.read_excel(filePath)
    ## 对空值进行填0处理
    df = df.fillna(0)
    # df_map = pd.read_excel('尼尔森scope与行销公司名称对应表.xlsx', index_col=[0])
    # df1 = pd.merge(df, df_map, left_index=True, right_index=True, how='left')
    # df.index.names = [scopeAC, channelAC]
    # df = df.reset_index()
    df1 = df[[scopeAC, channelAC, manufacturer, priceType, periodTag]]
    # periodTag<201705-201804>改为sales
    df1 = df1.rename(columns={periodTag: sale})
    # df_dupli = df1[df1.duplicated()]
    # df_dupli.to_excel('尼尔森数据重复项.xlsx', index=False)
    df2 = df1.drop_duplicates()
    # 重新求各厂商整体
    def sumPriceType(df2):
        df3 = df2[df2[priceType]!='整体']
        # 五品类整体
        df4 = df3[df3[priceType].isin(category_list1)].groupby([scopeAC, channelAC, manufacturer],as_index=False).sum()
        df4[priceType] = '整体'
        df5 = pd.concat([df3,df4])
        return df5
    df2 = sumPriceType(df2)
    # 计算尼尔森康师傅业绩市场占比
    df2 = df2.set_index([scopeAC, channelAC, priceType])
    df_ksf = df2[df2[manufacturer]=='康师傅']
    # 计算三甲总量
    df_top3 = df2[df2[manufacturer].isin(top3List)].groupby([scopeAC, channelAC, priceType]).sum()
    df_total =  df2[df2[manufacturer]=='即食面']
    # 康师傅市占
    df_ksf[[sale]] = df_ksf[[sale]] / df_total[[sale]]
    df_ksf.insert(1, typeAC, shareAC)
    # 三甲市占
    df_top3s = df_top3 / df_total[[sale]]
    df_top3s.insert(0, manufacturer, ''.join(top3List))
    df_top3s.insert(1, typeAC, shareAC)
    # 各厂商
    df2.insert(1, typeAC, capacityAC)
    df_top3[manufacturer] = ''.join(top3List)
    df_top3[typeAC] = capacityAC
    df_concat = pd.concat([df2, df_top3, df_top3s, df_ksf])
    # 添加单位
    df_concat[unit] = np.where(df_concat[typeAC]==capacityAC, '千包', None)
    df_final = df_concat.reset_index()
    df_final = df_final.merge(df_mapAC[[scopeAC,marketingCompany]], on=scopeAC,how='left')
    df_final[timeCol] = periodTag
    cm.toMysql(allManuShare, df_final, updateTime, exMethod)
    logger.info("完成各地区&厂商&品项的业绩市场占比计算！")


# 校准矩阵1--包含0.5权重的销量通路点数和0.5权重的正负因子系数bias
# 输入DataFrame需包含三甲在各商圈出货量，各商圈通路点数
def calibration_matrix1(df_top3, df_channel, df_predvsreal=[]):
    # 校准至0.7至1.2
    def ratio_calibration(x):
        # tanh函数
        tanh = lambda x: 2.0 / (1.0 + np.exp(-2*x)) - 1
        if x > 1: 
            # 控制在1.2以下
            y = 0.1 * tanh(0.5*x-0.5) + 1
        else:
            # 控制在0.6以上
            y = 0.1 * tanh(0.35*x-0.5) + 1
        return y


    ## 各商圈通路总和与销量总和的比值
    df_top3_channel = df_top3.merge(df_channel, on=[marketingCompany, salesDepartment, businessArea], how='left')
    df_top3_channel['ts1'] = df_top3_channel[factorNum] / df_top3_channel[sale]
    df_top3_channel2 = df_top3_channel.groupby(marketingCompany).sum()
    df_top3_channel2['ts2'] = df_top3_channel2[factorNum] / df_top3_channel2[sale]
    
    df_channel2 = df_top3_channel.merge(df_top3_channel2[['ts2']], left_on=marketingCompany,right_index=True)
    df_channel2['ratio'] = df_channel2['ts1'] / df_channel2['ts2']
    # df_channel2['ratio'] = df_channel2['ratio'].fillna(1)
    # df_channel2['ratio'] = df_channel2['ratio'].replace(np.inf, 1)
    df_channel2['ratio'] = df_channel2['ratio'].apply(ratio_calibration)
    df_channel2 = df_channel2[busAdInfo1+[priceType,'ratio']]
    # 对预估与实际的比值（bias）进行校准,如果为空，则只采用df_adjust1
    if len(df_predvsreal):
        df_predvsreal[predRealRatio] = df_predvsreal[predRealRatio].apply(ratio_calibration)
        df_m = df_channel2.merge(df_predvsreal,on=busAdInfo1+[priceType])
        df_m['ratio'] = df_m['ratio'] * df_m[predRealRatio]
        df_m['ratio'] = df_m['ratio'].fillna(1)
        df_m['ratio'] = df_m['ratio'].replace(np.inf, 1)
        df_cal = df_m.drop(predRealRatio, axis=1)
    else:
        df_cal = df_channel2
    # 输出各商圈因子综合影响系数和通路影响系数
    #df_adjust1.to_excel('%s各商圈正负因子综合指数.xlsx' % province)
    #df_adjust2.to_excel('%s各商圈各通路综合指数.xlsx' % province)
    # cal_mat1.to_excel('%s各商圈正负因子综合指数.xlsx' % province)
    return df_cal


# 获取尼尔森提供的三甲各品类在总方便面市场中的业绩市场占比
# foldAC为尼尔森覆盖范围的倒数;注意：尼尔森的单位是千包，需转换
def calibration_AC0(cm, foldAC=1.5): # 很多地方的平低价业绩市场占比偏高
    # 尼尔森三甲业绩市场占比
    sql_AC = "select {},{},{},{},{} from {} where {} in ('总和','全部渠道') and {}='{}'".format(scopeAC, priceType, sale,
                             manufacturer, typeAC, allManuShare, channelAC, timeCol, periodTag)
    df_AC = pd.read_sql(sql_AC, cm.engine)
    # 载入尼尔森覆盖地区与行销公司的对应表 , manufacturer, ''.join(top3List)
    df_mapAC = pd.read_excel("尼尔森scope与行销公司名称对应表.xlsx")
    df_AC = df_AC.merge(df_mapAC,on=scopeAC, how='right')
    # 总量推算，尼尔森即食面*foldAC
    df_ACtotal = df_AC[(df_AC[manufacturer]=='即食面')&(df_AC[typeAC]=='市场量')]
    df_ACtotal = df_ACtotal[[marketingCompany, priceType, sale]]
    df_ACtotal[sale] = df_ACtotal[sale] * foldAC * 1000 # 千包转化为包
    df_ACtotal.rename(columns={sale:'salesAC'}, inplace=True)
    
    # 提取三甲业绩市场占比
    df_share = df_AC[(df_AC[manufacturer]==''.join(top3List))&(df_AC[typeAC]=='市占')]
    df_share = df_share[[marketingCompany,priceType, sale]]
    df_share.rename(columns={sale:'ratio2'}, inplace=True)
    df_AC2 = df_share
    # df_AC2 = df_share.merge(df_total, on=[marketingCompany,priceType])
    
    return df_AC2, df_ACtotal

# 获取尼尔森提供的三甲整体(五品类总和)在总方便面市场中的业绩市场占比
# foldAC为尼尔森覆盖范围的倒数;注意：尼尔森的单位是千包，需转换
def calibration_AC(cm): # 不需要单独考虑平低价
    # 尼尔森三甲业绩市场占比
    sql_AC = "select {},{},{},{},{} from {} where {} in ('总和','全部渠道')  and {}='{}'".format(scopeAC, typeAC,
                     sale,manufacturer,priceType, allManuShare, channelAC,timeCol, periodTag)
    df_AC = pd.read_sql(sql_AC, cm.engine)
    # 载入尼尔森覆盖地区与行销公司的对应表 , manufacturer, ''.join(top3List)
    df_mapAC = pd.read_excel("尼尔森scope与行销公司名称对应表.xlsx")
    df_AC = df_AC.merge(df_mapAC,on=scopeAC, how='right')
    # 提取三甲业绩市场占比
    df_share = df_AC[(df_AC[manufacturer]==''.join(top3List))&(df_AC[typeAC]==shareAC)&(df_AC[priceType]=='整体')]
    df_share = df_share[[marketingCompany,sale]]
    df_share.rename(columns={sale:'ratio2'}, inplace=True)
    
    # 使用尼尔森市场量计算结构比
    df_vol = df_AC[(df_AC[manufacturer]=='即食面')&(df_AC[typeAC]==capacityAC)&(df_AC[priceType]!='整体')]
    df_vol = df_vol[[marketingCompany,priceType, sale]]
    df_vol2 = df_AC[(df_AC[manufacturer]=='即食面')&(df_AC[typeAC]==capacityAC)&(df_AC[priceType]=='整体')]
    df_vol2 = df_vol2[[marketingCompany,sale]]
    df_struct = df_vol.merge(df_vol2,on=marketingCompany)
    df_struct[sale] = df_struct[sale+'_x'] / df_struct[sale+'_y']
    df_struct = df_struct[[marketingCompany,priceType, sale]]
    # df_AC2 = df_share.merge(df_total, on=[marketingCompany,priceType])
    
    return df_share, df_struct


def multiZeroAdjust(df,df_channel,df_ACtotal,item='平低价'): # 针对平低价等品项在某些营业部大面积缺数据的item
    df1 = df[df[priceType]!=item]
    df2 = df[df[priceType]==item]
    df_ACtotal2 = df_ACtotal[df_ACtotal[priceType]==item]
    df_ACtotal2 = df_ACtotal2.drop(priceType, axis=1)
    df3 = df2.merge(df_channel,on=busAdInfo1, how='left')
    df3 = df3.merge(df_ACtotal2,on=marketingCompany, how='left')
    
    def _porc(x):
        cpx = 1 - (len(x[x[sale]==0]) / len(x)) # 计算非缺失值丰度
        if cpx == 0:
            x[sale] = 0
        else:
            x[sale] = x[sale] / x[sale].sum()
        x[factorNum] = x[factorNum] / x[factorNum].sum()
        x[sale] = x[sale] * cpx + x[factorNum] * (1-cpx)
        x[sale] = x[sale] * x['salesAC']
        return x
       
    df4 = df3.groupby(marketingCompany, as_index=False).apply(_porc)
    df4 = df4.drop([factorNum,'salesAC'], axis=1)
    df_mza = pd.concat([df1, df4])
    return df_mza


# 获取尼尔森提供的三甲在总方便面市场中的业绩市场占比
def calibration_manual(period, province):
    # 将规格别列名修改为对应年份的规格别
    df = pd.read_excel('Calibration_manual.xlsx')
    df.columns = [i+'.{}'.format(period-1) for i in df.columns]
    cal_man = df.loc[province]
    
    return cal_man


# 各商圈总方便面市场量预估
def market_total(df_top3, cal_mat1, cal_AC, cal_man=1):
    df_m1 = df_top3.merge(cal_mat1, on=busAdInfo1 + [priceType], how='inner')
    
    df_m2 = df_m1.merge(cal_AC, on=[marketingCompany, priceType], how='left')
    df_m2[sale] = df_m2[sale] * df_m2['ratio'] / df_m2['ratio2']
    df_total = df_m2[busAdInfo1 + [priceType, sale]]
    # df_total = df_total.drop_duplicates()
    # df_total.to_excel('第一版结果.xlsx')
    return df_total


# 将包转--箱转化:默认为包转箱
def UnitTransform(df, box=True):
    if box:
        df = df[df[priceType]!='整体']
        df[sale] = np.where(df[priceType].str.contains('容器'), df[sale]/12, df[sale]/24)
        df[sale] = df[sale].astype('int')
        # 求规格别总和
        df_zt = df[df[priceType].isin(category_list1)].groupby(busAdInfo2+[typeAC], as_index=False).sum()
        df_zt[priceType] = '整体'
        df = pd.concat([df,df_zt])
        df[unit] = '箱'
        
    else:
        # 将箱转化为包:容器面转化系数为12，其他规格的面为24
        df = df[df[priceType]!='整体']
        df[sale] = np.where(df[priceType].str.contains('容器'), df[sale]*12, df[sale]*24)
        df[unit] = '包'
    return df


# 求人均包
def PerCapitaPackage(df_pack, df_pop):
    df_pack = df_pack[df_pack[unit]=='包']
    df_pack = df_pack.merge(df_pop, on=busAdInfo2, how='left')
    df_pack[sale] = df_pack[sale] / df_pack[factorNum]
    df_per = df_pack.drop(factorNum, axis=1)
    df_per['type'] = '人均包'
    df_per[unit] = '包/人'
    return df_per

# 与1516拆分表比较，降幅为0.8左右可接受
def ajustBigScope(df_ksf3, df_total3, df_pop, scope, tag, manu=False, flucThreshold=0.8): 
    if manu:
        df_ratio4 = pd.read_excel('产出数据/%s各%s各品类ratio_%s.xlsx' % (tag, scope,periodTag),index_col=0)
        df_ratio5 = df_ratio4.stack().reset_index()
        df_ratio5.columns = [scope, priceType, 'ratio']
        return df_ratio5
        
    df_sbs = df_ksf3.merge(df_total3,on=busAdInfo2+[priceType,unit],how='left')
    df_sbs = df_sbs.dropna()
    # 计算业绩市场占比
    df_sbs2 = df_sbs.groupby([scope, priceType, unit]).sum()
    df_sbs2['业绩市场占比'] = df_sbs2[sale+'_x'] / df_sbs2[sale+'_y']
    df_sbs3 = pd.pivot_table(df_sbs2, index=scope, columns=[unit,priceType], values=['业绩市场占比'])
    df_sbs3.to_excel('产出数据/%s各%s业绩市场占比_%s.xlsx' % (tag, scope,periodTag))

    # 计算人均包
    df_sbsPack = df_total3[df_total3[unit]=='包']
    df_sbsPack2 = df_sbsPack.merge(df_pop, on=busAdInfo2, how='left')
    df_sbsPack2 = df_sbsPack2.dropna()
    df_sbsPer = df_sbsPack2.groupby([scope,priceType], as_index=False).sum()
    df_sbsPer.to_excel('产出数据/%s各%s总包数_%s.xlsx' % (tag, scope,periodTag))
    df_sbsPer['人均包'] = df_sbsPer[sale] / df_sbsPer[factorNum]
    df_sbsPer2 = pd.pivot_table(df_sbsPer, index=scope, columns=[priceType], values=['人均包'])
    df_sbsPer3 = df_sbsPer2['人均包']
    df_sbsPer3.to_excel('产出数据/%s各%s人均包_%s.xlsx' % (tag, scope,periodTag))
    """# 计算业绩市场占比
    df_sbs = df_ksf3s / df_total3s
    df_sbs2 = pd.pivot_table(df_sbs, index=scope, columns=[priceType], values=[sale])"""
    # 与1516拆分表中的五品类人均包进行对比
    df1516 = pd.read_excel('原始数据/1516拆分表人均包.xlsx', index_col=0)
    # 暂时只比较总市场的人均包
    df1516t = df1516[[i for i in list(df1516) if '市场量' in i]]
    newCol = [i[:-6] for i in list(df1516t)]
    df1516t.columns = newCol
    df1516t.rename(columns={'整体': '整体','中价面':'中价袋'}, inplace=True)
    df_ratio = df_sbsPer3 / df1516t
    df_ratio = df_ratio.dropna(how='all', axis=1)
    # 以0.8为门槛
    df_ratio = flucThreshold / df_ratio
    df_ratio3 = df_ratio.applymap(lambda x: 1 + 0.5 * (x-1))
    # 乘以随机数,弃用
    # df_ratio3 = df_ratio2.applymap(lambda x: x * random.uniform(0.95,1))
    df_ratio3[df_ratio3['整体']<1.05] = 1
    df_ratio4 = df_ratio3.applymap(lambda x: 1 if x<1.05 else x)
    for col in list(df_sbsPer3):
        if col not in list(df_ratio4):
            df_ratio4[col] = 1
    df_ratio4.to_excel('产出数据/%s各%s各品类ratio_%s.xlsx' % (tag, scope,periodTag))
    df_ratio5 = df_ratio4.stack().reset_index()
    df_ratio5.columns = [scope, priceType, 'ratio']
    return df_ratio5


def market_estimate(cm, associationAnnouncement, exMethod='fail'):
    # 获取康师傅指定年份的出货/销量数据,单位为包
    sql_ksf = "select {},{},{},{},{},{} from {} where {}='TT+MT' and {}='KSF' and {}='{}'".format(marketingCompany, 
                      salesDepartment, businessArea, priceType, sale, unit, ksfSales, channel,
                      manufacturer, timeCol, periodTag)
    df_ksf0 = pd.read_sql(sql_ksf, cm.engine)
    # 去除出货量中的整体
    df_ksf0 = df_ksf0[df_ksf0[priceType]!='整体']
    
    # df_ksfb = df_ksf0[df_ksf0[unit]=='箱'] # 单位为箱
    # df_ksf = df_ksf.drop(unit, axis=1)
    # df_ksf = df_ksfb.drop(unit, axis=1)
    
    # 三甲指定年份的出货/销量数据
    sql_top3 = "select {},{},{},{},{} from {} where {}='{}' and {}='包' and {}='{}'".format(marketingCompany, salesDepartment,
                       businessArea, priceType, sale, ksfSales, manufacturer, ''.join(top3ListEN), unit, timeCol, periodTag)
    df_top3 = pd.read_sql(sql_top3, cm.engine)
    
    # 获取商圈行销公司信息
    sql_info = "select {},{},{},{},{} from {} where {}='{}'".format(marketingCompany, province, salesDepartment, 
                       city, businessArea, infoName, timeCol, periodTag)
    df_info = pd.read_sql(sql_info, cm.engine)

    # 获取预估与实际比值数据
    sql_predvsreal = "select {},{},{},{},{} from {} where {}='{}'".format(marketingCompany, salesDepartment, 
                             businessArea, priceType, predRealRatio, predVsReal, timeCol, periodTag)
    df_predvsreal = pd.read_sql(sql_predvsreal, cm.engine)
    
    # 获取通路点数数据
    sql_factor = "select {},{},{},{},{} from {} where {}='{}'".format(marketingCompany, salesDepartment, 
                          businessArea, factorType, factorNum, areaFactor, timeCol, periodTag)
    df_factor = pd.read_sql(sql_factor, cm.engine)
    df_channel = df_factor[df_factor[factorType].isin(channelList)]
    df_channel = df_channel.groupby(busAdInfo1, as_index=False).sum()
    
    # 获取各商圈人口数据
    df_pop = df_factor[df_factor[factorType]=='人口'].drop(factorType, axis=1)

    # 获取校准系数矩阵1
    cal_mat1 = calibration_matrix1(df_top3, df_channel, df_predvsreal)
    
    ## 针对个别特殊商圈进行人工修改校准矩阵
    def cal_manu(cal_mat1, filePath='原始数据/someBusManu.xlsx'):
        df_adj = pd.read_excel(filePath, index_col=[0,1,2])
        df_adj = df_adj.stack().reset_index()
        df_adj = df_adj.rename(columns={'level_3':priceType, 0:'ratio2'})
        df_merge = cal_mat1.merge(df_adj, on=busAdInfo1+[priceType], how='left')
        df_merge.loc[df_merge['ratio2'].notnull(),'ratio'] = df_merge['ratio'] * df_merge['ratio2']
        df_merge = df_merge.drop('ratio2', axis=1)
        return df_merge
    cal_mat1 = cal_manu(cal_mat1)
    
    def calTotalMarket0(df_top3, cal_mat1):
        # 获取三甲厂商各规格占总市场各规格的比例
        cal_AC, df_ACtotal = calibration_AC0(cm)
        # 获取经验人工校准数据
        # cal_man = calibration_manual(period, province)
        # 预估各规格总市场量（潜力市场量）
        df_total = market_total(df_top3, cal_mat1, cal_AC)
        
        # 含修正平低价面
        df_total = multiZeroAdjust(df_total,df_channel,df_ACtotal)
        return df_total
    
    # 计算各商圈整体的总市场量（潜力市场量）
    def calTotalMarket(df_top3, cal_mat1):
        df_share, df_struct = calibration_AC(cm) # 获取三甲整体市占和即食面结构比
        df_m1 = df_top3.merge(cal_mat1, on=busAdInfo1 + [marketingCompany,priceType], how='inner')
        df_m2 = df_m1.merge(df_share, on=[marketingCompany], how='left')
        df_m2[sale] = df_m2[sale] * df_m2['ratio'] / df_m2['ratio2']
        df_total = df_m2[busAdInfo1 + [priceType, sale]]
        df_tp = df_total[df_total[priceType].isin(category_list1)].groupby([marketingCompany],as_index=False).sum()
        # df_total = df_total.drop_duplicates()
        return df_tp
    
    # 总市场量（潜力市场量）-包预测
    df_total = calTotalMarket0(df_top3, cal_mat1)
    
    # 地方认可尼尔森结构占比：在尼尔森结构占比基础上再适当提高高端、高价袋和容器面，适当降低中价平低价和干脆面
    def adjustReferstructAC(df_total):
        df_share, df_struct = calibration_AC(cm) # 获取三甲整体市占和即食面结构比
        # 各行销公司结构占比调整数据
        df_adj = pd.read_excel('原始数据/各行销公司结构占比调整.xlsx', index_col=0)
        df_adj = df_adj.stack().reset_index()
        df_adj = df_adj.rename(columns={'level_1':priceType, 0:'adj'})
        df_struct = df_struct.merge(df_adj, on=[marketingCompany,priceType])
        df_struct[sale] = df_struct[sale] + df_struct['adj']
        df_struct = df_struct.drop('adj', axis=1)
        
        df_tp = df_total[df_total[priceType].isin(category_list1)].groupby(marketingCompany,as_index=False).sum()
        df_tp2 = df_total.groupby([marketingCompany,priceType],as_index=False).sum()
        df_tv = df_struct.merge(df_tp, on=marketingCompany)
        df_tv[sale] = df_tv[sale+'_x'] * df_tv[sale+'_y']
        df_tv = df_tv[[marketingCompany,priceType, sale]]
        df_ratio = df_tp2.merge(df_tv, on=[marketingCompany,priceType])
        df_ratio['ratio'] = df_ratio[sale+'_y'] / df_ratio[sale+'_x']
        # 如果高端小于1，则修正为1
        df_ratio.loc[(df_ratio[priceType].str.contains('高端'))&(df_ratio['ratio']<1),'ratio'] = 1

        
        df_totals = df_total.merge(df_ratio, on=[marketingCompany,priceType])
        df_totals[sale] = df_totals[sale] * df_totals['ratio']
        df_totals = df_totals[list(df_total)]
        return df_totals
    df_total = adjustReferstructAC(df_total)
    
    # 总市场量（潜力市场量）-包
    df_total['type'] = '总市场量（潜力市场量）'
    df_total[unit] = '包'
    # 准备计算五品类
    ## 康师傅级别
    # 转化为整数
    df_ksf0[sale] = df_ksf0[sale].fillna(0).astype('int')
    df_ksf0f = df_ksf0[df_ksf0[priceType].isin(category_list1)]
    df_ksf0f2 = df_ksf0f.groupby(busAdInfo1+[unit],as_index=False).sum()
    df_ksf0f2[priceType] = '整体'
    df_ksf3 = pd.concat([df_ksf0, df_ksf0f2])
    df_ksf3['type'] = 'KSF实际销量'


    
    ## 总市场量（潜力市场量）级别
    df_total2f = df_total[df_total[priceType].isin(category_list1)]
    df_total2f2 = df_total2f.groupby(busAdInfo1+['type',unit], as_index=False).sum()
    df_total2f2[priceType] = '整体'
    df_total3 = pd.concat([df_total, df_total2f2])
    
    # 进入最终校准阶段：计算各省或行销公司scope各指标
    scope = province
    # 给df_ksf3, df_total3, df_pop添加省份信息
    df_info2 = df_info.drop('city', axis=1) # 去除city
    df_info2 = df_info2.drop_duplicates()
    df_ksf3 = df_ksf3.merge(df_info2, on=busAdInfo1, how='left')
    df_total3 = df_total3.merge(df_info2, on=busAdInfo1, how='left')
    df_pop = df_pop.merge(df_info2, on=busAdInfo1, how='left')
    

    df_total4 = df_total3
    # df_ratio = ajustBigScope(df_ksf3, df_total3, df_pop, scope, '校准前', True)
    # df_total4 = df_total3.merge(df_ratio, on=[scope, priceType])
    # df_total4[sale] = df_total4[sale] * df_total4['ratio']
    # df_total4 = df_total4.drop('ratio', axis=1)
    # 准备控制五品类总量,计算各省五品类的总包数
    df_total5 = df_total4[df_total4[priceType].isin(category_list1)]
    df_total5 = df_total5.groupby(scope).sum()
    df_total6 = df_total4[df_total4[priceType]=='整体'].groupby(scope).sum()
    df_aj = df_total6 / df_total5
    df_aj.columns = ['adjust']
    df_total7 = df_total4.merge(df_aj, left_on=scope, right_index=True, how='left')
    df_total7.loc[df_total7[priceType]!='整体', sale] = df_total7[sale] * df_total7['adjust']
    df_total4 = df_total7.drop('adjust', axis=1)
    
    # ajustBigScope(df_ksf3, df_total4, df_pop, scope, '校准后')
    def association(df_total4,prov='河南省'):
        df_total5 = df_total4[df_total4[unit]=='包']
        df_total6 = df_total4[df_total4[priceType] != '整体']
        
        df_total5r = df_total5[df_total5[priceType]=='容器面']  # 容器面
        df_total5d = df_total5[df_total5[priceType].isin(packetNoodle_list)] # 袋面
        rqCoef = associationAnnouncement['容器面']*10**8/df_total5r[sale].sum()
        dmCoef = associationAnnouncement['袋面']*10**8/df_total5d[sale].sum()
        logger.info("协会公告的容器面市场量与推估容器面市场量的比值%s" % rqCoef)
        logger.info("协会公告的袋面市场量与推估袋面市场量的比值%s" % dmCoef)
        df_total6[sale] = np.where(df_total6[priceType].str.contains('容器'),df_total6[sale] * rqCoef, df_total6[sale] * dmCoef)
        
        # 单独调整河南行销公司
        # ['新乡部','济源市']  ['安阳部','濮阳县'] ['洛阳部','吉利区']
        # df_total6[sale] = np.where((df_total6[province]==prov)&(df_total6[priceType]!='干脆面'),df_total6[sale]*0.9,df_total6[sale])
        # df_total6.loc[(df_total6[province]==prov)&(df_total6[priceType]!='干脆面'), sale] = df_total6[sale]*0.91
        df_total6.loc[(df_total6[province]==prov)&(df_total6[priceType]=='平低价')&(df_total6[businessArea].isin(['济源市',
                      '濮阳县','吉利区'])), sale] = df_total6[sale]*0.3
                
        # 计算整体
        df_total6[sale] = df_total6[sale].fillna(0).astype('int')
        df_total7 = df_total6[df_total6[priceType].isin(category_list1)].groupby(busAdInfo2+[unit, typeAC], as_index=False).sum()
        df_total7[priceType] = '整体'
        df_total8 = pd.concat([df_total6, df_total7])
        return df_total8

    # 对各省整体进行校准
    def provTotalAdjust(df_total4, filePath='原始数据/各省整体校准系数.xlsx'):
        df = pd.read_excel(filePath)[['province','ratio']]
        df_total5 = df_total4.merge(df, on=province,how='left')
        df_total5[sale] = df_total5[sale] * df_total5['ratio']
        df_total5 = df_total5.drop('ratio', axis=1)
        return df_total5
    
    df_total4 = provTotalAdjust(df_total4)
    
    # 使用协会公告的数据进行调整
    df_total4 = association(df_total4)
    

    # 人均包
    df_total4b = df_total4[df_total4[unit]=='包']
    df_per = PerCapitaPackage(df_total4b, df_pop)
    df_per[manufacturer] = '总市场量'
    df_ksfPer = PerCapitaPackage(df_ksf3, df_pop)
    df_ksfPer[manufacturer] = 'KSF'

    # 总市场量（潜力市场量）-箱
    df_total4b = UnitTransform(df_total4)
    
    # 合并包，箱
    df_total4 = pd.concat([df_total4, df_total4b])
    
    # 计算各商圈业绩市场占比
    df_ksfshare = df_ksf3.merge(df_total4,on=busAdInfo2+[priceType,unit])
    df_ksfshare[sale] = df_ksfshare[sale+'_x'] / df_ksfshare[sale+'_y']
    df_ksfshare.drop([sale+'_x', sale+'_y'], axis=1, inplace=True)
    df_ksfshare.drop([typeAC+'_x',typeAC+'_y'], axis=1, inplace=True)
    df_ksfshare[typeAC] = '业绩市场占比'
    df_ksfshare[unit] = np.where(df_ksfshare[unit]=='箱', '箱/箱', '包/包')
    df_total4[manufacturer] = '总市场量'
    df_ksfshare[manufacturer] = 'KSF'
    df_ksf3[manufacturer] = 'KSF'
    df_final = pd.concat([df_total4, df_ksfshare, df_ksf3, df_per, df_ksfPer])
    df_final = df_final.replace(np.inf, np.nan)
    
    
    # 数据格式转换并导出excel提供给客户
    def provideForCustomer(df_final):
        header = ['整体','高端容器','高端袋','容器面','高价袋','中价袋','平低价','干脆面']
        
        df_excel = pd.pivot_table(df_final, index=busAdInfo2, 
                                  columns=[typeAC,manufacturer,unit,priceType], values=[sale])
        df_excel = df_excel[sale]
        
        # 人均包
        df_per = df_excel['人均包']['总市场量'] 
        df_per.rename(columns={'包/人':'总市场量人均包'}, inplace=True)
        
        # 总市场量（潜力市场量）
        df_total = df_excel['总市场量（潜力市场量）']['总市场量']
        df_total = df_total / 1000
        df_total.rename(columns={'包':'总市场量（潜力市场量）_千包','箱':'总市场量（潜力市场量）_千箱'}, inplace=True)
        
        # 康师傅实际销量
        df_ksf = df_excel['KSF实际销量']['KSF']
        # 转化为千箱或千包
        df_ksf = df_ksf / 1000
        df_ksf.rename(columns={'包':'KSF实际销量_千包','箱':'KSF实际销量_千箱'}, inplace=True)

        # 康师傅业绩市场占比
        df_prop = df_excel['业绩市场占比']['KSF']  
        df_prop.rename(columns={'包/包':'KSF业绩市场占比_千包','箱/箱':'KSF业绩市场占比_千箱'}, inplace=True)
        
        df_concat = pd.concat([df_per, df_total, df_ksf, df_prop], axis=1)
        # 暂时无能为力，改变列名
        col = ['_'.join(i) for i in list(df_concat)]
        df_concat.columns = col
        h1 = ['总市场量人均包_'+i for i in header]
        h2 = ['总市场量（潜力市场量）_千包_'+i for i in header]
        h3 = ['总市场量（潜力市场量）_千箱_'+i for i in header]
        h4 = ['KSF实际销量_千包_'+i for i in header]
        h5 = ['KSF实际销量_千箱_'+i for i in header]
        h6 = ['KSF业绩市场占比_千包_'+i for i in header]
        h7 = ['KSF业绩市场占比_千箱_'+i for i in header]
        
        df_concat = df_concat[h1+h2+h3+h4+h5+h6+h7]
        df_pop2 = df_pop.set_index(busAdInfo2) / 10000
        df_pop2.columns = ['人口（万人）']
        df_f = df_pop2.merge(df_concat, left_index=True,right_index=True)
        
        return df_f
    

    def byprovince():
        df_prov_pop = df_excel.groupby(province).sum()
        # 加入全国
        df_prov_pop.loc['全国'] = df_prov_pop.sum()
        col_total1 = [i for i in list(df_excel) if '总市场量（潜力市场量）_千包_' in i]
        col_ksf1 = [i for i in list(df_excel) if 'KSF实际销量_千包_' in i]
        col_total2 = [i for i in list(df_excel) if '总市场量（潜力市场量）_千箱_' in i]
        col_ksf2 = [i for i in list(df_excel) if 'KSF实际销量_千箱_' in i]
        col_share1 = [i for i in list(df_excel) if 'KSF业绩市场占比_千包_' in i]
        col_share2 = [i for i in list(df_excel) if 'KSF业绩市场占比_千箱_' in i]
        col_tp = [i for i in list(df_excel) if '总市场量人均包_' in i]
        # col_kp = [i for i in list(df_excel) if '人均包_KSF_包/人_' in i]
        df_t1 = df_prov_pop[col_total1]
        df_k1 = df_prov_pop[col_ksf1]
        df_t2 = df_prov_pop[col_total2]
        df_k2 = df_prov_pop[col_ksf2]
        df_sh1 = pd.DataFrame(np.divide(np.mat(df_k1),np.mat(df_t1)),columns=col_share1,index=df_k1.index) # 业绩市场占比
        df_sh2 = pd.DataFrame(np.divide(np.mat(df_k2),np.mat(df_t2)),columns=col_share2,index=df_k2.index)
        df_tp = df_t1.apply(lambda x: x * 0.1/df_prov_pop['人口（万人）'])
        df_tp.columns = col_tp
        #df_kp = df_k.apply(lambda x: x/df_prov_pop['人口（万人）'])
        #df_kp.columns = col_kp
        df_fi = pd.concat([df_tp,df_t1,df_k1,df_t2,df_k2,df_sh1,df_sh2], axis=1)
        #df_fi.loc['全国'] = df_fi.sum()
        df_fi.to_excel('产出数据/全国商圈分级--{}市场量推算--by省.xlsx'.format(periodTag),merge_cells=False)
        
    df_excel = provideForCustomer(df_final)
    df_excel2 = df_excel[(df_excel['KSF实际销量_千箱_整体']==0)|(df_excel['KSF实际销量_千箱_整体'].isnull())]

    df_excel.to_excel('产出数据/全国商圈分级--{}市场量推算.xlsx'.format(periodTag),merge_cells=False)
    df_excel2.to_excel('产出数据/全国商圈分级--{}市场量推算--数据缺失的商圈.xlsx'.format(periodTag),merge_cells=False)
    byprovince()
    """
    # 添加等级信息
    import grading as gd
    
    df_vol = df_final[(df_final[typeAC].isin(['总市场量（潜力市场量）','人均包']))&(df_final[manufacturer]=='总市场量')]
    df_vol = df_vol[busAdInfo1+[priceType, sale, unit]]
    
    # 按原规则
    df_gd, df_m = gd.adjust(gd.VPT_ori, df_vol)
    df_gd2 = df_gd[busAdInfo1+['建议等级']]
    df_final2 = df_final.merge(df_gd2, on=busAdInfo1)
    df_final2 = df_final2.rename(columns={'建议等级':'business_level'})
    # 文件输出
    writer = pd.ExcelWriter('产出数据/各商圈分级建议%s_原分级规则.xlsx'%periodTag)
    df_gd.to_excel(writer, '分级建议', index=False)
    df_m.to_excel(writer, '变化')
    writer.save()
    
    df_gd, df_m = gd.adjust(gd.VPT2, df_vol)
    df_gd2 = df_gd[busAdInfo1+['建议等级']]
    df_final2 = df_final.merge(df_gd2, on=busAdInfo1)
    df_final2 = df_final2.rename(columns={'建议等级':'business_level'})

        
    # 文件输出
    writer = pd.ExcelWriter('产出数据/各商圈分级建议%s.xlsx'%periodTag)
    df_gd.to_excel(writer, '分级建议', index=False)
    df_m.to_excel(writer, '变化')
    writer.save()
    """
    # 添加市场潜力大小的标签
    
    #总市场量前50% 潜力大 后50%潜力低(sale中的type=总市场量（潜力市场量）)
    #根据康师傅自己的市场量 前50% 销量高 后50%销量低(sale中的type=KSF实际销量)
    
    def addPotentialTag(df_final):
        df1 = df_final[(df_final[priceType]=='整体')&(df_final[manufacturer]=='总市场量')&
                        (df_final[typeAC]=='总市场量（潜力市场量）')&(df_final[unit]=='包')]
        df2 = df_final[(df_final[priceType]=='整体')&(df_final[manufacturer]=='KSF')&
                        (df_final[typeAC]=='KSF实际销量')&(df_final[unit]=='包')]
        df1[potential] = np.where(df1[sale]>df1[sale].median(),'潜力大', '潜力小')
        df2['sl'] = np.where(df2[sale]>df2[sale].median(),'销量高', '销量低')
        df1 = df1[busAdInfo1+[potential]]
        df2 = df2[busAdInfo1+['sl']]
        df3 = df1.merge(df2, on=busAdInfo1)
        df3[potential] = df3[potential] + df3['sl']
        df4 = df3.drop('sl', axis=1)
        df_final3 = df_final.merge(df4, on=busAdInfo1,how='left')
        return df_final3
    # 上传至数据库
    df_final2 = addPotentialTag(df_final)
    df_final2[timeCol] = periodTag
    #cm.toMysql(marketVolume, df_final2, updateTime, exMethod)
    
    return df_final2


def finalVerify():
    df1 = pd.read_excel('原始数据/1516商圈分级各省总市场量（潜力市场量）和KSF实际销量(包).xlsx', index_col=0)
    """
    df2 = pd.read_excel('产出数据/校准前各province人均包_1705-1804.xlsx', index_col=0)
    df2 = df2.apply(lambda x: x / df2['整体'])
    df2[fiveItem].to_excel('结果校验/参考1516之前推估市场量得到的结构比.xlsx')
    df_ts2 = df2 / df1516t2
    df_ts2[fiveItem].to_excel('结果校验/1516校验前推估与1516占比.xlsx')
    """
    #colT = [i for i in list(df1516) if '市场量' in i]
    #df1516t = df1516[colT]
    #df1516t = df1516t
    df1s = df1.apply(lambda x: x / df1['整体'])
    df1s.to_excel('结果校验/1516商圈分级各品类与整体的占比.xlsx')
    # 加载计算得到的各省各品类人均包
    df_cal = pd.read_excel('产出数据/全国商圈分级--1705-1804市场量推算--by省.xlsx', index_col=0)
    colT2 = [i for i in list(df_cal) if '人均包_总市场量（潜力市场量）' in i]
    df_calT = df_cal[colT2]
    df_calT2 = df_calT.apply(lambda x: x / df_calT['人均包_总市场量（潜力市场量）_包/人_整体'])
    df_calT2.columns = [i.split('_')[-1] for i in list(df_calT2)]
    df_calT2 = df_calT2[fiveItem]
    df_calT2.to_excel('结果校验/推估得到各品类与整体的占比.xlsx')
    df_ts = df_calT2 / df1s
    df_ts[fiveItem].to_excel('结果校验/推估与1516占比.xlsx')
    # df1516t.rename(columns={'整体': '整体','中价面':'中价袋'}, inplace=True)


if __name__ == '__main__':
    cm = pmi.ConnMysql(dbName)
    exMethod = mt['exMethod']
    associationAnnouncement = {'容器面':109.3, '袋面':272.1}
    #cm = pmi.ConnMysql(dbName)
    exMethod2 = 'replace'
    #marketShareAC(exMethod=exMethod)
    market_estimate(cm, exMethod2, associationAnnouncement)


####################补充说明############################
## tanh曲线的绘制方法：
"""
import matplotlib.pyplot as plt  
import matplotlib as mpl  
mpl.rcParams['axes.unicode_minus']=False 
fig = plt.figure(figsize=(6,4))
ax = fig.add_subplot(111)  
  
x = np.linspace(-10, 10)  
tanh = lambda x: 2.0 / (1.0 + np.exp(-2*x)) - 1    
  
plt.xlim(-11,11)  
plt.ylim(-1.1,1.1)  
  
ax.spines['top'].set_color('none')  
ax.spines['right'].set_color('none')  
  
ax.xaxis.set_ticks_position('bottom')  
ax.spines['bottom'].set_position(('data',0))  
ax.set_xticks([-10,-5,0,5,10])  
ax.yaxis.set_ticks_position('left')  
ax.spines['left'].set_position(('data',0))  
ax.set_yticks([-1,-0.5,0.5,1])  
yValue = 0.5 * tanh(0.35*x)  
plt.plot(2*x,yValue,label="Tanh", color = "red")  
plt.legend()
plt.show()
"""

