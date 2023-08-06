import os, sys
import numpy as np
import pandas as pd


def merging_data(df, province, col_essential):
    featrue_series = df.loc[province].groupby('一级特征').first()['文件名']
    feature1_list = list(featrue_series.index)
    ftfile_list = list(featrue_series.values)
    df.fillna(0, inplace=True)
    sub_feature_index = list(df.columns).index('子特征1')
    feature_ori_index = list(df.columns).index('特征原名')
    for index, (feature1, feature1_filename) in enumerate(zip(feature1_list, ftfile_list)):
        # 从一级特征对应文件读取数据框
        # 判断工作目录中是否存在region合并化后的文件
        merging_filename = os.path.splitext(feature1_filename)[0] + '_region.xlsx'

        if os.path.exists(merging_filename):
            df1 = pd.read_excel(merging_filename, index_col=[0, 1, 2])
        else:
            # 解决直属县级市的问题
            # 判断文件类型，目前只考虑了'xlsx'和'csv'
            if feature1_filename.split('.')[-1] == 'csv':
                df1 = pd.read_csv(feature1_filename, engine='python')
            else:
                df1 = pd.read_excel(feature1_filename)

            # 解决省直属的问题
            if len(col_essential) > 2:
                df1[col_essential[2]] = np.where(df1[col_essential[2]].isnull(), df1[col_essential[1]], df1[col_essential[2]])
            df1 = df1.groupby(col_essential).sum()
            df1.to_excel(merging_filename)
        
        # 判断是否存在需通过子特征合并处理的特征，如存在则需先合并子特征并存于新的特征列
        df_s1 = df.loc[province][df.loc[province]['一级特征'] == feature1]
        for i in df_s1.values:
            if i[sub_feature_index]:
                df1[i[feature_ori_index]] = df1.loc[:, i[sub_feature_index:]].sum(axis=1)
        # 根据'特征原名'列提取各维度特征
        feature_list = list(df_s1['特征原名'])
        feature_change_list = list(df_s1['使用特征名'])
        df2 = df1.loc[:, feature_list]
        # 更改特征名
        df2.columns = feature_change_list
        if not index:
            df3 = df2
        else:
            df3 = df3.merge(df2, left_index=True, right_index=True, how='outer')

    # 使用0填充缺失值
    df3.fillna(0, inplace=True)
    df3.to_excel('%s_特征.xlsx' % province)


if __name__ == "__main__":
    feature_file = '湖北需求预估使用的特征.xlsx'
    province = '湖北'
    df = pd.read_excel(feature_file, index_col=[0])  # 将'省'列设为索引
    merging_data(df, province, col_essential)

