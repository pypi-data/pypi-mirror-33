import os
import sys
import numpy as np
import pandas as pd
from scipy import stats
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

# 提取QB1、QB2、QB3、QB4、QB3.1、QB5
def extract_data2(qtag, qtag_list, brand_list):
    # 多选题，将各选项纵向叠加
    for index, i in enumerate(qtag_list):
        df1 = df.loc[:, list_essential1]
        try:
            df1[qtag] = df[i]
            df2 = df1 if not index else df2.append(df1)
        except:
            continue

    # 使用透视表转换数据格式, 注意，其他就用其他栏统计的结果得到extract_data2的统计方式可借鉴此方法
    df2.replace(0, np.nan, inplace=True)
    df_city = pd.pivot_table(df2,index=[city_tag], columns=[qtag], values=[CODE], aggfunc=np.size)
    df_city = df_city['CODE'].loc[:, brand_list]
    df_sex = pd.pivot_table(df2,index=[sex_tag], columns=[qtag], values=[CODE], aggfunc=np.size)
    df_sex = df_sex['CODE'].loc[:, brand_list]
    df_age = pd.pivot_table(df2,index=[age_tag], columns=[qtag], values=[CODE], aggfunc=np.size)
    df_age = df_age['CODE'].loc[:, brand_list]
    df_rsjd = pd.pivot_table(df2,index=[rsjd_tag], columns=[qtag], values=[CODE], aggfunc=np.size)
    df_rsjd = df_rsjd['CODE'].loc[:, brand_list]

    # 周期，total
    df_period1 = df_city
    df_period2 = df_period1.apply(lambda x: x * df_weight.iloc[:, 0])
    total_list = list(df_period2.sum() / Base)
    total_list.insert(0, Base)

    # 处理城市、性别、年龄段和人生阶段
    df_city = df_city.apply(lambda x: x / city_base)
    df_city.insert(0, 'base', city_base)
    df_sex = df_sex.apply(lambda x: x / sex_base)
    df_sex.insert(0, 'base', sex_base)
    df_age = df_age.apply(lambda x: x / age_base)
    df_age.insert(0, 'base', age_base)
    df_rsjd = df_rsjd.apply(lambda x: x / rsjd_base)
    df_rsjd.insert(0, 'base', rsjd_base)
    
    return total_list, df_city.T, df_sex.T, df_age.T, df_rsjd.T


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

# 用于QB8-14
def period_proc2(qtag, sht, period_num, row_num, col_num_starting, vertical_length, total_list):
    # 获取各周期数据
    period_file = '%s_period_data.xlsx' % qtag
    if os.path.exists(period_file):
        df_total = pd.read_excel(period_file, usecols=period_num-2)
        df_total[period_num-1] = data_list
        df_total_percent, total_temp = df_total.drop(0), list(df_total.loc[0])
    else:
        df_total_percent, total_temp = extract_digit(sht, period_num, row_num-1, col_num_starting, vertical_length, total_list)
    # 改掉total_temp
    total_temp = list(sht.range((6, col_num_starting),(6, col_num_starting+period_num-1)).value)
    
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
        if j_sum:
            total_percent_list.append(i_sum / j_sum)
        else:
            total_percent_list.append(0)

    # total_percent_list.insert(0, sum(total_temp))
    # 将df_total['sum']列写入sheet <2.外食情况>的 Total列
    sht.range(row_num, col_num_starting-1).options(transpose=True).value = total_percent_list
    # 写入Base行
    # total_temp.insert(0, sum(total_temp))
    #sht.range(6, col_num_starting).value = total_temp
    # 标记显著性数值，并写入sheet <2.外食情况>
    mark_significance(df_total_percent, total_temp, sht, row_num-1, col_num_starting)




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

# 用于QB8-
def csar_proc2(qtag, sht, period_num, row_num, col_num_starting, vertical_length, df_city, df_sex, df_age, df_rsjd):
    # 修改row_num
    row_num = row_num - 1
    complete_city_list = ['成都', '哈尔滨', '西安', '郑州', '福州', '杭州']
    df_city_proc = dimension_proc(df_city, complete_city_list, vertical_length)
    for index, column in enumerate(df_city_proc.columns):
        # city_file = '%s_period_%s_data.xlsx' % qtag 这个功能后面再添加
        # 使用col_num2跟踪移动列
        col_num2 = col_num_starting + period_num * (index + 1)
        df_digit_percent, base_temp = extract_digit(sht, period_num, row_num, col_num2, vertical_length, df_city_proc[column])
        # 改掉base_temp
        base_temp = list(sht.range((6, col_num2),(6, col_num2+period_num-1)).value)
        # 先写入base数据
        # sht.range(row_num, col_num2).value = base_temp
        # 标记显著性数值，并写入sheet <2.外食情况>
        mark_significance(df_digit_percent, base_temp, sht, row_num, col_num2)

    # 按顺序填入性别信息，***性别没有考虑缺失数据的情况
    complete_sex_list = ['男性', '女性']
    df_sex_proc = dimension_proc(df_sex, complete_sex_list, vertical_length)
    for column in df_sex_proc.columns:
        index += 1  # 使用col_num2跟踪移动列
        col_num2 = col_num_starting + period_num * (index + 1)
        df_digit_percent, base_temp = extract_digit(sht, period_num, row_num, col_num2, vertical_length, df_sex_proc[column])
        # 改掉base_temp
        base_temp = list(sht.range((6, col_num2),(6, col_num2+period_num-1)).value)
        # 先写入base数据
        # sht.range(row_num, col_num2).value = base_temp
        # 标记显著性数值，并写入sheet <2.外食情况>
        mark_significance(df_digit_percent, base_temp, sht, row_num, col_num2)

    # 按顺序填入各年龄段信息
    complete_age_list = ['15-19岁', '20-24岁', '25-29岁', '30-34岁', '35-39岁']
    df_age_proc = dimension_proc(df_age, complete_age_list, vertical_length)
    for column in df_age_proc.columns:
        index += 1  # 使用col_num2跟踪移动列
        col_num2 = col_num_starting + period_num * (index + 1)
        df_digit_percent, base_temp = extract_digit(sht, period_num, row_num, col_num2, vertical_length, df_age_proc[column])
        # 改掉base_temp
        base_temp = list(sht.range((6, col_num2),(6, col_num2+period_num-1)).value)
        # 先写入base数据
        # sht.range(row_num, col_num2).value = base_temp
        # 标记显著性数值，并写入sheet <2.外食情况>
        mark_significance(df_digit_percent, base_temp, sht, row_num, col_num2)

    # 按人生阶段填入各年龄段信息
    complete_rsjd_list = ['青少年&学生', '青年', '壮年', '家庭']
    df_rsjd_proc = dimension_proc(df_rsjd, complete_rsjd_list, vertical_length)
    for column in df_rsjd_proc.columns:
        index += 1  # 使用col_num2跟踪移动列
        col_num2 = col_num_starting + period_num * (index + 1)
        df_digit_percent, base_temp = extract_digit(sht, period_num, row_num, col_num2, vertical_length, df_rsjd_proc[column])
        # 改掉base_temp
        base_temp = list(sht.range((6, col_num2),(6, col_num2+period_num-1)).value)
        # 先写入base数据
        # sht.range(row_num, col_num2).value = base_temp
        # 标记显著性数值，并写入sheet <2.外食情况>
        mark_significance(df_digit_percent, base_temp, sht, row_num, col_num2)



def processing_type2(qtag, sht, period_num, row_num, col_num_starting, vertical_length, brand_list=brand_list):
    qtag_list = list(df_qa.loc[qtag].dropna())
    total_list, df_city, df_sex, df_age, df_rsjd = extract_data2(qtag, qtag_list, brand_list)

    # 处理并填入"周期"信息
    period_proc1(qtag, sht, period_num, row_num, col_num_starting, vertical_length, total_list)
    # 处理城市、性别、年龄段和人生阶段
    csar_proc1(qtag, sht, period_num, row_num, col_num_starting, vertical_length, df_city, df_sex, df_age, df_rsjd)


def processing_type4(qtag, sht, period_num, row_num, col_num_starting, vertical_length, brand_list):
    qtag_list = list(df_qa.loc[qtag].dropna())
    total_list, df_city, df_sex, df_age, df_rsjd = extract_data2(qtag, qtag_list, brand_list)

    # 处理并填入"周期"信息
    period_proc2(qtag, sht, period_num, row_num, col_num_starting, vertical_length, total_list)
    # 处理城市、性别、年龄段和人生阶段
    csar_proc2(qtag, sht, period_num, row_num, col_num_starting, vertical_length, df_city, df_sex, df_age, df_rsjd)



# T-test
def mark_significance2(list1, list2, list3, sht, row_num, col_num):
    def ttest(u1, u2, n1, n2, v1, v2):
		f = n1+n2-2
        t = abs((u1 - u2) / np.sqrt( ((n1-1)*v1+(n2-1)*v2) * (n1+n2) / (f*n1*n2)))
		p = stats.t.cdf(t,df=f)
        return p < 0.05

    # df_percent.replace(0, np.nan, inplace=True)
	# df_percent.replace('-', np.nan, inplace=True)

	u_proc_list = []
	for index1, (u1, n1, v1) in enumerate(zip(list1, list2, list3)):
		u1_proc = str(u1) + "("  # 有显著的数值不保留小数点后有效数字
		tag_significance = False
		for index2, (u2, n2, v2) in enumerate(zip(list1, list2, list3)):
			if u1 > u2:
				if ttest(u1, u2, n1, n2, v1, v2):
					# u1高于u2且显著时，在u1后面标记u2的位置
					u1_proc = u1_proc + chr(index2+97).upper()
					# 如果u1有经过标记处理，则tag_significance为True
					tag_significance = True
		if tag_significance:
			u1_proc += ")"
		else:
			u1_proc = u1
		# 写入Base
		sht.range(row_num+index, index1+col_num).value = n1
		if type(p1_proc) == str:
			# 写入显著性数值
			sht.range(row_num+index+1, index1+col_num).value = u1_proc
			sht.range(row_num+index+1, index1+col_num).color = (253,245,230)
		else:
			if np.isnan(p1_proc): # 判断缺失值的唯一方法,注意np.isnan('94%(D)')会报错
				# 写入缺失数据
				p1_proc = 0
			sht.range(row_num+index+1, index1+col_num).value = p1_proc
			sht.range(row_num+index+1, index1+col_num).color = (255,255,255)


def processing_qb15(qtag, sht, period_num, row_num, col_num_starting, vertical_length, brand_list):
    # qtag_list = list(df_qa.loc[qtag].dropna())
	# 时间有限，暂时省略基本计算。
	## 直接t检验
    period_file = '%s_period_data.xlsx' % qtag
	period_file = '%s_period_data.xlsx' % qtag
	df1 = pd.read_excel(period_file, , index_col=[2,0,1])
	df1.replace(0, np.nan, inplace=True)
	df1.replace('-', np.nan, inplace=True)
    # 获取各周期数据
	df1_period = df1.loc['周期']
	# df1[period_tag] = list

	period_base = df1.loc['Base'].loc['周期'].values
	period_mean = df1.loc['Mean'].loc['周期'].values
	# 写入'Total'列
	for index, (b, m) in enumerate(zip(period_base, period_mean)):
		sht.range(row_num+index, col_num-1).value = b.sum()
		sht.range(row_num+index+1, col_num-1).value = np.multiply(b, m).sum() / b.sum() # multiply为向量内积
		
	Mean = df1.loc['Mean'].values
	Base = df1.loc['Base'].values
	Variance = df1.loc['Variance'].values
	for index, (list1, list2, list3) in enumerate(zip(Mean, Base, Variance)):
		 mark_significance2(list1, list2, list3)


def BIT_automation(filepath1, filepath2, filepath3, filepath4, period_num):
    global wb, df, df_qa, df_weight, Base, city_base, sex_base, age_base, rsjd_base, period_tag
	# 处理period_num
	try:
		period_list = period_num.split('-')
		period_start = int(period_list[0].strip('Ww'))
		if len(period_list) == 2:
			period_end = int(period_list[1].strip('Ww'))
		elif len(period_list) == 1:
			period_end = period_start + 3
		period_list = range(period_start, period_end+1)
		period_list = list(map(lambda x: 'W'+str(x), period_list))
		period_num = period_end / 4 - 8
		period_tag = 'W%s-W%s ' % (str(period_start), str(period_end))
	except err:
		print(err)
    # 提取问卷数据
    ## 打开问卷信息文件，该数据已经清洗过 
    df = pd.read_excel(filepath2)
	df = df[df['S0'].isin(period_list)]
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


    # 读取<4.品牌购买与食用> sheets
    sht4 = wb.sheets['4.品牌购买与食用']
    """brand_list2 = ['肯德基', '德克士', '麦当劳', '华莱士', '汉堡王', '其他']
    row_num = 6
    processing_type2('QB7' , sht4, period_num, row_num, 4, 6, brand_list2)
    for i in range(1, 8):
        qtag = 'QB' + str(7 + i)
        row_num = 7 + i * 6
        processing_type4(qtag, sht4, period_num, row_num, 4, 6, brand_list2)"""
    
	## 处理Q15
	df_w = 

if __name__ == "__main__":
    filepath = 'ts2.xlsx' #sys.argv[1]
    period_num = 4 #int(sys.argv[2])
    BIT_automation(filepath)






