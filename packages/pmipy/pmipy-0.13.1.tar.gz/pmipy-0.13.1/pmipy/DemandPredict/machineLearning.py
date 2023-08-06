# -*- coding: utf-8 -*-
"""
Created on Fri Apr  6 09:59:36 2018

@author: jasonai
"""

import numpy  as np
import pandas as pd
from pmipy import log
from pmipy import pmi
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
# from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score #, mean_squared_error


try:
    config = pmi.ConfigHandler(__file__)
except NameError:
    config = pmi.ConfigHandler('calKSFshipment.py')
mt = config.read_configure('Manifest.ini', 'tag')
# 数据库或数据表名称
dbName = mt['dbName']
ksfSales = mt['ksfSales']
infoName = mt['infoName']
regionFactor = mt['regionFactor']
areaFactor = mt['areaFactor']
predVsReal = mt['predVsReal']
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
predRealRatio = mt['predRealRatio']
# 区分不同商圈商圈名相同的额外信息
busAdInfo1 = [marketingCompany, salesDepartment, businessArea]
# 内容
updateTime = mt['updateTime']
periodTag = mt['periodTag'] # 1705-1804
logger = log.createLogger(__name__)
cm = pmi.ConnMysql(dbName)


# PCA降维
def pca_Lnr(df):
    # 对缺失值进行填0处理
    df.fillna(0, inplace=True)
    # 纵向数据标准化
    df_std = df.apply(lambda x: (x-x.mean()) / x.std())
    # 获取外卖销量数据
    waimai_std = df_std['外卖销量']
    # 去除跟外卖相关的数据
    cols = list(df)
    cols2 = [i for i in cols if '外卖' in i ]
    df_std.drop(cols2, axis=1, inplace=True)
    """
    暂时不做数据拆分
    # random_state：可以为整数、RandomState实例或None，默认为None
    # 若为None时，每次生成的数据都是随机，可能不一样,若为整数时，每次生成的数据都相同
    train_data, test_data = train_test_split(df.values, test_size=0.3)
    X_train, y_train = scaler.transform(train_data)[:, :-1], scaler.transform(train_data)[:, -1]
    X_test, y_test = scaler.transform(test_data)[:, :-1], scaler.transform(test_data)[:, -1]
    """
    X_train, y_train = df_std.iloc[:, :-1], df_std.iloc[:, -1]
    # 去除含缺失值列
    X_train = X_train.dropna(axis=1, how='any')
    # 主成分分析
    pca = PCA(n_components=3)
    X_train_pca = pca.fit_transform(X_train)
    comp = pca.explained_variance_ratio_
    logger.info("地理因子的第一组成分信息量为{:0.3};第二组成分信息量为{:0.3}".format(comp[0],comp[1]))
    # 线性回归
    linreg = LinearRegression()
    linreg.fit(X_train_pca, y_train)
    y_pred = linreg.predict(X_train_pca)
    R2 = r2_score(y_train, y_pred)
    ## 考虑外卖的负面影响，对预测的市场量进行加权修正,目前暂时将外卖的权重设为0.1
    y_pred_ad = y_pred * 0.9 - waimai_std * 0.1
    
    # 预估与实际的比值
    # 计算实际值的均值和标准差
    mean_y = df.iloc[:, -1].mean()
    std_y = df.iloc[:, -1].std()
    y_pred_restore = y_pred_ad * std_y + mean_y
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
    R2 = r2_score(y_train, y_pred)
    # 预估与实际的比值
    mean = scaler.mean_  # 平均值，原真实数据用
    std = np.sqrt(scaler.var_)  # 标准差，还原真实数据用
    y_pred_restore = y_pred * std[-1] + mean[-1]
    predvsReal = y_pred_restore / df.values[:, -1]
    return predvsReal, R2


# XX zoneManifest为存放大地区(比如晋蒙)-省份名单的清单文件路径--此方法暂时不考虑
# 以行销公司为单元进行机器学习
def main(exMethod):
    # 从数据库中获取各商圈的因子
    sql_factor = "select {},{},{},{},{} from {} where {}='{}'".format(marketingCompany,
                         salesDepartment, businessArea, factorType, factorNum, areaFactor, timeCol, periodTag)
    df_factor = pd.read_sql(sql_factor, cm.engine)
    # 获取康师傅指定年份的出货/销量数据,，单位为包
    sql_ksf = "select {},{},{},{},{} from {} where {}='TT+MT' and {}='包' and {}='{}'".format(marketingCompany, 
                      salesDepartment, businessArea, priceType, sale, ksfSales, channel, unit, timeCol, periodTag)
    df_ksf = pd.read_sql(sql_ksf, cm.engine)
    # 对地理因子进行pivot
    df_factor2 = pd.pivot_table(df_factor, index=busAdInfo1, columns=factorType, values=factorNum)
    df_ksf2 = pd.pivot_table(df_ksf, index=busAdInfo1, columns=priceType, values=sale) # .reset_index()
    """# 训练时确保priceType的sales为0的样本数不超过30%
    listCompx1 = []
    listCompx2 = []
    for col in list(df_ksf2):
        if len(df_ksf2[df_ksf2[col]==0]) < 0.3 * len(df_ksf2):
            listCompx1.append(col)
        else:
            listCompx2.append(col)"""
    
    pricetype_all = list(df_ksf2)
    # 分别对各地区进行处理
    def _proc(df_factor, df_sales, scope):
        df_s = df_sales[df_sales.index.get_level_values(marketingCompany)==scope]
        # 分别取某品类销量
        for index, pricetype in enumerate(pricetype_all):
            df_s2 = df_s[[pricetype]]
            df = pd.merge(df_factor, df_s2, 
                          left_index=True,right_index=True, how='inner') # 取销量和因子数据框的交集
            if len(df_s2[df_s2[pricetype]==0]) < 0.3 * len(df_s2): # 训练时确保priceType的sales为0的样本数不超过30%
                predvsReal, R2 = pca_Lnr(df)
                logger.info("{}地区{}预估值与实际值的判定系数为{:0.3}".format(scope, pricetype, R2))
                predvsReal.name = pricetype
                predvsReal = predvsReal.reset_index()
            else:
                logger.warning("{}地区{}无销量信息！".format(scope, pricetype))
                predvsReal = (df_s[pricetype]+1) / (df_s[pricetype]+1) # 不做机器学习训练时，默认比值为1
                predvsReal = predvsReal.reset_index()
            if not index:
                df_pvr = predvsReal 
            else:
                df_pvr = pd.merge(df_pvr, predvsReal, on=busAdInfo1)
            # 可考虑缺失值填1处理
            #df_pvr['地区'] = marketingCompany
        return df_pvr

    # 各种品类/规格别的预估
    try:
        for i, mc in enumerate(df_ksf2.index.get_level_values(0).drop_duplicates()):
            try:
                df_pvr = _proc(df_factor2, df_ksf2, mc)
                if not i:
                    df_final = df_pvr 
                else:
                    df_final = pd.concat([df_final, df_pvr])
            except TypeError:
                logger.info("存在“无行销公司”公司名称的情况！")
    except MemoryError:
        logger.warning("内存不足！请检查是否有商圈重复问题！")
        raise SystemExit
    
    # 使用np.nan替换np.inf
    df_final = df_final.replace(-1 * np.inf, np.nan)
    df_final = df_final.replace(np.inf, np.nan).set_index(busAdInfo1)
    df_final = df_final.stack().reset_index()
    df_final.rename(columns={'level_3':priceType, 0:predRealRatio}, inplace=True)
    df_final[timeCol] = periodTag
    cm.toMysql(predVsReal, df_final, updateTime, exMethod)
    logger.info("完成各商圈各品类（价格带）的市场预估！")
    
    """
    # 只考虑8个筛选过的正负因子，最终R方为0.86,小于全部因子的0.91，补位使用
    # 获取相应省份的正负因子用
    df_mapt = pd.read_excel('%s各地区正负因子.xlsx' % province, sheetname='省份-地区对应表', index_col=0)
    df_pninfo = pd.read_excel('%s各地区正负因子.xlsx' % province, sheetname='各地区正负因子系数', index_col=0)
    pn_list = list(df_pninfo.loc[df_mapt.loc[province]]['整体'])
    df_factor2 = df_factor[pn_list]
    df_merge2 = pd.concat([df_factor2, df_sale['整体.{}'.format(period-1)]], axis=1)
    """
 
if __name__ == '__main__':
    exMethod = mt['exMethod']
    exMethod2 = 'append'
    main(exMethod)


