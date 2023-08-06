import os
import sys
import numpy as np
import pandas as pd
import xlwings as xw


# 必用表头列表
CODE = 'CODE'
city_tag='S1'
sex_tag='S4'
age_tag='RES5'
rsjd_tag = 'rsjd'
list_essential1 = [CODE, city_tag, sex_tag, age_tag, rsjd_tag]
brand_list = ['肯德基', '德克士', '麦当劳', '华莱士', '汉堡王', '其他', '必胜客']
advertising_list = ['门店海报', '电视广告', '网络视频网站', '公交车候车亭', '公交车车身', '楼宇电梯广告', '微信', '微博', '其他，请注明', '不记得（与其他选项互斥）']


# 提取QA1和QA2
def extract_data1(qtag_list):
    # 这里加入'CODE',以便统计每个分组的总数
    qtag_list.insert(0, CODE)
    # 按不同类别进行分组
    gb_city = df.groupby(city_tag)
    gb_sex = df.groupby(sex_tag)
    gb_age = df.groupby(age_tag)
    df_city = gb_city.count().loc[:, qtag_list]
    # 基于df_city数据计算sheet <2.外食情况> 周期数据
    df_period = df_city
    # 使用各城市权重进行校正
    df_period1 = df_weight.merge(df_period, left_index=True,right_index=True)
    df_period2 = df_period1.drop(['权重', CODE], axis=1).apply(lambda x: x*df_period1['权重'])
    total_list = list(df_period2.sum() / len(df))   # base
    # 在列表开头部分插入总问卷数Base
    total_list.insert(0, df_period1[CODE].sum())
    # 计算每个城市的问卷数
    df_city = df_city.T
    df_city = pd.concat([pd.DataFrame(df_city.loc[CODE]).T,df_city.drop(CODE).apply(lambda x: x / df_city.loc[CODE], axis=1)])
    # 计算不同性别分布
    df_sex = gb_sex.count().loc[:, qtag_list].T
    df_sex = pd.concat([pd.DataFrame(df_sex.loc[CODE]).T,df_sex.drop(CODE).apply(lambda x: x / df_sex.loc[CODE], axis=1)])
    # 计算不同年龄段分布
    df_age = gb_age.count().loc[:, qtag_list].T
    df_age = pd.concat([pd.DataFrame(df_age.loc[CODE]).T,df_age.drop(CODE).apply(lambda x: x / df_age.loc[CODE], axis=1)])
    # 按'人生阶段'进行分组
    gb_rsjd = df.groupby(rsjd_tag)
    df_rsjd = gb_rsjd.count().loc[:, qtag_list].T
    df_rsjd = pd.concat([pd.DataFrame(df_rsjd.loc[CODE]).T,df_rsjd.drop(CODE).apply(lambda x: x / df_rsjd.loc[CODE], axis=1)])

    return total_list, df_city, df_sex, df_age, df_rsjd


# 从excel中提取含显著性标记的数字矩阵, col_num指填入列的
def extract_digit(sht, period_num, row_num, col_num, vertical_length, data_list):
    df_digit = pd.DataFrame(sht.range((row_num, col_num),(row_num+vertical_length, col_num+period_num-1)).value)
    # 去除非数字字符串，提取数字
    def format_data(x):
        if '%(' in str(x):
            x = float(x.split('%(')[0]) / 100
        return x
    df_digit = df_digit.applymap(format_data)
    # 将字符串'-'和0 替换为缺失值NaN，确保计算平均值时不考虑数据缺失的样本
    df_digit.replace('-', np.nan, inplace=True)
    df_digit.replace('0', np.nan, inplace=True)
    df_digit[period_num-1] = data_list
    base_temp = list(df_digit.loc[0])  # 注：base_temp为列表类型时，写入excel表时才会按行的方向输入
    df_digit_percent = df_digit.drop(0)

    return df_digit_percent, base_temp


def mark_significance(df_percent, base_temp, sht, row_num, col_num):

    # Z-test函数
    def ztest(p1, p2, n1, n2):
        z = abs((p1 - p2) / np.sqrt((n1 * p1 + n2 * p2) * (n1 * (1 - p1) + n2 * (1 - p2)) / (n1 * n2) / (n1 + n2)))
        return z > 1.959963985

    df_percent.replace('-', np.nan, inplace=True)
    for index, row in enumerate(df_percent.values):
        p1_proc_list = []
        for index1, (p1, n1) in enumerate(zip(row, base_temp)):
            p1_proc = '%.0f' % (p1 * 100) + "%("  # 有显著的数值不保留小数点后有效数字
            tag_significance = False
            for index2, (p2, n2) in enumerate(zip(row, base_temp)):
                if p1 > p2:
                    if ztest(p1, p2, n1, n2):
                        # p1高于p2且显著时，在p1后面标记p2的位置
                        p1_proc = p1_proc + chr(index2+97).upper()
                        # 如果p1有经过标记处理，则tag_significance为True
                        tag_significance = True
            if tag_significance:
                p1_proc += ")"
            else:
                p1_proc = p1
            
            if type(p1_proc) == str:
                # 写入显著性数值
                sht.range(row_num+index+1, index1+col_num).value = p1_proc
                sht.range(row_num+index+1, index1+col_num).color = (253,245,230)
            else:
                if np.isnan(p1_proc): # 判断缺失值的唯一方法,注意np.isnan('94%(D)')会报错
                    # 写入缺失数据
                    p1_proc = '-'
                    sht.range(row_num+index+1, index1+col_num).value = p1_proc
                    sht.range(row_num+index+1, index1+col_num).color = (169,169,169)
                else:
                    sht.range(row_num+index+1, index1+col_num).value = p1_proc
                    sht.range(row_num+index+1, index1+col_num).color = (255,255,255)


def period_proc1(qtag, sht, period_num, row_num, col_num_starting, vertical_length, total_list):
    # 获取各周期数据
    period_file = '%s_period_data.xlsx' % qtag
    if os.path.exists(period_file):
        df_total = pd.read_excel(period_file, usecols=period_num-2)
        df_total[period_num-1] = data_list
        df_total_percent, total_temp = df_total.drop(0), list(df_total.loc[0])
    else:
        df_total_percent, total_temp = extract_digit(sht, period_num, row_num, col_num_starting, vertical_length, total_list)
    
    # 加入新周期total信息时，需保存信息数据
    df_total = pd.concat([pd.DataFrame(total_temp).T, df_total_percent])
    #======df_total.to_excel(period_file, index=False)
    # 计算sheet Total列数据
    total_percent_list = []
    df_total2 = df_total_percent.apply(lambda x: x * total_temp, axis=1)
    for row in df_total2.values:
        i_sum, j_sum = 0, 0
        for i, j in zip(row, total_temp):
            if i > 0:
                i_sum += i
                j_sum += j
        total_percent_list.append(i_sum / j_sum)

    total_percent_list.insert(0, sum(total_temp))
    # 将df_total['sum']列写入sheet <2.外食情况>的 Total列
    sht.range(row_num, col_num_starting-1).options(transpose=True).value = total_percent_list
    # 写入Base行
    sht.range(row_num, col_num_starting).value = total_temp
    # 标记显著性数值，并写入sheet <2.外食情况>
    mark_significance(df_total_percent, total_temp, sht, row_num, col_num_starting)


# 各维度分析问卷结果
def dimension_proc(df_dimens, complete_dimens_list, vertical_length):
    for index, dimens in enumerate(complete_dimens_list):
        try:
            dimens_list = list(df_dimens[dimens])
        except:
            # dimens_list包含base数据，因此行数为vertical_length + 1
            dimens_list = ['-'] * (vertical_length + 1)
        if not index:
            df_dimens_proc = pd.DataFrame(dimens_list)
        else:
            df_dimens_proc[index] = dimens_list
    return df_dimens_proc


# 处理城市、性别、年龄段和人生阶段
def csar_proc1(qtag, sht, period_num, row_num, col_num_starting, vertical_length, df_city, df_sex, df_age, df_rsjd):
    # 按Excel顺序填入城市信息
    complete_city_list = ['成都', '哈尔滨', '西安', '郑州', '福州', '杭州']
    df_city_proc = dimension_proc(df_city, complete_city_list, vertical_length)
    for index, column in enumerate(df_city_proc.columns):
        # city_file = '%s_period_%s_data.xlsx' % qtag 这个功能后面再添加
        # 使用col_num2跟踪移动列
        col_num2 = col_num_starting + period_num * (index + 1)
        df_digit_percent, base_temp = extract_digit(sht, period_num, row_num, col_num2, vertical_length, df_city_proc[column])
        # 先写入base数据
        sht.range(row_num, col_num2).value = base_temp
        # 标记显著性数值，并写入sheet <2.外食情况>
        mark_significance(df_digit_percent, base_temp, sht, row_num, col_num2)

    # 按顺序填入性别信息，***性别没有考虑缺失数据的情况
    complete_sex_list = ['男性', '女性']
    df_sex_proc = dimension_proc(df_sex, complete_sex_list, vertical_length)
    for column in df_sex_proc.columns:
        index += 1  # 使用col_num2跟踪移动列
        col_num2 = col_num_starting + period_num * (index + 1)
        df_digit_percent, base_temp = extract_digit(sht, period_num, row_num, col_num2, vertical_length, df_sex_proc[column])
        # 先写入base数据
        sht.range(row_num, col_num2).value = base_temp
        # 标记显著性数值，并写入sheet <2.外食情况>
        mark_significance(df_digit_percent, base_temp, sht, row_num, col_num2)

    # 按顺序填入各年龄段信息
    complete_age_list = ['15-19岁', '20-24岁', '25-29岁', '30-34岁', '35-39岁']
    df_age_proc = dimension_proc(df_age, complete_age_list, vertical_length)
    for column in df_age_proc.columns:
        index += 1  # 使用col_num2跟踪移动列
        col_num2 = col_num_starting + period_num * (index + 1)
        df_digit_percent, base_temp = extract_digit(sht, period_num, row_num, col_num2, vertical_length, df_age_proc[column])
        # 先写入base数据
        sht.range(row_num, col_num2).value = base_temp
        # 标记显著性数值，并写入sheet <2.外食情况>
        mark_significance(df_digit_percent, base_temp, sht, row_num, col_num2)

    # 按人生阶段填入各年龄段信息
    complete_rsjd_list = ['青少年&学生', '青年', '壮年', '家庭']
    df_rsjd_proc = dimension_proc(df_rsjd, complete_rsjd_list, vertical_length)
    for column in df_rsjd_proc.columns:
        index += 1  # 使用col_num2跟踪移动列
        col_num2 = col_num_starting + period_num * (index + 1)
        df_digit_percent, base_temp = extract_digit(sht, period_num, row_num, col_num2, vertical_length, df_rsjd_proc[column])
        # 先写入base数据
        sht.range(row_num, col_num2).value = base_temp
        # 标记显著性数值，并写入sheet <2.外食情况>
        mark_significance(df_digit_percent, base_temp, sht, row_num, col_num2)


def processing_type1(qtag, sht, period_num, row_num, col_num_starting):
    ## col_num_starting为起始单元格的列
    qtag_list = list(df_qa.loc[qtag].dropna())
    vertical_length = len(qtag_list)
    total_list, df_city, df_sex, df_age, df_rsjd = extract_data1(qtag_list)
    # 处理并填入"周期"信息
    period_proc1(qtag, sht, period_num, row_num, col_num_starting, vertical_length, total_list)

    csar_proc1(qtag, sht, period_num, row_num, col_num_starting, vertical_length, df_city, df_sex, df_age, df_rsjd)


def BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num):
    global wb, df, df_qa, df_weight, Base
    # 提取问卷数据
    ## 打开问卷信息文件，该数据已经清洗过 
    df = pd.read_excel(filepath2)
    ## 提取问卷题目编号信息文件，如未来题目有变动，需更新此文件信息
    df_qa = pd.read_excel(filepath3, index_col=0)
    ## 获取配额/权重
    df_weight = pd.read_excel(filepath4, index_col=0)
    Base = len(df) # Base即为行数，也就是问卷数
    # 给"人生阶段"打标签
    # 统计“人生阶段”，青少年&学生（消费者15-24岁，没有小孩或小孩2岁以下）;青年（消费者25-29岁，没有小孩或小孩2岁以下）;
    # 壮年（消费者30-39岁，没有小孩或小孩2岁以下）;家庭（小孩3岁以上）
    # 第一步：给150份问卷打标签
    df[rsjd_tag] = '家庭'
    df.loc[(df.S5.isin(['15-19岁', '20-24岁'])) & df.D2.isin(['未婚','已婚，无小孩','已婚，小孩0岁~2岁']), rsjd_tag] = '青少年&学生'
    df.loc[(df.S5 == '25-29岁') & df.D2.isin(['未婚','已婚，无小孩','已婚，小孩0岁~2岁']), rsjd_tag] = '青年'
    df.loc[(df.S5.isin(['30-34岁', '35-39岁'])) & df.D2.isin(['未婚','已婚，无小孩','已婚，小孩0岁~2岁']), rsjd_tag] = '壮年'

    # 统计各标签的base
    df_base = df.loc[:, list_essential1]
    city_base = pd.pivot_table(df_base, columns=[city_tag], values=[CODE], aggfunc=np.size).loc[CODE]
    sex_base = pd.pivot_table(df_base, columns=[sex_tag], values=[CODE], aggfunc=np.size).loc[CODE]
    age_base = pd.pivot_table(df_base, columns=[age_tag], values=[CODE], aggfunc=np.size).loc[CODE]
    rsjd_base = pd.pivot_table(df_base, columns=[rsjd_tag], values=[CODE], aggfunc=np.size).loc[CODE]

    # 打开Excel程序
    app=xw.App(visible=True,add_book=False)
    # 打开已存在的文件
    wb = app.books.open(filepath1)

    # 读取<2.外食情况> sheets
    sht2 = wb.sheets['2.外食情况']
    # 将QA1和QA2的数据填入<2.外食情况> sheets
    processing_type1('QA1', sht2, period_num, 6, 3)
    processing_type1('QA2', sht2, period_num, 39, 3)


if __name__ == "__main__":
    BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num)





