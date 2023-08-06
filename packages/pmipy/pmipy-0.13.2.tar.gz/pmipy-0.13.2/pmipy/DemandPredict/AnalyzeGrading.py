# Analysis of Business Circle 's Grading Rationality Based on Real Sales

import os
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from pyplotz.pyplotz import PyplotZ


# 解决matplotlib和seaborn绘图中文乱码的问题（坐标轴元素乱码）
zhfont1 = mpl.font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf')


def boxplot(df, x, y, data_path, hue=None):
    pltz = PyplotZ()
    pltz.enable_chinese()  # 解决坐标标签乱码的问题
    sns.set_style("white")  # sns.set(style="ticks")
    plt.xticks(fontproperties=zhfont1)
    plt.yticks(fontproperties=zhfont1)
    sns.boxplot(x=x, y=y, hue=hue, data=df, palette="PRGn")
    pltz.xlabel(x)
    pltz.ylabel(y)
    sns.swarmplot(x=x, y=y, hue=hue, data=df)
    plt.savefig("%s/%s_swarmplot" % (data_path, y))
    plt.close()


def analyze_grading(data_path, data_file, grade, sale, tag, province):
    # 读取各商圈销量数据
    df = pd.read_excel(os.path.join(data_path, data_file), index_col=0)
    df.sort_values(by=grade, inplace=True)
    boxplot(df, grade, sale, data_path)

    # 根据上图（箱线图）个等级的销量分布，
    # 仅考虑整体平均千箱数据，通过商圈等级进行分组，最终通过四分位和最小值找出不合理的分级商圈
    df2 = df.loc[:, [grade, sale]]
    gb = df2.groupby(grade)

    # 获取各等级的下四分位Q1销量数据
    df_q1 = gb.quantile(q=0.25)

    # 获取各等级的中位Q2销量数据
    df_q2 = gb.quantile(q=0.5)

    # 获取各等级的上四分位Q3销量数据
    df_q3 = gb.quantile(q=0.75)

    """
    分析商圈分级合理性的方法1：
    某等级的商圈销量超过上一级的销量中位值即视为分级过低，
    而当销量小于下一级的销量中位值即视为分级过高。

    分析商圈分级合理性的方法2：
    从箱线图显示的6个等级销量分布结果中，我们可以看出1级商圈和2级商圈的销量拉的最开，而2级以下的等级，每个级别都存在较多的销量重叠。
    根据分布结果，我们拟定：
    1级商圈中，销量低于2级上四分位的商圈标记为不合理分级的商圈；
    2级商圈中，销量低于3级下四分位的商圈标记为不合理分级的商圈；
    3级商圈中，销量低于4级下四分位的商圈标记为不合理分级的商圈；
    4级商圈中，销量低于5级下四分位的商圈标记为不合理分级的商圈；
    5级商圈中，销量低于6级下四分位的商圈标记为不合理分级的商圈；
    2级商圈中，销量超过1级下四分位的商圈标记为不合理分级的商圈；
    3级商圈中，销量超过2级中位数的商圈标记为不合理分级的商圈；
    4级商圈中，销量超过3级上四分位的商圈标记为不合理分级的商圈；
    5级商圈中，销量超过4级上四分位的商圈标记为不合理分级的商圈；
    6级商圈中，销量超过5级上四分位的商圈标记为不合理分级的商圈；
    """
    evaluate_tag = []
    for grade, sale in df2.values:
        if grade == '1级':
             if sale < df_q2.loc['2级'].values:
                 evaluate_tag.append('分级过高')
             else:
                 evaluate_tag.append('分级合理')
        elif grade == '6级':
                 if sale > df_q2.loc['5级'].values:
                    evaluate_tag.append('分级过低')
                 else:
                    evaluate_tag.append('分级合理')
        else:
            last_grade = str(int(grade[0]) - 1) + '级'
            next_grade = str(int(grade[0]) + 1) + '级'
            if sale < df_q2.loc[next_grade].values:
                evaluate_tag.append('分级过高')
            elif sale > df_q2.loc[last_grade].values:
                evaluate_tag.append('分级过低')
            else:
                evaluate_tag.append('分级合理')
    df2['%s分析分级合理性' % tag] = evaluate_tag
    df2.to_excel('%s/基于%s分析%s商圈分级合理性.xlsx' % (data_path, tag, province))

"""
    方法2：
    for grade, sale in df2.values:
        if grade == '1级':
            if sale < df_q3.loc['2级'].values:
                evaluate_tag.append('分级过高')
            else:
                evaluate_tag.append('分级合理')
        elif grade == '2级':
            if sale < df_q1.loc['3级'].values:
                evaluate_tag.append('分级过高')
            elif sale > df_q3.loc['1级'].values:
                evaluate_tag.append('分级过低')
            else:
                evaluate_tag.append('分级合理')
        elif grade == '3级':
            if sale < df_q1.loc['4级'].values:
                evaluate_tag.append('分级过高')
            elif sale > df_q2.loc['2级'].values:
                evaluate_tag.append('分级过低')
            else:
                evaluate_tag.append('分级合理')
        elif grade == '4级':
            if sale < df_q1.loc['5级'].values:
                evaluate_tag.append('分级过高')
            elif sale > df_q3.loc['3级'].values:
                evaluate_tag.append('分级过低')
            else:
                evaluate_tag.append('分级合理')
        elif grade == '5级':
            if sale < df_q1.loc['6级'].values:
                evaluate_tag.append('分级过高')
            elif sale > df_q3.loc['4级'].values:
                evaluate_tag.append('分级过低')
            else:
                evaluate_tag.append('分级合理')
        else:  # 6级
            if sale > df_q3.loc['5级'].values:
                evaluate_tag.append('分级过低')
            else:
                evaluate_tag.append('分级合理')
"""


if __name__ == '__main__':
    data_path = '整体平均千箱_2017-12-04-15h00m'
    data_file = '整体平均千箱_2017-12-04-15h00m_综合.xlsx'
    grade = '客户形态对应的商圈等级'
    sale = '预估销量'
    tag = '整体预估销量'
    analyze_grading(data_path, data_file, grade, sale, tag)
    analyze_grading('.', '湖北各商圈销量.xlsx', grade, '整体平均千箱', '整体平均销量')
