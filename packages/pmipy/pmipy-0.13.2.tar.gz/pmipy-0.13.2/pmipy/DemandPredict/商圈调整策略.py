# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 16:27:28 2018

@author: jasonai
"""
import numpy as np
import pandas as pd



# 考虑的通路点数
channel = ["中学","加油加气站","小学","成人教育","火车站","网吧","超市","酒店","长途汽车站","高等院校"]
def grading_standard(df, province='湖北省'):
    gb = df.groupby('原先等级')
    df_q1 = gb.quantile(q=0.25)
    df_q1['统计'] = '下四分位'
    df_q2 = gb.quantile(q=0.5)
    df_q2['统计'] = '中位数'
    df_q3 = gb.quantile(q=0.75)
    df_q3['统计'] = '上四分位'
    df2 = pd.concat([df_q1, df_q2, df_q3])
    df3 = df2.sort_index()
    df3.to_excel('各等级信息.xlsx')
    return df3


df = pd.read_excel('湖北商圈分级调整建议2.xlsx')
# df2 = grading_standard(df)

# df['建议等级'] = df['原先等级']
# 其他
df['形态1'] = '其他'
# 定义核心城区
df.ix[(df['总市场量(千箱/月)'] >= 180) & (df['通路点数']>2500) & ((df['高价面']>15) | (df['人口']>500)), '形态1'] = '核心城区'
df.ix[(df['形态1'] == '核心城区') & (df['人口']>200), '商圈形态'] = '核心城区A'
df.ix[(df['形态1'] == '核心城区') & (df['人口']<=200), '商圈形态'] = '核心城区B'
# 精耕城区
df.ix[(df['形态1'] != '核心城区') & (df['总市场量(千箱/月)'] >= 80) & (df['高价面']>11), '形态1'] = '精耕城区'
df.ix[df['形态1'] == '精耕城区', '商圈形态'] = '精耕城区'
# 准精耕城区
df.ix[(df['形态1'] == '其他') & (df['总市场量(千箱/月)'] >= 50) & (df['高价面']>6) & (df['人口']>45), '形态1'] = '准精耕城区'
df.ix[(df['形态1'] == '准精耕城区') & ((df['人口']>80) | (df['总市场量(千箱/月)'] >= 70)), '商圈形态'] = '准精耕城区A'
df.ix[(df['形态1'] == '准精耕城区') & (df['形态1'] !='准精耕城区A'), '商圈形态'] = '准精耕城区B'

# 其他-外阜
df.ix[(df['大商圈'] == '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] > 40), '商圈形态'] = '外埠A'
df.ix[(df['大商圈'] == '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] > 30) & (df['总市场量(千箱/月)'] <= 40), '商圈形态'] = '外埠B'
df.ix[(df['大商圈'] == '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] > 15) & (df['总市场量(千箱/月)'] <= 30), '商圈形态'] = '外埠C'
df.ix[(df['大商圈'] == '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] < 15), '商圈形态'] = '外埠C'

# 其他
df.ix[(df['大商圈'] != '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] > 40), '商圈形态'] = '核心郊区县A'
df.ix[(df['大商圈'] != '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] > 20) & (df['总市场量(千箱/月)'] <= 40), '商圈形态'] = '核心郊区县B'
df.ix[(df['大商圈'] != '外埠片区') & (df['形态1'] == '其他') & (df['总市场量(千箱/月)'] < 20), '商圈形态'] = '核心郊区县C'

df2 = pd.read_excel('湖北商圈分级调整建议2.xlsx', sheetname='等级信息对应表')
df_merge = df.merge(df2, on='商圈形态', how='left')
df_merge = df_merge.rename(columns={"商圈等级": "建议等级"})
# 升降级
df_merge['调整建议'] = '维持'
df_merge.ix[df_merge['原先等级'] > df_merge['建议等级'], '调整建议'] = '建议升级'
df_merge.ix[df_merge['原先等级'] < df_merge['建议等级'], '调整建议'] = '建议降级'
print('建议升级：',len(df_merge[df_merge['调整建议'] == '建议升级']))
print('建议降级：', len(df_merge[df_merge['调整建议'] == '建议降级']))
df_merge.to_excel('ts.xlsx', index=False)

#get_channel('湖北省各商圈总市场量（千箱）')
# get_channel('湖北省各商圈人口')
#get_channel('湖北省各商圈人均包')
"""
df1 = pd.read_excel('湖北省各商圈总市场量（千箱）_含等级信息.xlsx')
df1.drop('湖北省', inplace=True)
df2 = pd.read_excel('湖北省各商圈通路点数.xlsx', index_col='具体描述',usecols=['具体描述','通路点数'])
df3 = pd.read_excel('湖北省各商圈人均包.xlsx',index_col='具体描述',usecols=['具体描述','高价面'])
df = pd.concat([df1,df2,df3], axis=1)
df = pd.concat([df,df3], axis=1)
"""






df['状态'] = '维持不变'
df.ix[df['等级'] > df['建议等级'], '状态'] = '建议升级'
df.ix[df['等级'] < df['建议等级'], '状态'] = '建议降级'



df5 = pd.read_excel('湖北省各商圈地理因子数据.xlsx', index_col='具体描述')
df6 = df5[channel]
df6['通路点数'] = df6.sum(axis=1)
df6.to_excel('湖北通路点数.xlsx')