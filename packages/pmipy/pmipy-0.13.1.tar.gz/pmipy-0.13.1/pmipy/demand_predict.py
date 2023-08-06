import os, sys
import re
import time
import shutil
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from keras.models import Sequential
from keras.layers import Dense
# from keras.optimizers import SGD
from pmipy.DemandPredict.Visualization import SnsVisualization
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from pyplotz.pyplotz import PyplotZ
from pmipy.DemandPredict import adjustment_interpreter
from pmipy.DemandPredict import AnalyzeGrading

zhfont1 = mpl.font_manager.FontProperties(fname='C:\Windows\Fonts\simkai.ttf')  # 解决python可视化中文乱码的问题


class BusinessSalesPrediction(SnsVisualization):
    def __init__(self, work_dir, df, sales_file_proc, ocm_file, time_tag, sale_tag, sales_mapping_file, province):
        self.work_dir = work_dir
        self.time_tag = time_tag
        self.file_tag = os.path.splitext(sales_mapping_file)[0]
        self.df1 = df
        df2 = pd.read_excel(os.path.join(work_dir, ocm_file), index_col=2)
        self.df2 = df2.drop(['省', '市'], axis=1).T
        self.sales_mapping_file = sales_mapping_file
        self.province =province
        self.sales_file_proc = sales_file_proc
        self.sale_tag = sale_tag

    # 处理康师傅提供的各商圈销量数据，关键点是合并一个商圈多个经销商的销量数据
    def sum_mutil_dealer(self, sales_file_ori):
        """
        如要读取Excel多个sheet，则可以通过下列方法实现：
        xls = pd.ExcelFile('path_to_file.xls')
        df = pd.read_excel(xls, 'Sheet1')
        或者通过上下文管理器实现：
        with pd.ExcelFile('path_to_file.xls') as xls:
            df1 = pd.read_excel(xls, 'Sheet1')
            df2 = pd.read_excel(xls, 'Sheet2')
        """
        df = pd.read_excel(os.path.join(self.work_dir, sales_file_ori), skiprows=2)  # 忽略前两行
        df.drop(['省', '市', '区/县', '营业部', '现有经销商/物流公司名称', '客户形态', 
                 '现有经销商/物流公司代码'], axis=1, inplace=True)
        df.fillna(method='pad', inplace=True)  # excel原合并行缺失值填充
        # 由于20171201日客户又添加了商圈客户形态等级，在一下部分代码作了修改
        df.drop_duplicates(['具体描述', '整体', '高价面'], inplace=True)  # 先处理一商圈多区县的销量数据
        df2 = df.groupby(['具体描述']).sum()  # 合并一商圈多经销商销量数据
        # 计算各商圈历年'整体平均千箱'、'高价平均千箱'、'整体平均千元'、'高价平均千元'的平均数据
        df2['整体平均千箱'] = df2.loc[:, ['整体', '整体.1', '整体.2']].mean(axis=1)
        df2['高价平均千箱'] = df2.loc[:, ['高价面', '高价面.1', '高价面.2']].mean(axis=1)
        df2['整体平均千元'] = df2.loc[:, ['整体.3', '整体.4', '整体.5']].mean(axis=1)
        df2['高价平均千元'] = df2.loc[:, ['高价面.3', '高价面.4', '高价面.5']].mean(axis=1)
        # 提取平均销量数据及最近一年的销量平均数据
        df3 = df2.loc[:, ['整体.2', '整体平均千箱', '整体.5', '整体平均千元', '高价面.2', '高价平均千箱', '高价面.5',
                          '高价平均千元']]
        df3.rename(index=str, columns={"整体.2": "整体2017千箱", "整体.5": "整体2017千元", "高价面.2": "高价2017千箱",
                                       "高价面.5": "高价2017千元"}, inplace=True)
        # 对商圈等级进行排序
        # df3.sort_index(level='客户形态对应的商圈等级', inplace=True)
        df3.sort_index(level='具体描述', inplace=True)
        print('%s共有%d商圈' % (self.province, len(df3)))
        df3.to_excel(self.sales_file_proc)

    def ocm_pretreatment(self):
        # 部分商圈包含多个区县，因此需先合并这类商圈的OCM参数
        df = pd.DataFrame(self.df2.index, columns=['区县'], index=self.df2.index)
        for business in self.df1.index:
            # 包含“市辖区”字段的商圈有一个或多个区县，不包含的只有一个区县
            if ("、" in business) or ("，" in business):
                business_parse = re.split(r'[（、，）]', business)[1:-1]
                try:
                    df.loc[:, business] = self.df2.loc[:, business_parse].sum(axis=1)
                except Exception as err:
                    print(err)  # 如果报错，将输出OCM中缺失的区县
            else:
                if business in self.df2.columns:
                    df[business] = self.df2[business]
        df.set_index("区县", inplace=True)
        df = df.T
        df = pd.concat([df, self.df1[self.sale_tag]], axis=1, join='inner')
        df.index.set_names("商圈", inplace=True)
        df.to_excel(self.sales_mapping_file)
        return df

    # 传统神经网络
    def neural_network_model(self, data, step_list=[50], mutil_NN=False, test_size=0.3):
        mutil_tag = "MutilNN" if mutil_NN else "MonoNN"  # 判断单层还是多层神经网络
        dim = len(data.columns) - 1
        parameter = np.append(data.columns[:-1], ['bias'])
        # 数据标准化
        scaler = StandardScaler().fit(data.values)  # sklearn的标准化类
        mean = scaler.mean_  # 平均值，为后续还原真实数据准备
        std = np.sqrt(scaler.var_)  # 标准差，为后续还原真实数据准备

        # random_state：可以为整数、RandomState实例或None，默认为None
        # 若为None时，每次生成的数据都是随机，可能不一样,若为整数时，每次生成的数据都相同
        train_data, test_data = train_test_split(data, test_size=test_size)
        X_train, y_train = scaler.transform(train_data)[:, :-1], scaler.transform(train_data)[:, -1]
        X_test, y_test = scaler.transform(test_data)[:, :-1], scaler.transform(test_data)[:, -1]
        # sgd = SGD(lr=0.005)

        # 此函数用于判断预测值与真实值的偏差，范围在0.2以后表示较为理想
        def deviation(y_true, y_pred):
            return (y_pred - y_true) / y_true
        effective_learning = True  # 用于判断是否有有效学习
        # 创建文件夹
        if not os.path.exists(self.time_tag):
            os.mkdir(self.time_tag)
        # 探究训练迭代次数对参数权重的影响
        for index, time_step in enumerate(step_list):
            model = Sequential()
            if mutil_NN:
                model.add(Dense(dim * 4, input_dim=dim, activation='relu'))
                model.add(Dense(dim * 2, activation='relu'))
                model.add(Dense(1))
            else:
                model.add(Dense(1, input_dim=dim))

            model.compile(loss='mse', optimizer='sgd', metrics=[deviation])  # 目前暂不使用自己定义的sgd
            model.fit(X_train, y_train, batch_size=10, epochs=time_step)  # batch_size需优化
            score = model.evaluate(X_test, y_test, verbose=0)
            print('Test loss:', score[0])
            if score[0] > 0.3:  # 设置loss上限
                print("Test loss is over 0.3, the model is abandoned!")
                effective_learning = False
                shutil.rmtree(self.time_tag)
                break
            # 获取个参数的权重
            W, b = model.layers[0].get_weights()
            W = np.append(W, b)
            df_w = pd.DataFrame(W)
            df_w.columns = [time_step]
            df_w2 = df_w if not index else pd.concat([df_w2, df_w], axis=1)
            # 保存模型
            model.save(os.path.join(self.time_tag, "%s_model_%s_%s.h5" % (self.file_tag, mutil_tag, self.time_tag)))

            # 训练集真实数据及预测数据
            df_ytrain = train_data.iloc[:, -1:]
            y_train_pred = model.predict(X_train)
            df_ytrain['预估销量'] = y_train_pred * std[-1] + mean[-1]
            df_ytrain['training_time'] = time_step
            df_ytrain['预估与实际比值'] = df_ytrain['预估销量'] / df_ytrain[self.sale_tag]
            df_ytrain['vote'] = np.where(abs(1 - df_ytrain['预估与实际比值']) < 0.5, 1, 0)
            df_ytrain['accuracy'] = df_ytrain['vote'].sum()/len(df_ytrain)
            df_train_summary = df_ytrain if not index else df_train_summary.append(df_ytrain)
            
            # 测试集真实数据及预测数据
            df_ytest = test_data.iloc[:, -1:]
            y_test_pred = model.predict(X_test)
            df_ytest['预估销量'] = y_test_pred * std[-1] + mean[-1]
            df_ytest['training_time'] = time_step
            df_ytest['预估与实际比值'] = df_ytest['预估销量'] / df_ytest[self.sale_tag]
            df_ytest['vote'] = np.where(abs(1 - df_ytest['预估与实际比值']) < 0.5, 1, 0)
            df_ytest['accuracy'] = df_ytest['vote'].sum() / len(df_ytest)
            df_test_summary = df_ytest if not index else df_test_summary.append(df_ytest)

            # 绘制散点图，分析预测结果与实际值的偏差
            tag1 = 'Train_' + mutil_tag + '_n' + str(time_step)
            tag2 = 'Test_' + mutil_tag + '_n' + str(time_step)
            self.correlation_analysis(self.sale_tag, "预估销量", df_ytrain, tag1, 'reg')
            self.correlation_analysis(self.sale_tag, "预估销量", df_ytest, tag2, 'reg')

        if effective_learning:
            if not mutil_NN:
                df_w2['参数'] = parameter
                df_w2.set_index('参数', inplace=True)
                df_w2.to_excel(os.path.join(self.time_tag, "各参数权重_%s.xlsx" % self.time_tag))

            # 合并训练和测试的summary
            df_train_summary["type"] = "training"
            df_test_summary["type"] = "test"
            df_summary = df_train_summary.append(df_test_summary)
            #df_summary.index.set_names("商圈", inplace=True)
            df_summary.sort_index(inplace=True)  # 按索引(即商圈名字)进行排序
            df_summary['商圈编号'] = np.arange(1, len(df_summary) + 1)  # data_visualization函数需商圈编号
            self.data_file = "summary_%s_%s.xlsx" % (mutil_tag, self.time_tag)
            df_summary.to_excel(os.path.join(self.time_tag, self.data_file))
            self.df = pd.read_excel(os.path.join(self.time_tag, self.data_file))
            self.boxplot("training_time", "预估与实际比值", "type")
        return effective_learning


def feature_extraction(feature_file):
    try:
        df = pd.read_excel(feature_file)
        parameter = list(df.iloc[:, 0])
    except:
        parameter = "火车站；网吧；便利店；中学；风景区；酒店；美食总数；小吃快餐；日本料理；"\
                    "火锅；烧烤；湖北菜；咖啡厅；湘菜；粤菜；面包甜点；西餐；外卖销量；人口；商圈面积"
        parameter = parameter.split('；')
        print("由于缺乏特征列表文件（%s），我们将使用一下特征列表\n" % feature_file, parameter)
    return parameter


# 集成学习
def ensemble_learning(work_dir, df, sales_file_proc, ocm_file, time_tag, sale_tag, sales_mapping_file, feature_file, province):
    if not os.path.exists("history"):
        os.mkdir("history")
    if not os.path.exists(time_tag):
        os.mkdir(time_tag)
    df = pd.read_excel(sales_mapping_file, index_col=0)
    parameter = feature_extraction(feature_file)
    df = df.loc[:, parameter + [sale_tag]]
    # 对缺失值进行填充
    df.fillna(0, inplace=True)
    step_list = [200]  # 50, 100, 200, 500, 1500]
    num = 0
    for i in range(100):
        time_tag2 = "%s_%s" % (time_tag, str(i + 1))  # time_tag2是为了分离每个弱学习器的学习结果
        bsp = BusinessSalesPrediction(work_dir, df, sales_file_proc, ocm_file, time_tag2, sale_tag, sales_mapping_file, province)
        effective_learning = bsp.neural_network_model(df, step_list)
        if effective_learning:
            num += 1

        if num >= 20:
            break

    num2 = 0
    for i in os.listdir('.'):
        if time_tag + '_' in i:  # 字符串中添加'_'是为了区分总文件夹time_tag
            df2 = pd.read_excel(os.path.join(i, "summary_MonoNN_%s.xlsx" % i))
            df_w = pd.read_excel(os.path.join(i, "各参数权重_%s.xlsx" % i), index_col=0)  # 将参数列设置为index
            df_w.drop('bias', inplace=True)
            df_w2 = df_w
            df_w.columns = ['权重']
            df2 = df2[df2['training_time'] == 200]  # 整体千箱运算目前只考虑200训练循环数
            df3 = df2 if not num2 else df3.append(df2, ignore_index=True)
            df_w1_all = df_w if not num2 else pd.concat([df_w1_all, df_w])
            df_w2_all = df_w2 if not num2 else pd.concat([df_w2_all, df_w2], axis=1)
            num2 += 1
            # 使用完之后，将文件夹移至history
            shutil.move(i, "history")

    df3.drop(['type'], axis=1, inplace=True)
    gb = df3.groupby("商圈")
    df4 = gb.median()
    df5 = gb.mean()
    df4.sort_values('预估与实际比值', ascending=False, inplace=True)  # 按销量变化率从大到小排序
    df_w1_all_median = df_w1_all.groupby('参数').median()
    df_w1_all_median.sort_values('权重', inplace=True)
    df_positive_factor = df_w1_all_median[::-1][:5]
    # df_positive_factor = df_positive_factor[df_positive_factor['权重'] > 0.1]
    df_positive_factor['正负性'] = '正因子'
    df_negative_factor = df_w1_all_median.head(5)
    # df_negative_factor = df_negative_factor[df_negative_factor['权重'] < -0.1]
    df_negative_factor['正负性'] = '负因子'
    df_factor = pd.concat([df_positive_factor, df_negative_factor])

    # 集成学习数据产出
    df3.to_excel(os.path.join(time_tag, '%s_all.xlsx' % time_tag), index=False)  # 所有弱学习器的产出数据
    df4.to_excel(os.path.join(time_tag, '%s_median.xlsx' % time_tag))  # 产出中位数
    df5.to_excel(os.path.join(time_tag, '%s_mean.xlsx' % time_tag))  # 产出平均值
    df_w1_all.to_excel(os.path.join(time_tag, "%s_weight_boxplot.xlsx" % time_tag))  # 纵向合并各弱学习器的参数权重，用于画boxplot
    df_w2_all.to_excel(os.path.join(time_tag, "%s_weight_heatmap.xlsx" % time_tag))  # 横向合并各弱学习器的参数权重，用于画热图
    df_w1_all_median.to_excel(os.path.join(time_tag, "%s_weight.xlsx" % time_tag))
    df_factor.to_excel(os.path.join(time_tag, '%s_正负因子.xlsx' % time_tag))  # 排名前五的正因子


def data_visualization(work_dir, time_tag, sale_tag, sales_file_proc, province):
    data_file1 = os.path.join(time_tag, "%s_weight_heatmap.xlsx" % time_tag)
    data_file2 = os.path.join(time_tag, "%s_weight_boxplot.xlsx" % time_tag)
    data_file3 = os.path.join(time_tag, "%s_all.xlsx" % time_tag)

    svl = SnsVisualization(work_dir, data_file1, time_tag)
    df1 = pd.read_excel(data_file1)
    df1.set_index("参数", inplace=True)
    # 绘制各地理因子的权重的热图
    svl.heatmap(df1, "弱学习器", "地理因子", "各地理因子的权重", annot=True, cmap="RdYlGn")
    # 绘制各地理因子的权重的箱线图
    pltz = PyplotZ()
    pltz.enable_chinese()
    df2 = pd.read_excel(data_file2)
    plt.figure(figsize=(14, 7))  # 输出图片的尺寸
    sns.set(style="ticks")
    plt.plot(np.arange(-1, 49), np.zeros(50), linestyle="--")  # 绘制0基线
    plt.xticks(rotation='45', fontproperties=zhfont1, fontsize=20)
    sns.boxplot(x='参数', y='权重', data=df2, color="#48D1CC")
    pltz.xlabel('参数')
    pltz.ylabel('权重')
    plt.savefig(os.path.join(time_tag, '%s_weight_boxplot.png' % time_tag), dpi=120, bbox_inches='tight')
    plt.close()
    # 使用箱线图显示各商圈的预估销量与真实销量的偏移水平
    df3 = pd.read_excel(data_file3)
    pltz = PyplotZ()
    pltz.enable_chinese()
    plt.figure(figsize=(16, 7))  # 输出图片的尺寸
    sns.set_style("whitegrid")
    plt.plot(np.arange(-1, 99), np.ones(100), linestyle="--")  # 绘制0基线
    plt.xticks(fontproperties=zhfont1)
    #  fliersize是异常值符号的大小
    sns.boxplot(x='商圈编号', y='预估与实际比值', data=df3, width=0.7, fliersize=1.5, color="#5CACEE", linewidth=0.8)
    pltz.xlabel('商圈编号')
    plt.yticks(np.arange(-2, 5, 1))
    pltz.ylabel('偏移值')
    plt.savefig(os.path.join(time_tag, '%s_商圈预估销量偏移.png' % time_tag), dpi=120, bbox_inches='tight')
    plt.close()
    # 箱线图-散点图解释商圈需要调整的原因
    adjustment_interpreter.interpreter(time_tag, sale_tag, sales_file_proc, province)


def main(work_dir, province, sales_file_ori, ocm_file, feature_file):
    sales_file_proc = sales_file_ori.split('.')[0] + '_proc.xlsx'
    if not os.path.exists(sales_file_proc):
         BusinessSalesPrediction(work_dir, 'df', sales_file_proc, ocm_file, 'time_tag', 'sale_tag',
                                 'sales_mapping_file', province).sum_mutil_dealer(sales_file_ori)

    sale_data = pd.read_excel(os.path.join(work_dir, sales_file_proc), index_col=0)
    time_tag = time.strftime("%Y-%m-%d-%Hh%Mm", time.localtime())
    for sale_tag in ['整体平均千箱', '高价平均千箱']:
        tag = "%s_%s_" % (province, sale_tag) + time_tag
        df = pd.DataFrame({sale_tag: sale_data[sale_tag]})
        sales_mapping_file = "%s商圈OCM_%s.xlsx" % (province, sale_tag)  # sales_mapping_file为中间过度文件，经常被覆盖
        # if not os.path.exists(sales_mapping_file):
        bsp = BusinessSalesPrediction(work_dir, df, sales_file_proc, ocm_file, tag, sale_tag, sales_mapping_file, province)
        bsp.ocm_pretreatment()
        ensemble_learning(work_dir, df, sales_file_proc, ocm_file, tag, sale_tag, sales_mapping_file, feature_file, province)
        data_visualization(work_dir, tag, sale_tag, sales_file_proc, province)
        # 暂时关闭商圈等级分析：AnalyzeGrading.analyze_grading(tag, '%s_综合.xlsx' % tag, '客户形态对应的商圈等级', '预估销量', '整体预估销量', province)


if __name__ == "__main__":
    work_dir = "."
    sales_file_ori = "湖北业绩信息1218.xlsx"
    ocm_file = "湖北_OCM参数.xlsx"#"湖北各区县OCM_20171219.xlsx"
    main(work_dir, province, sales_file_ori, sales_file_proc, ocm_file)

