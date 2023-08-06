# -*- coding: utf-8 -*-
"""
Created on Sat Apr 14 11:23:05 2018

@author: jasonai
"""

import os
import numpy as np
import pandas as pd
from pmipy import log
from pmipy import pmi
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib as mpl


logger = log.createLogger(__name__)

def readXlsCsv(filePath):
    [path, file] = os.path.split(filePath)
    [fileName, fileSuffix] = os.path.splitext(file)
    if fileSuffix == '.xlsx' or fileSuffix == '.xls':
        df = pd.read_excel(filePath)
    elif fileSuffix == '.csv':
        try:
            df = pd.read_csv(filePath, engine='python')
        except pd.errors.ParserError: # csv为tab键分割的情况
            df = pd.read_csv(filePath, sep='\t', engine='python')
    else:
        logger.error("Please input csv or xlsx file!")
        raise SystemExit
        
    return df, path, fileName


# 对特征、标签进行预处理
class pretreatment(object):
    def __init__(self, featureFile, labelFile):
        self.featureFile = featureFile
        self.labelFile = labelFile
        # 输出文件的目录为存放特征文件的目录，文件名为特征文件名的拓展
        self.df_feature, self.path, self.feaName = readXlsCsv(featureFile)


    # 合并、简单处理特征文件和标签文件,并对标签进行二分类；colF和colL为特征和标签数据的索引列名（vlookup列）
    def featureLabel(self, colF='编号', colL='编号', label='label', border='mean'): 

        if not self.labelFile: # 判断是否指定了labelData文件路径，默认labelFile为''
            if label not in self.df_feature.columns: 
                logger.error("请指定存放标签数据表文件名/文件路径! <命令行提示：-f2 pathOfLabelFile >")
                raise SystemExit
            else:
                df_merge = self.df_feature
            self.labelName = 'onefile'
        else:
            [df_label, self.labelName] = readXlsCsv(self.labelFile)[::2]
            # df_label = readXlsCsv(self.labelFile)[0]
            df_merge = self.df_feature.merge(df_label[[colL, label]], left_on=colF, right_on=colL, how='inner')
    
        # 降序,确保1分类为1
        df_merge.sort_values(label, inplace=True)
        # 复制一份给df_featurelabel,用于其他模块做有监督特征分析时使用
        self.df_featurelabel = df_merge.copy()
        
        # 获取标签复杂度
        labelDul = df_merge[label].drop_duplicates()
        labelNum = len(labelDul)
        
        # 数值型标签处理,进行二分类
        try:
            # 如果发现数字型series只有两个值，我们暂时当中分类问题
            if labelNum == 2:
                raise TypeError
            
            logger.info("使用%s方法进行二分类数值型标签 ..." % border)
            if border == 'mean':
                df_merge['cls'] = np.where(df_merge[label] <= df_merge[label].mean(), 0, 1)
            elif border == 'median':
                df_merge['cls'] = np.where(df_merge[label] <= df_merge[label].median(), 0, 1)
            elif border == 'kmeans':
                from sklearn.cluster import KMeans
                estimator=KMeans(n_clusters=2)
                res=estimator.fit_predict(pd.concat([df_merge[label],df_merge[label]],axis=1))
                df_merge['cls'] = [abs(1-x) for x in res]
                # logger.exception('导入KMeans模块失败！')
            elif border == 'self':
                df_merge['cls'] = df_merge[self.labelFile]
            else:
                logger.error("%s方法获得二分类的分界值尚未开发，如有需求请联系开发人员<pmi-jasonai>!" % border)
                raise SystemExit
                
        except TypeError:
            if labelNum  > 2:
                logger.error("所得标签的数据类型为非数字型(dtype:object)，因此只能视为分类问题，但WOE特征选择算法暂时只考虑二分类问题！")
                raise SystemExit
            elif labelNum == 2:
                df_merge['cls'] = np.where(df_merge[label] == labelDul.values[0], 0, 1)
            else: # 如果标签只有1种值
                logger.warning("所获取的标签只有一种值，请仔细检查标签是否存在问题！")
                SystemExit
    
        return df_merge

    # 对特征进行缺失值处理  
    def missingValue(self, percent):
        series_list = []
        for col in self.df_feature.columns:
            series = self.df_feature[col]
            null_ratio = len(series[series.isnull()]) / len(series)
            if null_ratio > percent:
                logger.info("特征“{}”的缺失值占比达{:.1f}%,舍弃此特征".format(series.name, null_ratio * 100))
            else:
                # 暂时不做其他处理，未来有时间可能会在此加稀疏度之类的分析
                # series.fillna(0)
                series_list.append(series)
        self.df_feature = pd.concat(series_list, axis=1)
        return self.df_feature
        
    # 分析标签的复杂度,舍弃复杂度小于num的标签
    def analyzeComplex(self, label, num=None):
        # 如果没有提供复杂度要求
        if not num:
            num = 4
        series_list = []
        for col in self.df_feature.columns:
            series = self.df_feature[col]
            complexNum = len(series.drop_duplicates())
            if complexNum < num:
                if series.name != label:
                    logger.info("特征'{}'的复杂度为{}，小于指定的{},舍弃此特征".format(series.name, complexNum, num))
                else:
                    series_list.append(series)
            else:
                series_list.append(series)
        self.df_feature = pd.concat(series_list, axis=1)
        return self.df_feature


class featureWOE(object):
    def __init__(self, df):
        self.df = df

    # 对特征进行分组
    def getWOEandIV(self, groupNum=4, groupMeth=1):
        logger.info("对特征进行WOE编码和信息度IV值计算 ...")
        IV_list = []
        if groupMeth == 1:
            logger.info("使用等距法进行分{}组 ...".format(groupNum))
            sample_size = len(self.df)
            for feature in self.df.columns[:-2]: # 最后两列,'label'和'cls'列为标签相关列
                try:
                    df_uniF = self.df.sort_values(feature)
                except TypeError:
                    self.df[feature] = self.df[feature].astype('str')
                    df_uniF = self.df.sort_values(feature)
                df_uniF['group'] = np.arange(sample_size) // (sample_size / groupNum)
                WOE, IV = self.calWOEandIV(df_uniF)
                IV_list.append([feature, WOE, IV])
            
        elif groupMeth == 2:
            logger.info("使用自身分类法进行分组 ...")
            for feature in self.df.columns[:-2]:
                try:
                    df_uniF = self.df.sort_values(feature)
                except TypeError:
                    self.df[feature] = self.df[feature].astype('str')
                    df_uniF = self.df.sort_values(feature)
                WOE, IV = self.calWOEandIV(df_uniF, var=feature)
                IV_list.append([feature, WOE, IV])
        else:
            pass

        df_ouput = pd.DataFrame(IV_list, columns=['特征', 'WOE', 'IV'])
        df_ouput.sort_values('IV', ascending=False, inplace=True)
        
        return df_ouput
        

    def calWOEandIV(self, df_uniF, var='group', target='cls'):
        eps = 0.000001 # 以避免除以0
        gbi = pd.crosstab(df_uniF[var], df_uniF[target]) + eps
        gb = df_uniF[target].value_counts() + eps
        gbri = gbi / gb
        gbri['woe'] = np.log(gbri[1] / gbri[0])
        gbri['iv'] = (gbri[1] - gbri[0]) * gbri['woe']
        
        return gbri['woe'].to_dict(), gbri['iv'].sum()


# 输入的df需包含特征和标签
def correlationAnalysis(df, label, tag, path, aveMethod='median', method='kendall', cmap="RdYlGn", annot=False):
    # 解决保存图像是负号'-'显示为方块的问题
    mpl.rcParams['axes.unicode_minus'] = False
    dimension = len(df.columns) # 获取特征个数
    logger.info("使用{}分析{}个特征与标签的相关性 ...".format(method, dimension-1))
    # 计算各数值标签的均值（非数值型标签pandas.mean会自动忽略）
    # 确保无缺失值
    df = df.fillna(0)
    # 选择求均值的方法
    if aveMethod == 'median':
        df_feaMean = pd.DataFrame({'特征均值': df.median()})
    elif aveMethod == 'mean':
        df_feaMean = pd.DataFrame({'特征均值': df.mean()})
    else:
        logger("暂时未开发{}求均值的方法！".format(aveMethod))
        raise SystemExit
    corrmat = df.corr(method=method)
    # 将label列放第一列
    cols =list(corrmat)
    cols.insert(0, cols.pop(cols.index(label)))
    corrmat = corrmat.ix[:, cols]
    # 绘制热图，用于POC报告
    # 确保特征名在heatmap上不遗漏
    plt.figure(figsize=(dimension/4.3, dimension/5.3)) 
    sns.set(style="white", font="simhei")  #,font_scale=1.6)
    sns.heatmap(corrmat, square=False, linewidths=.5, annot=annot, cmap=cmap)
    # plt.xlabel(ylabel)
    plt.title(tag)
    plt.savefig(os.path.join(path,"%s_%s_heatmap" % (tag, method)), bbox_inches='tight', pad_inches=0.2, dpi=200)
    plt.close()
    # 添加特征均值信息
    corrmat2 = pd.merge(df_feaMean, corrmat, left_index=True, right_index=True, how='right')
    corrmat2.sort_values(label, ascending=False, inplace=True)
    corrmat2.to_excel(os.path.join(path,'%s_%s相关性分析.xlsx' % (tag, method)))
    
    return corrmat2


@pmi.execInfo()
def featureEngineering(featureFile, labelFile, colF, colL, label, border='mean', groupNum=4, compNum=4, 
                       groupMeth=1, file_ouput='', aveMethod='median', method='kendall', cmap="RdYlGn", annot=False):
    # 初始化pretreatment类
    pret = pretreatment(featureFile, labelFile)
    # 先进行特征预处理
    # 缺失值处理：去除缺失值超过60%的特征
    pret.missingValue(percent=0.6)
    # 去除复杂度低于样本数10分之一的特征
    pret.analyzeComplex(label, compNum)
    # 处理并合并标签
    df_fela = pret.featureLabel(colF, colL, label, border)
    # 初始化featureWOE类
    fw = featureWOE(df_fela)
    dfWOE = fw.getWOEandIV(groupNum, groupMeth)
    tag = pret.feaName + '_' + pret.labelName
    dfWOE.to_excel(os.path.join(pret.path, tag+'_woe.xlsx'), index=False)
    
    # 相关性分析
    correlationAnalysis(pret.df_featurelabel, label, tag, pret.path, aveMethod, method, cmap, annot)




if __name__ == '__main__':
    featureFile = 'E:\CloudStation\康饮商圈分析\零售饮料\Linx特征工程\LinxAddr_4_dianping.csv'
    labelFile = 'E:\CloudStation\康饮商圈分析\零售饮料\Linx特征工程\江苏super.xlsx'
    colF, colL, label = '编号', '店铺编号', '销售分数'
    featureEngineering(featureFile, labelFile, colF, colL, label)
