# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 09:59:36 2018

@author: jasonai
"""

import numpy  as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
# from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score #, mean_squared_error


# PCA降维
def proc_pca(df):
    # 数据标准化
    # df = df_merge
    df.fillna(0, inplace=True)
    scaler = StandardScaler().fit(df.values)  # sklearn的标准化类

    """
    暂时不做数据拆分
    # random_state：可以为整数、RandomState实例或None，默认为None
    # 若为None时，每次生成的数据都是随机，可能不一样,若为整数时，每次生成的数据都相同
    train_data, test_data = train_test_split(df.values, test_size=0.3)
    X_train, y_train = scaler.transform(train_data)[:, :-1], scaler.transform(train_data)[:, -1]
    X_test, y_test = scaler.transform(test_data)[:, :-1], scaler.transform(test_data)[:, -1]
    """

    X_train, y_train = scaler.transform(df.values)[:, :-1], scaler.transform(df.values)[:, -1]
    # 主成分分析
    pca = PCA(n_components=2)
    X_train_pca = pca.fit_transform(X_train)
    # 线性回归
    linreg = LinearRegression()
    linreg.fit(X_train_pca, y_train)
    y_pred = linreg.predict(X_train_pca)
    R2 = r2_score(y_train, y_pred)
    # 预估与实际的比值
    mean = scaler.mean_  # 平均值，原真实数据用
    std = np.sqrt(scaler.var_)  # 标准差，还原真实数据用
    y_pred_restore = y_pred * std[-1] + mean[-1]
    predvsReal = y_pred_restore / df.values[:, -1]

    return predvsReal, R2

def proc_onlyLnr(df):
    # 数据标准化
    df.fillna(0, inplace=True)
    scaler = StandardScaler().fit(df.values)  # sklearn的标准化类
    
    X_train, y_train = scaler.transform(df.values)[:, :-1], scaler.transform(df.values)[:, -1]

    # 线性回归
    linreg = LinearRegression()
    linreg.fit(X_train, y_train)
    y_pred = linreg.predict(X_train)
    R2 = r2_score(y_train, y_pred); print(R2)
    # 预估与实际的比值
    mean = scaler.mean_  # 平均值，原真实数据用
    std = np.sqrt(scaler.var_)  # 标准差，还原真实数据用
    y_pred_restore = y_pred * std[-1] + mean[-1]
    predvsReal = y_pred_restore / df.values[:, -1]
    return predvsReal, R2

def main(province='湖北省', period=3):
    df_factor = pd.read_excel('%s各商圈地理因子数据.xlsx' % province, index_col=0)
    df_sale = pd.read_excel('%sKSF各商圈TT&MT出货.xlsx' % province, index_col=0)
    df_factor['学校'] = df_factor[['小学', '中学', '高等院校']].sum(axis=1)
    category = [i+'.{}'.format(period-1) for i in ['容器面', '高价袋','中价面','平低价','干脆面']]
    df_sale = df_sale[category]
    df_sale['整体.{}'.format(period-1)] = df_sale.sum(axis=1)
    df_merge = pd.concat([df_factor, df_sale['整体.{}'.format(period-1)]], axis=1)
    """
    # 只考虑8个筛选过的正负因子，最终R方为0.86,小于全部因子的0.91，补位使用
    # 获取相应省份的正负因子用
    df_mapt = pd.read_excel('%s各地区正负因子.xlsx' % province, sheetname='省份-地区对应表', index_col=0)
    df_pninfo = pd.read_excel('%s各地区正负因子.xlsx' % province, sheetname='各地区正负因子系数', index_col=0)
    pn_list = list(df_pninfo.loc[df_mapt.loc[province]]['整体'])
    df_factor2 = df_factor[pn_list]
    df_merge2 = pd.concat([df_factor2, df_sale['整体.{}'.format(period-1)]], axis=1)
    """
    predvsReal, R2 = proc_pca(df_merge)

    