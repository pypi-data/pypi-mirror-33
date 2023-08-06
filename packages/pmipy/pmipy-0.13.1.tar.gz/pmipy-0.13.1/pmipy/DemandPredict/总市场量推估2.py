# -*- coding: utf-8 -*-
"""
Created on Mon Feb 26 15:43:50 2018

@author: Administrator
"""
import yaml
import numpy as np
import pandas as pd


# 分配统一和今麦郎的销量至康师傅的各商圈
def allocation_sale(df_ksf, df_tyjml, period):
    # 确保三甲公司五种规格的名称统一
    df_ksf = df_ksf.fillna(0)
    df_tyjml = df_tyjml.fillna(0)
    spec_list = [i+'.{}'.format(period-1) for i in ['容器面', '高价袋','中价面','平低价','干脆面']]
    df_ksf2 = df_ksf.loc[:, ["营业部","具体描述"]+spec_list]
    df_tyjml2 = df_tyjml.loc[:, ["营业部"]+spec_list].groupby("营业部").sum()
    df_depart = df_ksf2.groupby("营业部").sum() + df_tyjml2.drop('MT部')
    # 将MT部的销量分散在四个营业部中
    df_depart2 = df_tyjml2.loc['MT部'] * df_depart / df_depart.sum() + df_depart
    # 将康师傅其他MT部的销量分配到康师傅各商圈中
    df_ksf2 = df_ksf2.set_index(["营业部","具体描述"])
    df_ksf3 = df_tyjml.loc['康师傅其他', spec_list] * df_ksf2 / df_ksf2.sum() + df_ksf2
    df_ksf3 = df_ksf3.astype('float64')
    df_ksf_actual = df_ksf3.copy()
    # 额外计算整体市场
    df_ksf_actual['整体'] = df_ksf_actual.loc[:, spec_list].sum(axis=1)
    # 输出康师傅各商圈实际出货量
    df_ksf3.to_excel('KSF各商圈实际出货量.xlsx')
    # 将三大厂商的营业部出货数据拆分到KSF各商圈
    # 如果平低价为空，则将使用中价面和干脆面的量模糊代表中价面
    lowPrice = '平低价.{}'.format(period-1)
    if True in df_ksf3.groupby('营业部').sum()[lowPrice].isnull().values:
        df_ksf3.loc[:, lowPrice] = df_ksf3.loc[:, ['中价面.{}'.format(period-1), '干脆面.{}'.format(period-1)]].sum(axis=1)
    df_ksf4 = df_ksf3.apply(lambda x: x/x.groupby('营业部').sum())
    for index, d in enumerate(df_ksf["营业部"].drop_duplicates()):
        if not index:
            df_ksf5 = df_ksf4.xs(d, level='营业部') * df_depart2.loc[d]
        else:
            df_temp = df_ksf4.xs(d, level='营业部') * df_depart2.loc[d]
            df_ksf5 = pd.concat([df_ksf5, df_temp])
            
    # 重新获取营业部信息
    df_3c = pd.concat([df_ksf.loc[:, ["营业部","具体描述"]].set_index("具体描述"), df_ksf5], axis=1)
    # df_3c.to_excel('各商圈三甲市场量.xlsx')

    return df_3c, df_ksf_actual  # 三甲公司实际出货量, 康师傅实际出货量

# 校准矩阵1--包含0.5权重的销量通路点数和0.5权重的正负因子系数bias
# 输入DataFrame需包含三甲在各商圈出货量，各商圈通路点数
def calibration_matrix1(df_3c, df_channel, province, period, df_bias=[]):
    # 校准至0.7至1.2
    def ratio_calibration(x):
        # tanh函数
        tanh = lambda x: 2.0 / (1.0 + np.exp(-2*x)) - 1
        if x > 1: 
            # 控制在1.2以下
            y = 0.3 * tanh(0.5*x-0.5) + 1
        else:
            # 控制在0.6以上
            y = 0.5 * tanh(0.35*x-0.5) + 1
        return y

    # 选取指定年份下的规格别
    spec_list = [i+'.{}'.format(period-1) for i in ['容器面', '高价袋','中价面','平低价','干脆面']]
    ## 各商圈销量总和与通路总和的比值
    df_channel1 = df_3c.loc[:, spec_list].apply(lambda x: df_channel['总通路点数'] / x)
    # 各商圈销量总和与通路总和的比值
    sr_channel = df_channel['总通路点数'].sum() / df_3c.loc[:, spec_list].sum()
    df_channel1 = df_channel1 / sr_channel
    df_adjust1 = df_channel1.applymap(ratio_calibration)

    # 对预估与实际的比值（bias）进行校准,如果为空，则只采用df_adjust1
    if len(df_bias):
        try:
            df_bias = df_bias.loc[:, spec_list] # 首先尝试提取指定年份的规格别销量
        except:
            df_bias = df_bias.loc[:, ['容器面平均', '高价袋平均','中价面平均','平低价平均','干脆面平均']]
            df_bias.columns = spec_list
        df_adjust2 = df_bias.applymap(ratio_calibration)
        cal_mat1 = 0.5 * df_adjust1 +  0.5 * df_adjust2
    else:
        cal_mat1 = df_adjust1
    # 输出各商圈因子综合影响系数和通路影响系数
    #df_adjust1.to_excel('%s各商圈正负因子综合指数.xlsx' % province)
    #df_adjust2.to_excel('%s各商圈各通路综合指数.xlsx' % province)
    cal_mat1.to_excel('%s各商圈正负因子综合指数.xlsx' % province)
    return cal_mat1

# 获取尼尔森提供的三甲在总方便面市场中的市占
def calibration_AC(df_mutilComp, province, period):
    # 提取对应省份对应年份的物种规格别销量
    try:
        df_mutilComp2 = df_mutilComp.loc[province + '总和']['年销量.{}'.format(period-1)]
    except KeyError: # 省份名称切换
        df_mutilComp2 = df_mutilComp.loc[[x[0] for x in prov_mapp.items() 
        if province in x[1]][0] + '总和']['年销量.{}'.format(period-1)]
    # 将尼尔森的低平价面改为地评价
    # spec_list = [i+'.{}'.format(period-1) for i in ['容器面', '高价袋','中价面','平低价','干脆面']]
    spec_list_old = [i[:3]+'.{}'.format(period-1) for i in df_mutilComp2]
    df_mutilComp2.columns = spec_list_old
    cal_AC = df_mutilComp2.loc[['康师傅', '统一', '今麦郎'], :].sum()
    
    return cal_AC

# 获取尼尔森提供的三甲在总方便面市场中的市占
def calibration_manual(period, province):
    # 将规格别列名修改为对应年份的规格别
    df = pd.read_excel('Calibration_manual.xlsx')
    df.columns = [i+'.{}'.format(period-1) for i in df.columns]
    cal_man = df.loc[province]
    
    return cal_man

# 各商圈总方便面市场量预估
def market_total(df_3c, cal_mat1, cal_AC, cal_man):
    df_total = df_3c.reset_index().set_index(["营业部","具体描述"])
    df_total = df_total * cal_mat1 * cal_man / cal_AC
    df_total['整体'] = df_total.sum(axis=1)  
    return df_total
    

def market_estimate(province='湖北省', period=3):
    spec_list = [i+'.{}'.format(period-1) for i in ['容器面', '高价袋','中价面','平低价','干脆面']]
    # 获取康师傅各商圈实际出货，三甲各商圈实际出货
    df_3c, df_ksf2 = allocation_sale(df_ksf, df_tyjml, period)
    # 获取校准系数矩阵1
    cal_mat1 = calibration_matrix1(df_3c, df_channel, province, period, df_bias)
    # 获取三甲厂商各规格占总市场各规格的比例
    cal_AC = calibration_AC(df_mutilComp, province, period)
    # 获取经验人工校准数据
    cal_man = calibration_manual(period, province)
    # 预估各规格总市场量
    df_total = market_total(df_3c, cal_mat1, cal_AC, cal_man)
    # 计算营业部市占
    df_marketShare1 = df_ksf2.groupby('营业部').sum() / df_total.groupby('营业部').sum()
    # 计算各商圈市占
    df_ksf2_s = df_ksf2.reset_index(level='营业部', drop=True)
    df_total_s = df_total.reset_index(level='营业部', drop=True)
    df_ksf2_s.loc[province] = df_ksf2_s.sum()
    df_total_s.loc[province] = df_total_s.sum()
    df_marketShare2 = df_ksf2_s / df_total_s  
    # 计算人均包
    df_pop = df_channel.copy()
    df_pop.loc[province] = df_channel.sum()
    df_population = df_pop['人口'] # 获取各商圈人口信息
    # 将千箱转化为包
    df_capita = df_total_s * 24
    df_capita['容器面.{}'.format(period-1)] = df_capita['容器面.{}'.format(period-1)] / 2
    df_capita['整体'] = df_capita.loc[:, spec_list].sum(axis=1)
    df_capita2 = df_capita.apply(lambda x: x * 1000/ df_population) 
    df_capita2['整体'] = df_capita2.loc[:, spec_list].sum(axis=1)
    # 重新排序，将湖北省放最后
    df_capita2 = df_capita2.reindex(df_capita.index)
    df_total_s.loc[:, spec_list+['整体']].to_excel('{}各商圈总市场量（千箱）.xlsx'.format(province))
    df_capita.loc[:, spec_list+['整体']].to_excel('{}各商圈总市场量（千包）.xlsx'.format(province))
    df_marketShare1.loc[:, spec_list+['整体']].to_excel('{}各营业部市占.xlsx'.format(province))
    df_marketShare2.loc[:, spec_list+['整体']].to_excel('{}各商圈市占.xlsx'.format(province))
    df_capita2.loc[:, spec_list+['整体']].to_excel('{}各商圈人均包.xlsx'.format(province))


if __name__ == '__main__':
    df_ksf = pd.read_excel('湖北省KSF各商圈TT&MT出货.xlsx', sheetname='TT&MT')
    df_tyjml = pd.read_excel('统一和今麦郎出货量.xlsx', index_col="厂商")
    df_bias = pd.read_excel("湖北预估与实际的比值-最新.xlsx", index_col = '具体描述')
    df_dapart = pd.read_excel("营业部与商圈对应.xlsx", index_col = '具体描述')
    df_market = pd.read_excel("最新一年KSF各个部门的三甲市占.xlsx")
    df_channel = pd.read_excel("通路点数和人口.xlsx", index_col = '具体描述')
    df_mutilComp = pd.read_excel("各范围各厂商方便面.xlsx", index_col=[0,1], header=[0,1], sheetname='市占')
    prov_mapp = yaml.load(open('E:\CloudStation\OCM\省份名单对应表.yaml', encoding='utf-8'))
  
    market_estimate()



"""
df = df.applymap(lambda x: 1/x)
df.to_excel("湖北实际与预估的比值-最新.xlsx")
category = ['整体', '中高价面',	'高价面', '容器面','高价袋',	'中价面',	'平低价','干脆面']
for cate in category:
    # 计算三年平均
    df_channel[('平均', '{0}平均'.format(cate))] = df_channel.loc[:,[('2015年',cate),('2016年',cate), ('2017年',cate)]].mean(axis=1)
    # 计算通路点数/三年平均
    df_channel[('平均通路点数', '{0}通路'.format(cate))] = df_channel.loc[:,[('2015年',cate),('2016年',cate), ('2017年',cate)]].mean(axis=1)
df_channel.to_excel("业绩和通路点数2.xlsx")
"""

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

