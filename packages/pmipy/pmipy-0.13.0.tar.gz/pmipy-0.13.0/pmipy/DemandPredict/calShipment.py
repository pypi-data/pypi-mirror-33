"""
Created on Wed May  2 17:27:05 2018

@author: jasonai
"""

import numpy as np
import pandas as pd
from pmipy import log
from pmipy import pmi
import updateFactor
# import tagManifest as tm
# import connDatabase as cd


logger = log.createLogger(__name__)
try:
    config = pmi.ConfigHandler(__file__)
except NameError:
    config = pmi.ConfigHandler('calShipment.py')
mt = config.read_configure('Manifest.ini', 'tag')
mm = config.read_configure('Manifest.ini', 'mapping')


# 数据库名
dbName = mt['dbName']
# 数据表名标签
ksfSales = mt['ksfSales']
infoName = mt['infoName']
partitionName = mt['partitionName']
tyjmlSales = mt['tyjmlSales']
# Excel列名
TTclient = mt['TTclient'] # TT客户(现有实际)
periodTag = mt['periodTag'] # 1705-1804
indexCols = eval(mt['indexCols'])
category_list1 = eval(mt['category_list1'])
# 数据表列名
priceType = mt['priceType']
typeAC = mt['typeAC']
sale = mt['sale']
unit = mt['unit']
businessArea = mt['businessArea']
province = mt['province'] 
city = mt['city']
region = mt['region'] 
channel = mt['channel']
marketingCompany = mt['marketingCompany']
salesDepartment = mt['salesDepartment']
manufacturer = mt['manufacturer']
top3List = eval(mt['top3List'])
top3ListEN = eval(mt['top3ListEN'])
factorType = mt['factorType']
factorNum = mt['factorNum']
timeCol = mt['timeCol']
updateTime = mt['updateTime']
# 区分不同商圈商圈名相同的额外信息
busAdInfo1 = [marketingCompany, salesDepartment, businessArea]

# 连接数据库
cm = pmi.ConnMysql(dbName)

# 计算统一和今麦郎出货量
def tyJmlSales(filePath):
    #标准格式为二维列名
    # 由于tyJml和ksf业绩表中的行销公司名称不统一，读取前先进行名称转化，以ksf业绩为准
    df = pd.read_excel(filePath, header=[0,1], index_col=[0,1,2])
    ## 数据预处理：1.缺失值填0；2.使用0替换'-'
    df2 = df.replace({'-': None})
    df2.fillna(0, inplace=True)
    # 第一维列名:['1505-1604销量数据_箱_标箱', '1605-1704销量数据_箱_标箱', '1705-1804销量数据_箱_标箱']
    fistColumns = list(df2.columns.get_level_values(0).drop_duplicates())
    colName = [i for i in fistColumns if periodTag in i][0]
    df_tyjml = df2[colName]
    """
    sql_info = "select {},{},{},{} from {} where {}='{}'".format(province, 
                       city, region, businessArea, infoName, timeCol, periodTag)
    df_info = pd.read_sql(sql_info, cm.engine)"""
    df_tyjml = df_tyjml.stack().reset_index()
    df_tyjml.columns = [marketingCompany, salesDepartment, manufacturer, priceType, sale]

    return df_tyjml


# 将箱转化为包
def CapitaPackage(df):
    # 将千箱转化为包:容器面转化系数为12，其他规格的面为24
    df = df[df[priceType]!='整体']
    df[sale] = np.where(df[priceType].str.contains('容器'), df[sale]*12, df[sale]*24)
    df[unit] = '包'
    return df

# 去除商圈列为空的记录,busColNum为商圈所在的列数--顺带检查一下行销公司
def checkBusNull(df, busColNum=7):
    df2 = df[3:]
    df3 = df2[df2.iloc[:, busColNum-1].isnull()]
    df4 = df2[df2.iloc[:, 3].isnull()]
    if len(df3):
        logger.error("以下商圈的商圈名为空：\n{}".format(df3))
        raise SystemExit
    elif len(df4):
        logger.error("以下行销公司的名称为空：\n{}".format(df4))
        raise SystemExit
    else:
        logger.info("行销公司、商圈名检查合格！")
  

# 解读excel, 运行前先核定index列<即核定表头格式>；解析后将数据上传至数据库，且一次只上传一年的数据
def calSales(filePath1, filePath2='', exMethod='append'):
    # 核定index列名
    index_num = len(indexCols)
    df_temp = pd.read_excel(filePath1, usecols=list(range(index_num)))
    if list(df_temp.loc[0]) != indexCols:
        logger.error("前{}列列名应为{}，请核定！".format(index_num, indexCols))
        raise SystemExit
    # 检查商圈名是否为空
    checkBusNull(df_temp)

    df = pd.read_excel(filePath1, skiprow=[0,1], header=[2,3,4], index_col=list(range(index_num)))
    # 给index命名，且命英文名字
    indexColsEN = [i if i not in mm else mm[i] for i in indexCols] # 中文列名mapping至英文
    df.index.names=indexColsEN
    # 提取商圈各维度信息
    df_info = df['TT'][TTclient]
    # TT客户数据的列名中英文转换
    df_info.columns = [i if i not in mm else mm[i] for i in list(df_info)]
    df_info.reset_index(inplace=True)
    
    # 去除mt['TTclient,最终得到纯MT和TT数据
    df.drop(('TT',TTclient), axis=1, inplace=True)
    # 使用0填充MT、TT的缺失值
    df.fillna(0, inplace=True)
    # 提取并计算MT、TT数据,同时暂时放弃除商圈名称之外的其他信息
    # 由于跟营业的人已经定了基本格式，即一商圈多行政区时只将销量数据放在第一列
    # 因此，可以通过求和&&取第一列来获取商圈的销量信息。我们也可以利用这两种方法验证数据是否有问题
    # 保留province、city、marketingCompany、salesDepartment和businessArea
    # df_s = df.reset_index(level=['institute','bigbusiness', 'smallbusiness'], drop=True)
    df0 = df.groupby(busAdInfo1).sum()
    df_check = df['TT'][periodTag]
    df_check2 = df_check.reset_index()
    gb = df_check2.groupby(busAdInfo1)
    df1 = gb.sum()
    df2 = gb.head(1)
    df2 = df2.set_index(busAdInfo1)[list(df_check)]
    df2 = df2.loc[df1.index] # 确保顺序跟df2一样
    # 对两种方法得到的dataframe进行横向求和，并且通过比较两种方法的求和结果来检查数据质量
    logger.info("准备检查商圈原始业绩/出货数据质量 ...")
    checkState = True
    # MT合并，TT检查异常
    for i, (sum1, sum2) in enumerate(zip(df1.sum(axis=1), df2.sum(axis=1))):
        if sum1 != sum2:
            logger.warn("{}商圈原始业绩/出货数据(TT)可能存在问题！".format(df1.index[i]))
            checkState = False
    if checkState:
        logger.info("商圈原始业绩/出货数据质量过关！")
    # 准备取指定时间段timeTag的数据，如出现异常，未来可考虑修改
    df_MT = df0['MT'][periodTag]
    df_TT = df0['TT'][periodTag] # 默认为销量之后
    # 获取MT未分配的数据
    df_MT1 = df_MT[(df_MT.index.get_level_values(salesDepartment).str.contains('MT'))|
            (df_MT.index.get_level_values(businessArea).str.contains('MT'))]
    # 去除MT未分配的数据
    df_MT2 = df_MT[~((df_MT.index.get_level_values(salesDepartment).str.contains('MT'))|
            (df_MT.index.get_level_values(businessArea).str.contains('MT')))]
    df_TT2 = df_TT[~((df_TT.index.get_level_values(salesDepartment).str.contains('MT'))|
            (df_TT.index.get_level_values(businessArea).str.contains('MT')))]
    # 总MT和TT销量数据
    def updateBusAllocCoef(df_MT, df_TT):
        # 去除df_MT和df_TT“MT为分配的数据”
        df_ksf = df_MT + df_TT
        # 将数据上传至Mysql数据库area_grade之前先对列进行降维stack
        df_MT = df_MT.stack().reset_index()
        df_MT.columns = list(df_MT.columns)[:-2] + [priceType, sale]
        df_MT.insert(3, channel, 'MT') # 插入到type之前
        df_TT = df_TT.stack().reset_index()
        df_TT.columns = list(df_TT.columns)[:-2] + [priceType, sale]
        df_TT.insert(3, channel, 'TT')
        df_ksf = df_ksf.stack().reset_index()
        df_ksf.columns = list(df_ksf.columns)[:-2] + [priceType, sale]
        df_ksf.insert(3, channel,'TT+MT')
        df_concat = pd.concat([df_ksf, df_TT, df_MT])
        df_concat[manufacturer] = 'KSF'
        # [[ province, city, marketingCompany, manufacturer, salesDepartment, businessArea, channel, priceType, sale]]
        
        ## 计算分配系数
        # 计算各行政区分配系数 
        # 总结销量时，目前暂时只考虑五品类
        df_ksf2 = df_ksf[df_ksf[priceType].isin(category_list1)].drop(priceType, axis=1)
        # df_ksf3 = df_ksf2.groupby([marketingCompany,province, salesDepartment, city, businessArea], as_index=False).sum()
        # 商圈为2617个
        # 解决同一个商圈，<marketingCompany,province, salesDepartment, city, businessArea>不完全相同的问题
        # 目前暂认为同一个商圈的营业部和经销部一定是同一个
        # df_ksf4 = df_ksf3.groupby([marketingCompany,salesDepartment, businessArea], as_index=False).sum()  # 商圈变成2605个
        df_ksf3 = df_ksf2.groupby(busAdInfo1, as_index=False).sum()
        
        df_merge = df_ksf3.merge(df_info,on=busAdInfo1, how='left')
        
        #df_merge.set_index([marketingCompany,province, salesDepartment, city, businessArea], inplace=True)
        df_merge2 = df_merge.groupby([marketingCompany,salesDepartment,region],as_index=False).sum()
        df_merge3 = df_merge.merge(df_merge2, on=[marketingCompany,salesDepartment,region])
        df_merge3['partitionCoefficient'] = df_merge3[sale+'_x'] / df_merge3[sale+'_y']
        # 输出无销量的商圈
        df_problem = df_merge3[df_merge3['partitionCoefficient'].isnull()]
        problemAreaList = list(df_problem[businessArea].drop_duplicates())
        # 对问题商圈的分配系数填1处理
        df_merge3['partitionCoefficient'] = df_merge3['partitionCoefficient'].fillna(1)
        df_alloc = df_merge3.reset_index()
        # 提前上传df_info，df_alloc，为地理因子更新做准备 
        df_info[timeCol] = periodTag
        df_alloc[timeCol] = periodTag
        cm.toMysql(infoName, df_info, updateTime, exMethod)
        cm.toMysql(partitionName, df_alloc, updateTime, exMethod)
        ## 准备更新地理因子
        factorManifest = '原始数据/地理因子信息.xlsx'
        df_area_factor = updateFactor.areaFactorUpdate(factorManifest,exMethod)
        
        df_ksf2 = df_concat
        return df_area_factor, df_ksf2, problemAreaList
    
    # 第一次更新各商圈的因子信息
    df_area_factor = updateBusAllocCoef(df_MT2, df_TT2)[0]
    # 获取各商圈的超市数量并计算经销公司下各商圈的超市占比
    df_area_sm = df_area_factor[df_area_factor[factorType]=='超市']
    df_area_sm2 = df_area_sm.groupby(marketingCompany,as_index=False).sum()
    df_area_sm3 = df_area_sm.merge(df_area_sm2,on=marketingCompany)
    df_area_sm3[factorNum] = df_area_sm3[factorNum+'_x'] / df_area_sm3[factorNum+'_y'] 
    df_MT1s = df_area_sm3.merge(df_MT1.reset_index()[[marketingCompany]+list(df_MT1)], on=marketingCompany)
    df_MT1s[list(df_MT1)] = df_MT1s[list(df_MT1)].apply(lambda x: x * df_MT1s[factorNum])
    df_MT2s = pd.concat([df_MT1s,df_MT2.reset_index()],join='inner')
    df_MT2s = df_MT2s.groupby(busAdInfo1).sum()

    # 第二次更新各商圈的因子信息
    df_area_factor, df_ksf2, problemAreaList = updateBusAllocCoef(df_MT2s, df_TT2)
    logger.info("各商圈地理因子更新完成！")
    logger.warning("以下商圈的五品类的销量之和为0:\n{}".format(problemAreaList))
    
    if filePath2:
        df_tyjml = tyJmlSales(filePath2)
        # 三甲数据中包含的营业部信息
        compDepart = df_tyjml[[marketingCompany,salesDepartment]].drop_duplicates()
        ksfDepart = df_ksf2[[marketingCompany,salesDepartment]].drop_duplicates()
        compDepart2 = compDepart[compDepart[salesDepartment]!='MT部']
        logger.info('三甲数据表共涵盖{}个营业部，去除“MT部”后剩{}个营业部！'.format(len(compDepart),len(compDepart2)))
        logger.info('康师傅出货数据表共涵盖{}个营业部！'.format(len(ksfDepart)))
        # 检查营业部匹配问题
        kdLack = []
        cdLack = []
        for kd in ksfDepart.values:
            kd = list(kd)
            if kd not in compDepart2.values.tolist():
                kdLack.append(kd)
        for cd in compDepart2.values:
            cd = list(cd)
            if cd not in ksfDepart.values.tolist():
                cdLack.append(cd)
        if len(kdLack) and len(cdLack):
            logger.info("""康师傅出货数据表涵盖营业部在三甲表中未匹配到的有：\n{}\n
三甲表涵盖营业部在康师傅出货数据表未匹配到的有：\n{}""".format(kdLack, cdLack))
        else:
            logger.info("康师傅出货数据表涵盖的营业部和三甲表涵盖的营业部匹配通过！")
        # 给统一今麦郎各营业部添加省份信息
        # df_tyjml = df_tyjml.merge(df_ksf2d,on=[marketingCompany,salesDepartment],how='left') 、
        
        df_sale = pd.concat([df_ksf2, df_tyjml])
    else:
        df_sale = df_ksf2

    # 行销公司下的各商圈三甲市场量的计算
    # 各商圈MT+TT销量
    ksf_bus = df_sale[(df_sale[manufacturer]=='KSF')&(df_sale[channel]=='TT+MT')][busAdInfo1+[priceType,sale]]
    ksf_dp = df_sale[(df_sale[manufacturer]=='KSF')&(df_sale[channel]=='TT+MT')][[marketingCompany, 
                     salesDepartment,priceType,sale]]  # 各营业部MT+TT销量
    ksf_dp = ksf_dp.groupby([marketingCompany, salesDepartment, priceType]).sum() # 各营业部MT+TT销量
    # 三甲各营业部总销量,注意不要重复计算TT和MT
    top3_dp = df_sale[~df_sale[channel].isin(['TT','MT'])][[marketingCompany, salesDepartment,priceType,sale]]
    top3_dp = top3_dp.groupby([marketingCompany, salesDepartment, priceType]).sum().reset_index(level=salesDepartment)
    # xxxxxxxxxxxx暂时未设计： 将康师傅未分配的MT分配到对应行销公司的各商圈中,比如云南部 xxxxxxxxxxxxxx
    # 将各行销公司的MT部按比例分配至下属其他营业部
    #top3_dp_MT = top3_dp.iloc[top3_dp.index.get_level_values(salesDepartment)=='MT部']
    #top3_dp_MT = top3_dp_MT.groupby([marketingCompany, priceType]).sum()
    top3_dp1 = top3_dp[top3_dp[salesDepartment]!='MT部'] # 去除各行销公司的MT部
    top3_dp2 = top3_dp1.groupby([marketingCompany, priceType]).sum() # 各营业部求和
    top3_dp1 = top3_dp1.merge(top3_dp2, left_index=True,right_index=True)
    top3_dp1[sale] = top3_dp1[sale+'_x'] / top3_dp1[sale+'_y'] # 计算得到各营业部销量占比
    top3_dp1.drop([sale+'_x', sale+'_y'], axis=1, inplace=True)
    top3_dp3 = top3_dp.groupby([marketingCompany, priceType]).sum()
    top3_dp4 = top3_dp1.merge(top3_dp3, left_index=True,right_index=True)
    top3_dp4[sale] = top3_dp4[sale+'_x'] * top3_dp4[sale+'_y']
    top3_dp4.drop([sale+'_x', sale+'_y'], axis=1, inplace=True)
    top3_dp4.reset_index(inplace=True)


    # 将统一今麦郎各营业部数据按比例分配到各商圈
    ## 检查每一种品类的风度（即非0或非空样本的占比）
    def itemComplex(df): # 策略1
        itemList = list(df[priceType].drop_duplicates())
        # departList = list(df[priceType].drop_duplicates())
        df[priceType] = df[priceType].fillna(0) # 确保缺失值已转化为0
        df['r'] = 0
        lowCmpx =[]
        for i in itemList:
            df2 = df[df[priceType] == i]
            # 计算品项销量为0的占比,占比超30%的使用人口进行分配
            cmpx = len(df2[df2[sale]==0]) / len(df2)
            if cmpx > 0.3: 
                lowCmpx.append(i)
        if len(lowCmpx):
            for lc in lowCmpx:
                df.ix[df[priceType]==lc, 'r'] = 1
        return df
    
    def plusFactorWeight(df):# 策略2
        df1 = df.copy()
        df1['ratio'] = 0.9 * df1[sale] + 0.1 * df1[factorNum]

        # 计算最终营业部各商圈的占比，注意确保ratio之后为1
        df1s = df1.groupby([marketingCompany,salesDepartment,priceType],as_index=False).sum()
        df_m = df1.merge(df1s, on=[marketingCompany,salesDepartment,priceType],how='left')
        df_m['ratio'] = df_m['ratio'+'_x'] / df_m['ratio'+'_y']
        df_m2 = df_m[busAdInfo1+[priceType,'ratio']]
        
        return df_m2
    
    df_area_factor2 = df_area_factor[df_area_factor[factorType]=='人口'] # 目前只考虑使用人口进行分配
    df_area_factor2 = df_area_factor2[busAdInfo1+[factorNum]]
    ksf_bus2 = ksf_bus.merge(df_area_factor2, on=busAdInfo1,how='left')
    ksf_bus2s = ksf_bus2.groupby([marketingCompany, salesDepartment, priceType]).sum() # 各商圈求和
    ksf_bus1 = ksf_bus2.merge(ksf_bus2s, left_on=[marketingCompany, salesDepartment, priceType],right_index=True)
    ksf_bus1[sale] = ksf_bus1[sale+'_x'] / ksf_bus1[sale+'_y']
    ksf_bus1.drop([sale+'_x', sale+'_y'], axis=1, inplace=True)
    ksf_bus1[factorNum] = ksf_bus1[factorNum+'_x'] / ksf_bus1[factorNum+'_y'] # 计算得到各营业部销量占比
    ksf_bus1.drop([factorNum+'_x', factorNum+'_y'], axis=1, inplace=True)

    # 确保缺失值填0
    ksf_bus1 = ksf_bus1.fillna(0)
    ksf_bus1 = plusFactorWeight(ksf_bus1) # 选择了策略2
    ksf_bus3 = ksf_bus1.merge(top3_dp4, on=[marketingCompany, salesDepartment, priceType])
    ksf_bus3[sale] = ksf_bus3[sale] * ksf_bus3['ratio']
    ksf_bus3.drop('ratio', axis=1, inplace=True)
    ksf_bus3[manufacturer] = ''.join(top3ListEN)
    ksf_bus3[channel] = 'TT+MT'
    df_sale = pd.concat([df_sale, ksf_bus3])
    df_sale[sale] = df_sale[sale].fillna(0)
    df_sale[unit] = '箱'
    # 转化为包
    df_sale_pack = CapitaPackage(df_sale)
    df_sale = pd.concat([df_sale, df_sale_pack])
    
    df_sale[timeCol] = periodTag

    # 上传至数据库
    cm.toMysql(ksfSales, df_sale, updateTime, exMethod)


if __name__ == '__main__':
    filePath1 = '原始数据/全国业绩表5.25(PMI清整过版本-北京已修正6.5).xlsx'
    filePath2 = '原始数据/TY JML三年数据-三甲.xlsx'
    exMethod = mt['exMethod']
    exMethod2 = 'append'
    calSales(filePath1, filePath2, exMethod)

"""
开发中遇到的问题注释：
有商圈（即省、市和商圈）名都一样但行销公司或者营业部不一样的情况
"""

