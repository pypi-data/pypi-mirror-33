# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 15:26:51 2018

@author: Administrator
"""

import numpy as np
import pandas as pd
from pmipy import log
from pmipy import pmi


logger = log.createLogger(__name__)
try:
    config = pmi.ConfigHandler(__file__)
except NameError:
    config = pmi.ConfigHandler('calShipment.py')
mt = config.read_configure('Manifest.ini', 'tag')
# 数据库或数据表名称
dbName = mt['dbName']
areaFactor = mt['areaFactor']
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
shareAC = mt['shareAC']
capacityAC = mt['capacityAC']
ksfShareAC = mt['ksfShareAC']
top3ShareAC = mt['top3ShareAC']
category_list1 = eval(mt['category_list1'])
top3List = eval(mt['top3List'])
top3ListEN = eval(mt['top3ListEN'])
channelList = eval(mt['channelList'])
bigbusiness = mt['bigbusiness']
smallbusiness = mt['smallbusiness']
infoName = mt['infoName']

# 区分不同商圈商圈名相同的额外信息
busAdInfo1 = [marketingCompany, salesDepartment, businessArea]
# 内容
updateTime = mt['updateTime']
periodTag = mt['periodTag']


cm = pmi.ConnMysql(dbName)

filePath = '原始数据/全国各商圈客户形态等级信息.xlsx'
# 考虑的通路点数
channelList = ["中学","加油加气站","小学","成人教育","火车站","网吧","超市","酒店","长途汽车站","高等院校",""]

# 加载通路点数和人口数据
def getData(df_vol=''):
    # 加载因子
    sql_factor = "select {},{},{},{},{} from {} where {}='{}'".format(marketingCompany, salesDepartment, 
                          businessArea, factorType, factorNum, areaFactor, timeCol, periodTag)
    df_factor = pd.read_sql(sql_factor, cm.engine)
    if not isinstance(df_vol, pd.DataFrame):
        # 加载商圈市场量：箱&包
        sql_vol = "select {},{},{},{},{},{} from {} where {}='{}' and {} in ('总市场量（潜力市场量）','人均包') and {}='总市场量'".format(marketingCompany, salesDepartment,
                              businessArea, priceType, sale, unit, marketVolume, timeCol, periodTag, typeAC, manufacturer)
        df_vol = pd.read_sql(sql_vol, cm.engine)
    # 获取人口
    df_pop = df_factor[df_factor[factorType]=='人口'].set_index(busAdInfo1)
    df_pop = df_pop[[factorNum]]
    # 人口单位转化为万人
    df_pop = df_pop / 10000
    df_pop.columns = ['人口']
    # 计算通路点数
    df_channel = df_factor[df_factor[factorType].isin(channelList)].groupby(busAdInfo1).sum()
    df_channel.columns = ['通路点数']
    # 获取商圈信息，比如大商圈
    sql_info = "select {},{},{},{},{},customerpattern from {} where {} = '{}'".format(marketingCompany, salesDepartment,businessArea,
                                bigbusiness,smallbusiness,infoName,timeCol, periodTag)
    df_info = pd.read_sql(sql_info, cm.engine)
    df_info2 = df_info.drop_duplicates([marketingCompany,salesDepartment,businessArea])
    df_info2 = df_info2.set_index([marketingCompany,salesDepartment,businessArea])
    df_channel = df_channel.merge(df_info2, left_index=True,right_index=True,how='left')
    # 获取高价面人均包
    df_per = df_vol[(df_vol[unit]=='包/人')&(df_vol[priceType].isin(['高价袋','容器面']))]
    df_per = df_per.groupby(busAdInfo1).sum()
    df_per.columns = ['高价面人均包']
    # 获取五品类整体总市场量（箱）
    df_total = df_vol[(df_vol[unit]=='箱')&(df_vol[priceType]=='整体')].set_index(busAdInfo1)
    # 将单位箱/年转化为千箱/每月
    df_total = df_total[[sale]]
    df_total = df_total/ (12*1000)
    df_total.columns = ['总市场量(千箱/月)']
    # 合并
    df_final = pd.concat([df_total, df_per, df_pop, df_channel], axis=1)
    df_final.to_excel('产出数据/商圈分级参考数据.xlsx', merge_cells=False)

    return df_final


def directMarketing():
    df1 = pd.read_excel('原始数据/康面直营二阶城市.xlsx').fillna(method="pad")
    df1 = df1.drop_duplicates(['公司', '城市名称'])
    df2 = pd.read_excel('原始数据/商圈城市信息.xlsx')
    # 筛选出直营二阶城市
    df2.loc[df2['city'].isin(df1['城市名称']), 'addInfo'] = '直营二阶城市'
    #len(df2[(df2['addInfo']=='直营二阶城市')&((df2['customerpattern'].str.contains('城市'))|(df2['customerpattern'].str.contains('物流')))])
    df2.to_excel('原始数据/商圈附加直营二阶城市信息.xlsx', index=False)


def toCustLocalGrade(df):
    # 将商圈形态信息转化为等级信息
    df2 = df.rename(columns={bigbusiness:'大商圈', smallbusiness:'小商圈', 'customerpattern':'客户形态'})
    xls_file=pd.ExcelFile('原始数据/全国各商圈客户形态等级对应表.xlsx')
    df_kh = xls_file.parse(sheetname='客户形态')
    df_lc = pd.read_excel('原始数据/全国各商圈地方希望的等级.xlsx')
    df3 = df2.merge(df_kh, on=['大商圈','客户形态'], how='left')
    df4 = df3.merge(df_lc, on=['大商圈','小商圈'], how='left')
    return df4


def provSummary(df_grade, periodTag, directTag):
    df1 = df_grade
    df3 = df1[['province','建议等级','总市场量(千箱/月)']]
    df_new = pd.pivot_table(df3,index=['province',],columns='建议等级',values=['建议等级','总市场量(千箱/月)'],
                         aggfunc={'建议等级':len,'总市场量(千箱/月)':np.sum},fill_value=0)

    df_new_1= df_new['建议等级']
    df_new_1['总计'] = df_new_1.sum(axis=1)
    df_new_sqzb = df_new_1.apply(lambda x:x/df_new_1['总计'])  #商圈数量占比
    df_new_sqljzb = df_new_sqzb.apply(np.cumsum,axis=1)  #商圈数量累计占比
    df_new_sqljzb['总计'] = 1
    
    df_new_2 = df_new['总市场量(千箱/月)']
    df_new_2['总计'] = df_new_2.sum(axis=1)
    df_new_sclzb = df_new_2.apply(lambda x:x/df_new_2['总计'])  #市场量占比
    df_new_sclljzb = df_new_sclzb.apply(np.cumsum,axis=1)   #市场量累计占比
    df_new_sclljzb['总计'] = 1
    # stack
    df_new_1 = df_new_1.stack()
    df_new_1.name = '商圈个数'
    
    df_new_sqzb = df_new_sqzb.stack()
    df_new_sqzb.name = '商圈数量占比'
    
    df_new_sqljzb = df_new_sqljzb.stack()
    df_new_sqljzb.name = '商圈个数累计占比'
    
    df_new_2 = df_new_2.stack()
    df_new_2.name = '整体市场千箱/月'

    df_new_sclzb = df_new_sclzb.stack()
    df_new_sclzb.name = '整体市场量占比'

    df_new_sclljzb = df_new_sclljzb.stack()
    df_new_sclljzb.name = '整体市场量累计占比'
    
    df_final = pd.concat([df_new_1, df_new_sqzb,df_new_sqljzb,df_new_2,df_new_sclzb,df_new_sclljzb], axis=1)
    df_final = df_final.reset_index()
    df_final = df_final.rename(columns={province:'省份','建议等级':'商圈级别'})
    df_final.to_excel('产出数据/各省商圈分级分布_%s%s.xlsx'%(periodTag,directTag), index=False)
    


def map15bus(df):
    dfo = pd.read_excel('原始数据/18版与15版商圈匹配.xlsx',skiprows=[0])
    df2 = df.merge(dfo, on=busAdInfo1, how='left')
    return df2

def directCity(df):
    df1 = pd.read_excel('原始数据/商圈附加直营二阶城市信息.xlsx')
    df2 = df.merge(df1, on=busAdInfo1,how='left')
    # 去除不包含“区”字段的商圈
    # df2.loc[~((df2[businessArea].str.contains('区'))&(~df2[businessArea].str.contains('县（'))), 'addInfo'] = np.nan
    return df2

def map15grade(df):
    df1 = pd.read_excel('原始数据/15商圈分级等级信息.xlsx')
    df2 = df1[['商圈等级', '城市', '行政区域']]
    df3 = df.merge(df2, on=['城市', '行政区域'],how='left')
    return df3

VPT = {
       '总市场量1':180,'高价面人均包1':20,'人口1':50,
       '总市场量2':100,'高价面人均包2':13,'人口2':0,'通路点数2':750,
       '总市场量3':60,'高价面人均包3':8,'人口3':40,
       '总市场量4':50,'高价面人均包4':0,'人口4':0,
       '总市场量5':30,'高价面人均包5':0,'人口5':0,
       }
def grading2(VPT, direct=False,  df_vol=''):
    gradeOutTag = '产出数据/全国商圈分级_%s'%periodTag
    directTag = ''
    # df = pd.read_excel('产出数据/商圈分级参考数据.xlsx',index_col=[0,1,2])
    df = getData(df_vol)
    df['建议等级'] = 6
    df.loc[(df['总市场量(千箱/月)'] >= VPT['总市场量1']) & (df['高价面人均包']>=VPT['高价面人均包1'])&
           (df['人口']>VPT['人口1']), '建议等级'] = 1
    df.loc[(df['总市场量(千箱/月)'] >= VPT['总市场量2']) & (df['高价面人均包']>=VPT['高价面人均包2'])&
           (df['通路点数']>VPT['通路点数2'])&(df['人口']>VPT['人口2'])&(df['建议等级']!=1), '建议等级'] = 2
    df.loc[(df['总市场量(千箱/月)'] >= VPT['总市场量3']) & (df['高价面人均包']>=VPT['高价面人均包3'])&
           (df['人口']>VPT['人口3'])&(~df['建议等级'].isin([1,2])), '建议等级'] = 3
    df.loc[(df['总市场量(千箱/月)'] >= VPT['总市场量4']) & (df['高价面人均包']>=VPT['高价面人均包4'])&
           (df['人口']>VPT['人口4'])&(~df['建议等级'].isin([1,2,3])), '建议等级'] = 4
    df.loc[(df['总市场量(千箱/月)'] >= VPT['总市场量5']) & (df['高价面人均包']>=VPT['高价面人均包5'])&
           (df['人口']>VPT['人口5'])&(~df['建议等级'].isin([1,2,3,4])), '建议等级'] = 5
    
    # 确保直营二阶的市辖区商圈在1级或2级
    df2 = df.reset_index()
    def makeDirect2Grade(df):   
        df.loc[(df['addInfo'].notnull())&(df['总市场量(千箱/月)']>150)&(df['高价面人均包']>15), '建议等级'] = 1
        df.loc[(df['addInfo'].notnull())&(df['建议等级']>1), '建议等级'] = 2
        return df
    df2 = directCity(df2)
    
    # 是否考虑直营二阶城市在一二级
    if direct:
        df2 = makeDirect2Grade(df2)
        directTag = '_直营二阶'
        gradeOutTag = gradeOutTag + directTag
        
    logger.info(df2.groupby('建议等级').size())
    
    df2 = toCustLocalGrade(df2)
    # 统计升降级个数
    df2.loc[df2['建议等级']>df2['客户形态等级'], '调整建议'] = '建议降级'
    df2.loc[df2['建议等级']<df2['客户形态等级'], '调整建议'] = '建议升级'
    df2.loc[df2['建议等级']==df2['客户形态等级'], '调整建议'] = '建议维持'
    logger.info('建议升级商圈数占比:{}'.format(len(df2[df2['调整建议']=='建议升级']) / len(df2[df2['客户形态等级'].notnull()])))
    logger.info('建议降级商圈数占比:{}'.format(len(df2[df2['调整建议']=='建议降级']) / len(df2[df2['客户形态等级'].notnull()])))
    logger.info('建议维持商圈数占比:{}'.format(len(df2[df2['调整建议']=='建议维持']) / len(df2[df2['客户形态等级'].notnull()])))
    
    df3 = map15bus(df2)
    

    # 暂时处理一商圈多城市的重复，保留第一个城市
    df5 = df3.drop_duplicates(busAdInfo1)
    df6 = map15grade(df5)
    df6 = df6.rename(columns={'商圈等级':'15商圈等级'})
    df6['15商圈等级'] = np.where(df6['15商圈等级'].isnull(),df6['15商圈等级'],df6['15商圈等级'].str.replace('级', ''))
    # 筛选出商圈含“区”的直营二阶
    df6.loc[~df6[businessArea].str.contains('区'),'addInfo'] = np.nan
    
    #获取本品市场量
    def addKsf(df6):
        df_add = pd.read_excel('产出数据/全国商圈分级--1705-1804市场量推算.xlsx')
        df_add[list(df_add)[13:-16]] = df_add[list(df_add)[13:-16]] / 12
        df_add['总市场量（潜力市场量）_千包_高价面'] = df_add['总市场量（潜力市场量）_千包_高价袋'] + df_add['总市场量（潜力市场量）_千包_容器面']
        df_add['KSF实际销量_千箱_高价面'] = df_add['KSF实际销量_千箱_高价袋'] + df_add['KSF实际销量_千箱_容器面']
        df_add['KSF实际销量_千包_高价面'] = df_add['KSF实际销量_千包_高价袋'] + df_add['KSF实际销量_千包_容器面']
        df_add = df_add.drop(['人口（万人）'], axis=1)
        df7 = df6.merge(df_add, on=busAdInfo1, how='right')
        return df7
    
    df6 = addKsf(df6)
    # 需要调整的商圈
    df6s = df6[df6['调整建议']!='建议维持']
    # 被降级的一级商圈
    df6s.loc[df6s['客户形态等级']==1, 'addInfo2'] = '被降级的1级商圈'
    df6s.loc[(df6s['客户形态等级']==2)&(df6s['调整建议']=='建议降级'), 'addInfo2'] = '被降级的2级商圈'
    df6s.loc[(df6s['客户形态等级']==3)&(df6s['调整建议']=='建议降级'), 'addInfo2'] = '被降级的3级商圈'
    df6s.loc[(df6s['客户形态等级']==4)&(df6s['调整建议']=='建议降级'), 'addInfo2'] = '被降级的4级商圈'
    df6s.loc[(df6s['客户形态等级']==5)&(df6s['调整建议']=='建议降级'), 'addInfo2'] = '被降级的5级商圈'
    df6s.loc[df6s['建议等级']==1, 'addInfo2'] = '升级为1级的商圈'
    df6s.loc[(df6s['建议等级']==2)&(df6s['调整建议']=='建议升级'), 'addInfo2'] = '升级为2级的商圈'
    df6s.loc[(df6s['建议等级']==3)&(df6s['调整建议']=='建议升级'), 'addInfo2'] = '升级为3级的商圈'
    df6s.loc[(df6s['建议等级']==4)&(df6s['调整建议']=='建议升级'), 'addInfo2'] = '升级为4级的商圈'
    df6s.loc[(df6s['建议等级']==5)&(df6s['调整建议']=='建议升级'), 'addInfo2'] = '升级为5级的商圈'
    
    writer = pd.ExcelWriter(gradeOutTag + '.xlsx')
    df6.to_excel(writer, '全部商圈', index=False)
    df6s.to_excel(writer, '需调整的商圈', index=False)
    writer.save()
    provSummary(df6, periodTag, directTag)
    return df6


if __name__ == '__main__':

    gradeFilePath = '产出数据/全国商圈分级第二版8直营二阶.xlsx'      
    grading2(VPT)
    provSummary(gradeFilePath, periodTag)
    gradeFilePath2 = '产出数据/2015年各省商圈分级建议.xlsx'
    provSummary(gradeFilePath2) 
            


"""
if __name__ == '__main__':
    df2, df_m = adjust(VPT2)
    tag = '_new'
    writer = pd.ExcelWriter('产出数据/2018年各商圈分级建议%s.xlsx'%tag)
    df2.to_excel(writer, '分级建议', index=False)
    df_m.to_excel(writer, '变化')
    writer.save()
"""

    # 按康师傅2014年的标准进行定级
    #df3 = adjust(VPT_ori)


# 升降级
"""
df2 = pd.read_excel('原始数据/湖北商圈分级调整建议2.xlsx', sheetname='等级信息对应表')
df_merge = df1.merge(df2, on='商圈形态', how='left')
df_merge = df_merge.rename(columns={"商圈等级": "建议等级",bigbusiness:'大商圈','customerpattern':'客户形态'})

# 升降级
df_merge['调整建议'] = '维持'
df_merge.loc[df_merge['原先等级'] > df_merge['建议等级'], '调整建议'] = '建议升级'
df_merge.loc[df_merge['原先等级'] < df_merge['建议等级'], '调整建议'] = '建议降级'
print('建议升级：',len(df_merge[df_merge['调整建议'] == '建议升级']))
print('建议降级：', len(df_merge[df_merge['调整建议'] == '建议降级']))
"""

VPT1 = {
       '总市场量1':180,
       '通路点数':1500,
       '高价面人均包1':15,
       '人口1':500,
       '人口2':200,
       '总市场量2':100,
       '高价面人均包2':13,
       '总市场量3':50,
       '高价面人均包3':6,
       '人口3':45,
       '人口4':80,
       '总市场量4':70,
       '总市场量5':40,
       '总市场量6':25,
       '总市场量7':20,
       '总市场量8':15,
       }

VPT2 = {
       '总市场量1':190,
       '通路点数':1500,
       '高价面人均包1':20,
       '人口1':500,
       '人口2':200,
       '总市场量2':100,
       '高价面人均包2':13,
       '总市场量3':55,
       '高价面人均包3':8,
       '人口3':45,
       '人口4':80,
       '总市场量4':80,
       '总市场量5':50,
       '总市场量6':30,
       '总市场量7':25,
       '总市场量8':20,
       }

VPT_ori = {
       '总市场量1':200,
       '通路点数':1500,
       '高价面人均包1':20,
       '人口1':500,
       '人口2':200,
       '总市场量2':100,
       '高价面人均包2':13,
       '总市场量3':60,
       '高价面人均包3':8,
       '人口3':45,
       '人口4':80,
       '总市场量4':90,
       '总市场量5':60,
       '总市场量6':40,
       '总市场量7':30,
       '总市场量8':20,
       }


## 旧的分级方法1
def grading_old(VPT, df_vol):
    df = getData(df_vol)
    df['形态1'] = '其他'
    # 定义核心城区 暂时先拿掉通路点数   & (df['通路点数']>VPT['通路点数']) 
    df.loc[(df['总市场量(千箱/月)'] >= VPT['总市场量1'])& ((df['高价面人均包']>=VPT['高价面人均包1']) | 
            (df['人口']>VPT['人口1'])), '形态1'] = '核心城区'
    df.loc[(df['形态1'] == '核心城区') & (df['人口']>VPT['人口2']), '商圈形态'] = '核心城区A'
    df.loc[(df['形态1'] == '核心城区') & (df['人口']<=VPT['人口2']), '商圈形态'] = '核心城区B'
    # 精耕城区
    df.loc[(df['形态1'] != '核心城区') & (df['总市场量(千箱/月)'] >= VPT['总市场量2']) & (df['高价面人均包']>VPT['高价面人均包2']), '形态1'] = '精耕城区'
    df.loc[df['形态1'] == '精耕城区', '商圈形态'] = '精耕城区'
    # 准精耕城市
    df.loc[(df['形态1'] == '其他') & (df['总市场量(千箱/月)'] >= VPT['总市场量3']) & (df['高价面人均包']>VPT['高价面人均包3']) & (df['人口']>VPT['人口3']),
           '形态1'] = '准精耕城市'
    df.loc[(df['形态1'] == '准精耕城市') & ((df['人口']>VPT['人口4']) | (df['总市场量(千箱/月)'] >= VPT['总市场量4'])), '商圈形态'] = '准精耕城市A'
    df.loc[(df['形态1'] == '准精耕城市') & (df['商圈形态'] !='准精耕城市A'), '商圈形态'] = '准精耕城市B'
    
    # 其他-外阜
    df.loc[(df[bigbusiness] == '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] > VPT['总市场量5']), '商圈形态'] = '外埠A'
    df.loc[(df[bigbusiness] == '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] > VPT['总市场量6']) & (df['总市场量(千箱/月)'] <= VPT['总市场量5']), '商圈形态'] = '外埠B'
    df.loc[(df[bigbusiness] == '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] > VPT['总市场量8']) & (df['总市场量(千箱/月)'] <= VPT['总市场量6']), '商圈形态'] = '外埠C'
    df.loc[(df[bigbusiness] == '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] < VPT['总市场量8']), '商圈形态'] = '外埠D'
    
    # 其他
    df.loc[(df[bigbusiness] != '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] > VPT['总市场量5']), '商圈形态'] = '核心郊区县A'
    df.loc[(df[bigbusiness] != '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] > VPT['总市场量7']) & (df['总市场量(千箱/月)'] <= VPT['总市场量5']), '商圈形态'] = '核心郊区县B'
    df.loc[(df[bigbusiness] != '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] < VPT['总市场量7']), '商圈形态'] = '核心郊区县C'
    
    df1 = df.reset_index()
    
    #df1[df1[businessArea]=='城关区+堆龙德庆区+林周县+当雄县+尼木县+曲水县+达孜县+墨竹工卡县']
    df.loc[(df['形态1'] == '准精耕城市') & (df['人口']>80)]
    df.loc[(df['人口']>80) | (df['总市场量(千箱/月)'] >= 70)]
    # 将商圈形态信息转化为等级信息
    df1 = df1.rename(columns={bigbusiness:'大商圈', 'customerpattern':'客户形态'})
    xls_file=pd.ExcelFile('E:\CloudStation\康面商圈分级\康面商圈分级最终代码V2\原始数据\商圈等级对应表.xlsx')
    df_sq = xls_file.parse(sheetname='商圈形态')
    df_kh = xls_file.parse(sheetname='客户形态')
    df2 = df1.merge(df_sq, on='商圈形态', how='left')
    df3 = df2.merge(df_kh, on=['大商圈','客户形态'], how='left')
    
    # 统计升降级个数
    df3.loc[df3['建议等级']>df3['客户形态等级'], '调整建议'] = '建议降级'
    df3.loc[df3['建议等级']<df3['客户形态等级'], '调整建议'] = '建议升级'
    df3.loc[df3['建议等级']==df3['客户形态等级'], '调整建议'] = '建议维持'
    
    # 变化
    dt1 = df3[['客户形态等级','商圈形态']].groupby('客户形态等级').count()
    dt2 = df3[['建议等级','商圈形态']].groupby('建议等级').count()
    df_m = dt1.merge(dt2,left_index=True,right_index=True)
    df_m.columns = ['原先(客户形态等级)数量','建议调整后的数量']
    df_m.index.name = '等级'
    
    print('建议升级商圈数占比:{}'.format(len(df3[df3['调整建议']=='建议升级']) / len(df3[df3['客户形态等级'].notnull()])))
    print('建议降级商圈数占比:{}'.format(len(df3[df3['调整建议']=='建议降级']) / len(df3[df3['客户形态等级'].notnull()])))
    print('建议维持商圈数占比:{}'.format(len(df3[df3['调整建议']=='建议维持']) / len(df3[df3['客户形态等级'].notnull()])))

    return df3, df_m




