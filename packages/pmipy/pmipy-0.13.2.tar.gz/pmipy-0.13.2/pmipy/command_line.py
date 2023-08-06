# ---------------------------------------------------------------------------------------------------------------------#
# AUTHOR: Jasonai, jasonai.zhu@gaialab.ai                                                                              #
# ORGANIZATION: PMI                                                                                                    #
# VERSION: 1.0                                                                                                         #
# CREATED: 3rd Mar 2018                                                                                                #
# ---------------------------------------------------------------------------------------------------------------------#

import os
import pandas as pd

#import seaborn as sns
#import matplotlib.pyplot as plt
#from sklearn.preprocessing import StandardScaler

"""Tnseq command line interface """

# =============== <Realization of shell scripts using click package> #==============#
import click

VERSION = '0.12'
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=VERSION)
def main():
    pass


@main.command(help='根据经纬度批量提取宜出行人流数据')
@click.option('--city_list', '-c',multiple=True, default=[], help='请输入需要更新的城市（标准地级市名称），如多个城市则按如下规则填写：\
              “-c 城市1 -c 城市2”，“-c 全国”则表示更新全国所有地级市的数据！')
@click.option('--option', '-op', default=1, help="请输入更新项目代号：1--宜出行流动人口数据;2--51job数据;3--携程酒店数据;\
4--外卖数据;5--高德POI数据;6--点评数据;7--百度POI数据;8--安居客房源数据。默认为“宜出行流动人口数据”")
@click.option('--database', '-d', default='ycx', help="请输入待更新数据源的数据库名称，默认为“ycx”")
@click.option('--table_collection', '-tc', default='', help="请输入存放待更新数据源的数据表（或集合）的名称！")
@click.option('--meter', '-m', default=1000, help='请输入网格格子的规格，输入格式为正整数，默认为1000(米)')
def updateOCM(**kwargs):
    from pmipy import updateTileData
    cityList = list(kwargs['city_list'])
    option = kwargs['option']
    dbName = kwargs['database']
    tableColl = kwargs['table_collection']
    meter = kwargs['meter']
    if option == 1:
        updateTileData.updateYCX(cityList, dbName, ycxTable=tableColl, meter=meter)
    else:
        print("目前尚未开发此项目的更新功能!")


@main.command(help='根据经纬度批量提取宜出行人流数据')
@click.option('--file_path1', '-f', default='', help='存放店铺/点位经纬度数据的文件，格式为xlsx或csv')
@click.option('--ycx_table', '-y', default='', help="如数据存放在Mysql数据库中，则填写数据表名称，\
如数据存放在文件中，文件格式须为xlsx或csv，且表头列名需包含['lng', 'lat', 'count']")
@click.option('--database', '-d', default='ycx', help="数据库名称，默认为“ycx”")
@click.option('--city', '-ct', default='上海', help="填写待计算的城市，默认为“上海”！")
@click.option('--file_store_type', '-ft', default='mysql', help="存储宜出行数据的载体，目前分三种：1，数据库--mysql；\
2，本地文件--localfile；3，内存存储--df。默认为'mysql'")
@click.option('--grid', '-g', is_flag=True, help='网格开关，如所计算的区域形状为网格，则需要在命令行中填写“-g”！')
@click.option('--lnglat', '-ll',multiple=True, default=['经度','纬度'], help='输入f1文件存放存放经度、纬度的列名，默认为“-l 经度 -l 纬度”')
@click.option('--meter', '-m', default='500', help='指定获取宜出行点位的范围(半径)，输入格式为正整数，默认为500(米)')
@click.option('--core_num', '-c', default='max', help='指定程序并发运行的线程数，输入格式为正整数，默认值为本地计算机最大的线程数')
@click.option('--file_ouput', '-o', default='', help='输入输出文件名，默认为f1,f2文件名的合并，输出格式为xlsx格式')
def yichuxing(**kwargs):
    from pmipy import getPeopleFlow
    pointFile = kwargs['file_path1']
    ycxTable = kwargs['ycx_table']
    dbName = kwargs['database']
    ycxStoreType = kwargs['file_store_type']
    city = kwargs['city']
    grid = kwargs['grid']
    lnglat = kwargs['lnglat']
    meter = kwargs['meter']
    core_num = kwargs['core_num']
    outputFile = kwargs['file_ouput']
    getPeopleFlow.getPeopleFlow(pointFile, ycxTable, dbName, ycxStoreType, city, grid, lnglat, meter, core_num, outputFile)


@main.command(help='地理编码或逆编码/坐标转换')
@click.option('--file_path', '-f', prompt='请输入文件路径', help='存放地理位置信息的文件，格式为xlsx或csv')
@click.option('--address', '-a',multiple=True, default=['地址'], help='输入描述性地址所在列的列名，多列请输入“-a column1 -a column2 ...”，\
比如需要文件中“省”、“市”和“具体地址”这三列的内容合并进行搜索经纬度度，则填写“-a 省 -a 市 -a 具体地址”，默认值为“-a 地址”')
@click.option('--tranform', '-tf', is_flag=True, help='经纬度坐标转换开关，只需要坐标转换时填写“-tf”即可！')
@click.option('--lnglat', '-l',multiple=True, default=['经度','纬度'], help='输入f文件存放经度、纬度的列名，默认为“-l 经度 -l 纬度”')
@click.option('--initial_coordinate', '-ic', default='gaode', help='填写原始坐标的格式标准，如为高德火星坐标系，则填写“gaode”;\
如为百度坐标系填写“baidu”;国际大地坐标系填写“global”，默认为gaode')
@click.option('--target_coordinate', '-tc', default='gaode', help='填写输出坐标的格式标准，如为高德火星坐标系，则填写“gaode”;\
如为百度坐标系填写“baidu”;国际大地坐标系填写“global”，默认为gaode')
@click.option('--thread', '-t', default=50, help='指定程序并发运行的线程数，输入格式为正整数，默认值为50')
@click.option('--file_ouput', '-o', default='', help='输入输出文件名，默认文件的前缀为f的文件名')
def coordinate(**kwargs):
    from pmipy import getTargetCoordinate
    file_path = kwargs['file_path']
    address = kwargs['address']
    tranform = kwargs['tranform']
    lnglat = kwargs['lnglat']
    initial_coordinate = kwargs['initial_coordinate']
    target_coordinate = kwargs['target_coordinate']
    thread = kwargs['thread']
    file_ouput = kwargs['file_ouput']
    if tranform:
        getTargetCoordinate.coordinateTransform(file_path, file_ouput, lnglat, initial_coordinate, target_coordinate)
    else:
        getTargetCoordinate.getTargetCoordinate(file_path, address, thread, target_coordinate, file_ouput)


@main.command(help='特征工程器<特征处理/特征选择>')
@click.option('--feature_file', '-f1', prompt='请输入特征文件路径', help='存放特征数据表的文件，格式为xlsx或csv')
@click.option('--label_file', '-f2', default='', help='存放标签数据表的文件，如标签在上述特征文件中，则可以不用填写，格式为xlsx或csv')
@click.option('--colf', '-cf',default='编号', help='colF和colL为特征和标签数据的索引列名（即vlookup列），默认为“编号”')
@click.option('--coll', '-cl',default='编号', help='colF和colL为特征和标签数据的索引列名（即vlookup列），默认为“编号”')
@click.option('--label', '-l',default='标签', help='机器学习的标签列名，默认为“标签”')
@click.option('--border', '-b',default='mean', help='针对回归项目的数值型标签：此选项可指定二分类化的方法，默认为“mean”,\
其他备选可以是“median”、“kmeans”等')
@click.option('--group_num', '-gn',default=4, help='针对WOE编码：分组时的组别数量，默认为4组')
@click.option('--comp_num', '-cn',default=4, help='针对特征分析：特征复杂度，默认为4')
@click.option('--group_meth', '-gm',default=1, help="针对WOE编码：分组的方法。1:'等距法,2:'自身类别法'。'默认为“等距法”")
@click.option('--mean_meth', '-mm',default='median', help="针对相关性分析方法。mean:'求特征的平均值',median:'求特征的中位值'。\
'默认为求“中位值”")
@click.option('--corr_meth', '-cm',default='kendall', help="针对相关性分析方法。主要有kendall和person。'默认为“kendall”")
@click.option('--file_ouput', '-o', default='', help='输入输出文件名，默认文件的前缀为f1的文件名')
def featreng(**kwargs):
    from pmipy import featureEngineer
    featureFile = kwargs['feature_file']
    labelFile = kwargs['label_file']
    colF = kwargs['colf']
    colL = kwargs['coll']
    label = kwargs['label']
    border = kwargs['border']
    groupNum = kwargs['group_num']
    compNum = kwargs['comp_num']
    groupMeth = kwargs['group_meth']
    meanMeth = kwargs['mean_meth']
    corrMeth = kwargs['corr_meth']
    file_ouput = kwargs['file_ouput']
    featureEngineer.featureEngineering(featureFile, labelFile, colF, colL, 
                                       label, border, groupNum, compNum, groupMeth, file_ouput, meanMeth, corrMeth)


@main.command(help='根据经纬度获取OCM数据>')
@click.option('--file_path', '-f', prompt='请输入存放经纬度信息的文件路径', help='存放经纬度信息的文件，格式为xlsx或csv')
@click.option('--lnglat', '-l', multiple=True, default=['经度','纬度'], help='输入f文件存放经度、纬度的列名，默认为“-l 经度 -l 纬度”')
@click.option('--tile_number', '-tn', default=1, help='请输入需获取的网格数，比如1表示只取一个格子的数据，默认为1')
@click.option('--file_ouput', '-o', default='', help='填写输出文件名，默认文件的前缀为f的文件名')
def getocm(**kwargs):
    from pmipy import getOcmData
    file_path = kwargs['file_path']
    lnglat = kwargs['lnglat']
    tileNum = kwargs['tile_number']
    file_ouput = kwargs['file_ouput']
    getOcmData.get_tileName(file_path, lnglat, tileNum, file_ouput)


@main.command(help='OCM参数可视化分析')
@click.option('--data_path', '-f', default='湖北人口_ocm1.5.csv', help="输入待分析的OCM文件路径，默认为“湖北人口_ocm1.5.csv”")
@click.option('--tag', '-t', default='湖北人口', help='用于存放输出文件的文件夹，默认为“湖北人口”')
def OCM_Visual(**kwargs):
    from pmipy import OCMVisualization
    data_path = kwargs['data_path']
    tag = kwargs['tag']
    path =os.path.dirname(OCMVisualization.__file__)  # OCMFeatureExtract模块所在的路径
    OCMVisualization.run_Rscript(data_path, tag, path)


@main.command(help='提取OCM参数')
@click.option('--data_path', '-f', default='湖北需求预估使用的参数.xlsx', help='输入待提取的参数信息文件路径，默认为“湖北需求预估使用的参数.xlsx”')
@click.option('--province', '-p', default='湖北', help='选择提取的省份，默认为湖北')
def OCM_extract(**kwargs):
    from pmipy import OCMFeatureExtract
    feature_file = kwargs['data_path']
    province = kwargs['province']
    df = pd.read_excel(feature_file, index_col=[0])  # 将'省'列设为索引
    OCMFeatureExtract.merging_data(df, province)


@main.command(help='分析销售数据或OCM参数')
@click.option('--data_path', '-f', default='福州上海子公司业绩表.xlsx', help='分析数据的文件路径')
@click.option('--index', '-i', default='餐厅名称', help='选择某列作为数据框的索引')
@click.option('--value_col', '-vc', default=5, help='选择用于数据标准化处理的开始列数')
def feature_analysis(**kwargs):
    data_path = kwargs['data_path']
    index = kwargs['index']
    # value_col = kwargs['value_col']
    df = pd.read_excel(data_path, index_col=index)
    print(df.head())


@main.command(help='BIT自动化程序')
@click.option('--file_path1', '-f1', default='ts2.xlsx', help='待写入的excel文件路径，默认为“ts2.xlsx”')
@click.option('--file_path2', '-f2', default='MR002-170802Y-德克士Brand Image Tracking（W45-W48）（11月）数据v2.xlsx', 
help='问卷信息文件（已初步清洗的excel文件）路径，默认为“MR002-170802Y-德克士Brand Image Tracking（W45-W48）（11月）数据v2.xlsx”')
@click.option('--file_path3', '-f3', default='qa-Olivia.xlsx', help='问卷题目编号信息文件路径，如未来题目有变动，需更新此文件信息，默认为“qa-Olivia.xlsx”')
@click.option('--file_path4', '-f4', default='新配额分布.xlsx', help='城市配额/权重文件路径，默认为“新配额分布.xlsx”')
@click.option('--sheet', '-s', default='sheet2', help='选择待填写的sheet。sheet2:<2.外食情况>;sheet3:<3.品牌与广告知名度>;sheet4:<4.品牌购买与食用>;\
sheet5:<5.西式快餐U&A >;sheet6:<6.重要指标汇总>;sheet7:<7.样本资料>，如填写“all”，则表示写入所有sheet。默认为“sheet2”')
@click.option('--period_num', '-p', default=4, help='输入阶段数，默认为4')
def BIT(**kwargs):
    from pmipy import BIT
    filepath1 = kwargs['file_path1']
    filepath2 = kwargs['file_path2']
    filepath3 = kwargs['file_path3']
    filepath4 = kwargs['file_path4']
    sheet = kwargs['sheet']
    period_num = kwargs['period_num']
    BIT.main(sheet, filepath1, filepath2, filepath3, filepath4, period_num)


@main.command(help='需求预估（商圈分级）')
@click.option('--work_dir', '-wd', default='.', help='输入数据的存放目录，默认为当前工作目录')
@click.option('--sales_file_ori', '-sfo', default='湖北业绩信息1218.xlsx', help='销售数据的初始文件路径，默认为“湖北业绩信息1218.xlsx”')
# @click.option('--sales_file_proc', '-sfp', default='', help='处理过的销售数据路径，如存在则程序会无视sales_file_ori文件，默认不存在')
@click.option('--ocm_file', '-of', default='湖北_OCM参数.xlsx', help='OCM参数的文件路径，默认为“湖北_OCM参数.xlsx”')
@click.option('--feature_file', '-ff', default='', help='OCM参数的名单路径，默认不填')
@click.option('--province', '-p', default='湖北', help='选择预测的省份，默认为湖北')
def demand_predict(**kwargs):
    from pmipy import demand_predict
    work_dir = kwargs['work_dir']
    sales_file_ori = kwargs['sales_file_ori']
    # sales_file_proc = kwargs['sales_file_proc']
    ocm_file = kwargs['ocm_file']
    feature_file = kwargs['feature_file']
    province = kwargs['province']
    demand_predict.main(work_dir, province, sales_file_ori, ocm_file, feature_file)


# ================================== <Running main function> ================================== #
if __name__ == '__main__':
    main()


