import os
import pandas as pd


def cal_shipment(df):
    # 纳入计算的品类名单
    category_list = ['容器面', '高价袋','中价面',"平低价","干脆面",
         '容器面.1', '高价袋.1','中价面.1',"平低价.1","干脆面.1",
         '容器面.2', '高价袋.2','中价面.2',"平低价.2","干脆面.2"]
    # 提取上述三部分信息
    df = df[['区/县', '具体描述'] + category_list]
    # 处理区域、商圈信息的合并单元格
    df[['区/县', '具体描述']] = df[['区/县', '具体描述']].fillna(method="pad")
    # 这一步很重要。各品类出货量数字合并单元格需填0处理
    df[category_list] = df[category_list].fillna(0)
    # 获取一区多商圈的样本
    split_df = df.loc[:, ['具体描述','区/县']]
    split_df.drop_duplicates(['具体描述','区/县'], inplace=True)
    split_df1 = split_df.groupby(['区/县']).count()
    split_df2 = split_df1[split_df1['具体描述'] > 1].reset_index()
    # 计算区县分销量
    split_df3 = split_df2.loc[:,['区/县']].merge(df.loc[:, ['区/县','具体描述','容器面.2', '高价袋.2','中价面.2',
                             "平低价.2","干脆面.2"]],on='区/县', how='left')
    split_df3['区县分销量'] = split_df3.loc[:, ['容器面.2', '高价袋.2','中价面.2',"平低价.2","干脆面.2"]].sum(axis=1)
    # 如存在一商圈多经销部，则合并商圈销量
    split_df4 = split_df3.groupby(['区/县', '具体描述'], as_index=False).sum()[['区/县', '具体描述', '区县分销量']]
    split_df4.set_index('区/县', inplace=True)
    split_df4['区县总销量'] = split_df4.groupby('区/县').sum()
    #split_df5 = split_df5.reset_index(level='区/县')
    allocation_df = split_df.merge(split_df4.reset_index(), on=['具体描述','区/县'], how='outer')
    allocation_df.columns = ['具体描述','区县', '区县分销量', '区县总销量']
    allocation_df.set_index(['具体描述','区县'], inplace=True)
    # 营业部放第一列
    final_df=df.groupby(['具体描述']).sum()
    return final_df, allocation_df

def sum_TT_MT(path, TT_file,MT_file, province):
    # 读取TT数据表, TT数据必须放在活动sheet
    df1 = pd.read_excel(TT_file,skiprows=2)
    # 读取MT数据表
    try:
        df2 = pd.read_excel(MT_file,skiprows=2, sheetname='MT(不含后面3张sheet标红系统)')
    except:
        # MT出货数据存放的sheet在活动sheet中
        df2 = pd.read_excel(MT_file,skiprows=2)
    
    # 此接口可灵活增减额外信息，比如经销商信息
    add_info = ['具体描述','省','市','区/县','营业部',"现有经销商/物流公司名称","客户形态","现有经销商/物流公司代码"]
    df_info = df1[add_info].fillna(method="pad")
    df_info.set_index('具体描述', inplace=True)
    TT_df, TT_allocation_df = cal_shipment(df1)
    MT_df, MT_allocation_df = cal_shipment(df2)
    TTMT_df = TT_df.copy()
    TTMT_allocation_df = TT_allocation_df.copy()
    # merged_df=pd.merge(TT_df,MT_df,on=["具体描述"])
    # 营业部在第一列
    for spec in TT_df:
        TTMT_df[spec] = TTMT_df[spec] + MT_df[spec]
    
    # 计算各区县分配系数
    for row in TT_allocation_df.columns:
        TTMT_allocation_df[row] = TTMT_allocation_df[row] + MT_allocation_df[row]
    TTMT_allocation_df['区县分配系数'] = TTMT_allocation_df['区县分销量'] / TTMT_allocation_df['区县总销量']
    TTMT_allocation_df['区县分配系数'] = TTMT_allocation_df['区县分配系数'].fillna(1)
    # 输出KSF各商圈TT&MT出货
    writer=pd.ExcelWriter(os.path.join(path, "{0}KSF各商圈TT&MT出货.xlsx".format(province)))
    TTMT_df.to_excel(writer,sheet_name="TT&MT", merge_cells=False)
    TT_df.to_excel(writer,sheet_name="TT", merge_cells=False)
    MT_df.to_excel(writer,sheet_name="MT", merge_cells=False)
    writer.save()
    # KSF各商圈区县分配系数
    writer2=pd.ExcelWriter(os.path.join(path, "{0}KSF各商圈区县分配系数.xlsx".format(province)))
    TTMT_allocation_df.to_excel(writer2,sheet_name="TT&MT", merge_cells=False)
    TT_allocation_df.to_excel(writer2,sheet_name="TT", merge_cells=False)
    MT_allocation_df.to_excel(writer2,sheet_name="MT", merge_cells=False)
    writer2.save()
    # 输出商圈经销商等额外信息
    df_info.to_excel('%s商圈信息.xlsx' % province)


if __name__ == '__main__':
    province = '湖北省'
    TT_file = '湖北业绩数据（TT+MT）.xlsx'
    MT_file = '湖北业绩数据（TT+MT）.xlsx'
    path = os.path.dirname(TT_file)
    sum_TT_MT(path, TT_file,MT_file, province)
    
