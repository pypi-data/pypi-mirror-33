import numpy as np
import pandas as pd
import os, sys
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from pyplotz.pyplotz import PyplotZ
from sklearn.preprocessing import MinMaxScaler


def interpreter(time_tag, sale_tag, sales_file_proc, province):
    zhfont1 = mpl.font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf')
    df = pd.read_excel(time_tag + "/%s_median.xlsx" % time_tag, index_col=0)
    # 去除训练次数，投票等信息
    df = df.loc[:, [sale_tag, '预估销量', '预估与实际比值']]
    try:
        df_grading = pd.read_excel(sales_file_proc, usecols=[0, 1], index_col=0)
    except Exception as err:
        print(err)  # 输出报错的原因
    df = df.merge(df_grading, left_index=True, right_index=True, how="left")  # 添加商圈分级信息，可能会产生缺失值

    """
    业绩结合分级的调整方案：
    # 计算每个商圈等级的中位数销量，使用中位数来判断商圈是否需要微调
    df_t1 = df[df['客户形态对应的商圈等级'].notnull()].loc[:, ['客户形态对应的商圈等级', sale_tag]]  # 去掉缺失等级信息的商圈
    df_grading_sale = df_t1.groupby('客户形态对应的商圈等级').median()
    grading_sale = df_grading_sale.to_dict()
    # 添加微调信息
    # df.columns: ['整体平均千箱', '预估销量', '预估与实际比值', '客户形态对应的商圈等级']
    suggest_list = []
    df.fillna('未知分级', inplace=True)
    for row in df.values:
        if row[3] != '未知分级':  # 客户形态对应的商圈等级非空缺时
            if row[2] >= 1.5:  # 先筛选出预估与实际比值大于等于1.5的商圈
                if row[3] == '1级':
                    suggest = '建议维持'
                else:
                    grading = str(int(row[3][0]) - 1) + row[3][1]
                    gs = grading_sale[sale_tag][grading]
                    suggest = '建议上调' if row[1] >= gs else '建议维持'
            elif row[2] <= 0.75:  # 筛选下调的第一步
                if row[3] == '6级':
                    suggest = '建议维持'
                else:
                    grading = str(int(row[3][0]) + 1) + row[3][1]
                    gs = grading_sale[sale_tag][grading]
                    gs2 = gs * 1.2  # 湖北省由于下调的商圈太少，我们将中位值提高20%
                    suggest = '建议下调' if row[1] <= gs2 else '建议维持'
            else:
                suggest = '建议维持'
        else:
            suggest = '信息缺失'
        suggest_list.append(suggest)
        """
    df['业绩表现'] = np.where(df['预估与实际比值'] > 1.5, '业绩还有上升空间', '业绩良好')
    # 为客户准备excel表
    df.to_excel(time_tag + "/%s_综合.xlsx" % time_tag)
    # 对df[sale_tag]列进行归一化而不是标准化
    df['sales_avg_norm'] = MinMaxScaler().fit_transform(df.loc[:, [sale_tag, '预估与实际比值']])[:, 0]
    df_maintain = df[(df['预估与实际比值'] > 0.9) & (df['预估与实际比值'] < 1.1)]
    df_up = df[df['业绩表现'] == '业绩还有上升空间']
    # df_down = df[df['业绩表现'] == '建议下调']
    df_factor = pd.read_excel(time_tag + '/%s_正负因子.xlsx' % time_tag)
    df_ocm = pd.read_excel('%s商圈OCM_%s.xlsx' % (province, sale_tag), index_col=0)
    df_ocm.fillna(0, inplace=True)
    param = list(df_factor["参数"].values)
    df_ocm_norm = MinMaxScaler().fit_transform(df_ocm.loc[:, param])
    df_ocm_norm = pd.DataFrame(df_ocm_norm, index=df_ocm.index, columns=param)

    def data_process(df_ocm_norm, df):
        df_concat = pd.concat([df_ocm_norm, df['sales_avg_norm']], axis=1, join='inner')
        df_proc = df_concat.apply(lambda x: x / df_concat['sales_avg_norm'])  # 标准化后，将各因子除以标准化的平均销量
        df_proc.drop('sales_avg_norm', axis=1, inplace=True)
        return df_proc

    df_maintain_proc = data_process(df_ocm_norm, df_maintain)
    df_maintain_proc.reset_index(inplace=True)
    for index, i in enumerate(param):
        df_maintain_proc['参数'] = i
        df_maintain_proc2 = df_maintain_proc.loc[:, ["商圈", '参数', i]]
        df_maintain_proc2.columns = ['商圈', '参数', 'value']
        # 去除极端异常值
        df_maintain_proc2 = df_maintain_proc2[(df_maintain_proc2['value'] < 8) & (df_maintain_proc2['value'] > -8)]

        df_maintain_proc3 = df_maintain_proc2 if not index \
            else df_maintain_proc3.append(df_maintain_proc2, ignore_index=True)

    df_up_proc = data_process(df_ocm_norm, df_up)
    # df_down_proc = data_process(df_ocm_norm, df_down)

    def data_visual(df, df_maintain, param, tag):
        sns.set_style("white")
        for i in df.index:
            pltz = PyplotZ()
            pltz.enable_chinese()
            plt.xticks(rotation='30', fontproperties=zhfont1)
            plt.plot((np.ones(10)) * 4.5, np.arange(-4, 6), linestyle="--")  # 绘制分割正负因子的虚线
            plt.scatter(np.arange(len(param)), df.loc[i].values, c='#CD2626', marker='*')  # 横坐标用len(param)代替param
            df_maintain2 = df_maintain
            sns.boxplot(x='参数', y='value', data=df_maintain2, fliersize=1.3, color="#48D1CC")
            pltz.xlabel('地理环境因子')
            pltz.title('%s_%s' % (i, tag))
            plt.savefig(os.path.join(time_tag, '%s_%s.png' % (i, tag)), bbox_inches='tight')
            plt.close()

    data_visual(df_up_proc, df_maintain_proc3, param, '业绩还有上升空间')
    # data_visual(df_down_proc, df_maintain_proc3, param, '建议下调')
    df_maintain_proc.drop(columns=['参数'], inplace=True)
    df_maintain_proc.set_index("商圈", inplace=True)
    df_final = pd.concat([df_maintain_proc, df_up_proc])  # df_down_proc,
    df_final = pd.concat([df_final, df.loc[:, ['sales_avg_norm', '业绩表现']]], axis=1, join='inner')
    df_final.to_excel(time_tag + "/%s_参数销量比.xlsx" % time_tag)


if __name__ == "__main__":
    time_tag = '整体平均千箱_2018-01-05-16h03m'
    sale_tag = '整体平均千箱'
    sales_file_proc='湖北各商圈总销量TT+MT.xlsx'
    interpreter(time_tag, sale_tag, sales_file_proc, '湖北')
