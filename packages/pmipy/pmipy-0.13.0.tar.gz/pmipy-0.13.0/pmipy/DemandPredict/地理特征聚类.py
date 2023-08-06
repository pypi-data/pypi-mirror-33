# -*- coding: utf-8 -*-
"""
地理特征聚类
Created on Thu Feb  1 22:09:50 2018

@author: jasonai
"""

import pandas as pd
from sklearn.cluster import KMeans

df = pd.read_excel('各省市区点评餐饮点数据.xlsx', index_col=[0,1,2])
df.fillna(0, inplace=True)

df2 = df.apply(lambda x: x / df.sum(axis=1))
df2.dropna(inplace=True)

#设定不同k值以运算
for k in range(5,6):
    clf = KMeans(n_clusters=k, max_iter=1000) #设定k ！！！这里就是调用KMeans算法
    s = clf.fit(df2) #加载数据集合
    numSamples=len(df2)
    centroids = clf.labels_  # 每个样本所属的簇
    #print(centroids) #显示中心点
    print(clf.inertia_)  #显示聚类效果

df2['类别'] = centroids