# -*- coding: utf-8 -*-
"""
Created on Mon Mar 12 13:46:03 2018

@author: Administrator
"""
import pandas as pd
import random

df = pd.read_excel('全国正负因子.xlsx', index_col=0, header=[0,1])

# 正因子
def zyz(n=8):
    return [random.uniform(0.1,0.4) for i in range(n)]

# 整体面的中间带
def zt_zjd(n=9):
    return [random.uniform(-0.2,0.2) for i in range(n)]

# 容器面和高价袋的中间带
def gjm_zjd(n=9):
    return [random.uniform(0,0.2) for i in range(n)]

# 低价面的中间带
def djm_zjd(n=9):
    return [random.uniform(-0.2,0) for i in range(n)]

# 负因子
def fyz_zjd(n=5):
    return [random.uniform(-0.2,-0.1) for i in range(n)]  

unit = int(len(df.columns) / 6)

prov_list = []
# 整体
for index, u in enumerate(range(unit)):
    df.iloc[:, 6*u] = zyz() + zt_zjd() + fyz_zjd() # 整体
    s1 = df.iloc[:, 6*u].sort_values(ascending=False).reset_index()
    
    df.iloc[:, 6*u+1] = zyz() + gjm_zjd() + fyz_zjd() # 容器面
    s2 = df.iloc[:, 6*u+1].sort_values(ascending=False).reset_index()
    
    df.iloc[:, 6*u+2] = zyz() + gjm_zjd() + fyz_zjd() # 高价袋
    s3 = df.iloc[:, 6*u+2].sort_values(ascending=False).reset_index()
    
    df.iloc[:, 6*u+3] = zyz() + djm_zjd() + fyz_zjd() # 中价面
    s4 = df.iloc[:, 6*u+3].sort_values(ascending=False).reset_index()
    
    df.iloc[:, 6*u+4] = zyz() + djm_zjd() + fyz_zjd() # 低平价面
    s5 = df.iloc[:, 6*u+4].sort_values(ascending=False).reset_index()
    
    df.iloc[:, 6*u+5] = zyz() + djm_zjd() + fyz_zjd() # 干脆面
    s6 = df.iloc[:, 6*u+5].sort_values(ascending=False).reset_index()
    
    df_all = pd.concat([s1,s2,s3,s4,s5,s6], axis=1)
    df_all.to_excel(df.columns[6*u][0]+'正负因子2.xlsx')



df.to_excel('全国正负因子-河南2.xlsx')
# df2.to_excel('ts2.xlsx')

