import os, sys
import time
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from pyplotz.pyplotz import PyplotZ


zhfont1 = mpl.font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf')


class SnsVisualization(object):
    def __init__(self, work_dir, data_file, time_tag=time.strftime("%Y-%m-%d-%Hh%Mm", time.localtime())):
        self.work_dir = work_dir
        self.data_file = data_file
        self.time_tag = time_tag
        file_suffix = os.path.splitext(data_file)[-1]
        if not os.path.exists(self.time_tag):
            os.mkdir(self.time_tag)
        if '.xls' in file_suffix:
            self.df = pd.read_excel(os.path.join(work_dir, data_file))
        elif file_suffix == '.csv':
            self.df = pd.read_csv(os.path.join(work_dir, data_file))
        else:
            self.df = pd.read_table(os.path.join(work_dir, data_file))

    def plot(self):
        df1 = pd.read_excel("2017-11-08-23h32m_median.xlsx")
        df2 = pd.read_excel("2017-11-08-23h32m_mean.xlsx")
        df1.sort_values(by=["sales_avg"], inplace=True)
        df2.sort_values(by=["sales_avg"], inplace=True)
        max1 = df1["sales_avg"].max() if df1["sales_avg"].max() > df1["sales_pred"].max() else df1["sales_pred"].max()
        max2 = df2["sales_avg"].max() if df2["sales_avg"].max() > df2["sales_pred"].max() else df2["sales_pred"].max()
        max = int(max1)+1 if max1 > max2 else int(max2)+1
        sns.set_style("whitegrid")
        plt.plot(np.arange(max), linestyle="--")
        plt.scatter(df1["sales_avg"], df1["sales_pred"], c='r')
        plt.scatter(df2["sales_avg"], df2["sales_pred"], c='b', marker="+")
        plt.savefig("2017-11-08-23h32m_sales_pred")

    def correlation_analysis(self, factor1, factor2, df, tag, kind='reg', title=''):
        # 判断文件类型，用适合的pandas读取器读取数据
        # 直方图的双变量类似物被称为“hexbin”图，因为它显示了落在六边形仓内的观测数
        pltz = PyplotZ()
        pltz.enable_chinese()
        sns.jointplot(x=factor1, y=factor2, data=df, kind=kind)
        pltz.xlabel(factor1)
        pltz.ylabel(factor2)
        pltz.title(title)
        plt.savefig(os.path.join(self.time_tag, "%s&%s_jointplot_%s_%s_%s" % (factor1, factor2, kind, tag, self.time_tag)))
        plt.close()
        """g = sns.jointplot(x=factor1, y=factor2, data=df, kind="kde", color="m")
        g.plot_joint(plt.scatter, c="w", s=30, linewidth=1, marker="+")
        g.ax_joint.collections[0].set_alpha(0)
        g.set_axis_labels("$X$", "$Y$")
        plt.show()"""

    def heatmap(self, df, xlabel, ylabel, title='', annot=False, cmap=None):
        f, ax = plt.subplots(figsize=(15, 12))
        # 解决中文乱码问题
        pltz = PyplotZ()
        pltz.enable_chinese()
        plt.xticks(fontproperties=zhfont1)  # rotation='90',
        plt.yticks(fontproperties=zhfont1)
        sns.heatmap(df, square=False, linewidths=.5, annot=annot, cmap=cmap)
        pltz.xlabel(xlabel)
        pltz.ylabel(ylabel)
        pltz.title(title)
        plt.savefig(os.path.join(self.time_tag, "%s_%s_heatmap_%s" % (xlabel, ylabel, self.time_tag)), bbox_inches='tight', pad_inches=0.2)
        plt.close()

    def correlation_heatmap(self, internal_chars=[], annot=False, cmap=None):
        tag = os.path.splitext(self.data_file)[0]
        corrmat = self.df[internal_chars].corr() if internal_chars else self.df.corr()
        self.heatmap(corrmat, tag, "correlation", annot, cmap)

    def boxplot(self, x, y, hue=None):
        tag = os.path.splitext(self.data_file)[0]
        pltz = PyplotZ()
        pltz.enable_chinese()
        sns.set_style("whitegrid")  # sns.set(style="ticks")
        plt.xticks(fontproperties=zhfont1)
        plt.yticks(fontproperties=zhfont1)
        sns.boxplot(x=x, y=y, hue=hue, data=self.df, palette="PRGn")
        pltz.xlabel(x)
        pltz.ylabel(y)
        plt.savefig(os.path.join(self.time_tag, "%s_boxplot_%s" % (tag, self.time_tag)))
        plt.close()
        """sns.swarmplot(x=x, y=y, hue=hue, data=self.df)
        plt.savefig(os.path.join(self.time_tag, "%s_swarmplot_%s" % (tag, self.time_tag)))
        plt.close()
        sns.violinplot(x=x, y=y, hue=hue, data=self.df, palette="muted")
        plt.savefig(os.path.join(self.time_tag, "%s_violinplot_%s" % (tag, self.time_tag)))
        plt.close()"""


if __name__ == "__main__":
    work_dir = "."
    data_file = "2017-11-08-23h32m_权重值.xlsx"
    vl = SnsVisualization(work_dir, data_file)
    # parameter = '从众适用型比例,理智务实型比例,点评最低(3元以下)-比例,点评中低(3-27元)-比例,人口总数,区域数量,平方米均日租金,平方米每户均单价,旅游景点,教育培训,火锅,烧烤,川菜,咖啡厅'
    parameter = "人口总数；医疗；金融；酒店；火锅；购物；汽车服务；休闲娱乐；川菜；生活服务；政府机构；美食；" \
                "公司企业；交通设施；湘菜；大众门店总数；运动健身；文化传媒；面包甜点；烧烤；西餐；咖啡厅；教育培训；" \
                "房地产；大众门店均单价；小吃快餐；旅游景点；行政地标；区域数量"
    internal_chars = parameter.split('；') + ['sales_avg'] #;sys.exit(internal_chars)
    df = pd.read_excel(os.path.join(work_dir, data_file))
    df.set_index("参数", inplace=True)
    tag = os.path.splitext(data_file)[0]
    vl.heatmap(df, tag, annot=True, cmap="RdYlGn")
    #vl.plot()

