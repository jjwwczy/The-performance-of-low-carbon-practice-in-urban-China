import pandas as pd
import numpy as np
import matplotlib
from fuzzywuzzy import process

def abbr_match(abbr_df,full_df):###传入缩写的列和完整的待匹配的列
    # 创建一个空字典来保存匹配结果
    matches = []

    # 遍历abbr_df中的每个缩写
    for abbreviation in abbr_df:
        # 使用fuzzywuzzy找到最佳匹配
        result = process.extractOne(abbreviation, full_df)
        match, score, _=result
        
        # 设置一个阈值来接受匹配，例如80
        if score > 80:
            matches.append(match)
        else:
            matches.append(None)  # 或者您可以选择其他表示未匹配的值
            print('{} 未匹配成功！匹配对象为{}, 匹配得分为{}!'.format(abbreviation,match,score))

    # 将结果转换为DataFrame
    matched_df = pd.DataFrame(matches,columns=['full'])
    return matched_df['full']


def get_df(datapath='./各维度打分表/居民.xlsx',indexdict=[7,12,17,36,39]):
    print('现在开始处理{}的数据！'.format(datapath.split('/')[-1][0:2]))
    Pindex,Iindex,Cindex,Oindex,Findex=tuple(indexdict)
    cur=pd.read_excel('./基于七普城区人口的城市分组(4组).xlsx')
    # 定义映射关系
    group_mapping = {1: '超大及特大城市', 2: '大城市', 3: '中等城市', 4: '小城市'}

    # 应用映射
    cur['分组'] = cur['分组'].map(group_mapping)
    if datapath.split('/')[-1][0:2]=='经济':
        data=pd.read_excel(datapath,sheet_name=0)
    else:
        data=pd.read_excel(datapath)
    # print(data.head())
    data=data.iloc[1:,:].fillna(0).reset_index(drop=True)
    citycolumn=data.columns[0]
    fullcityname=abbr_match(data[citycolumn],cur['城市'])
    data[citycolumn]=fullcityname
    ###打印缺失的城市####
    print('缺失的城市为:{}'.format([x for x in cur['城市'].values if x not in data[citycolumn].values]))
    groupdict=cur.set_index('城市')['分组']
    data['城市分类']=data[citycolumn].map(groupdict)
    ##P得分为第6列 ,依次类推，需要观察表格确定PICOF的得分
    weights = [0.2, 0.2,	0.15,	0.3,	0.15]  # 得分权重需要手动设定 
    # weights = [0.2, 0.2, 0.2, 0.2, 0.2]
    P = pd.to_numeric(data.iloc[:, Pindex], errors='coerce')
    I = pd.to_numeric(data.iloc[:, Iindex], errors='coerce')
    C = pd.to_numeric(data.iloc[:, Cindex], errors='coerce')
    O = pd.to_numeric(data.iloc[:, Oindex], errors='coerce')
    F = pd.to_numeric(data.iloc[:, Findex], errors='coerce')

    data['总分'] = (P * weights[0] + I * weights[1] + C * weights[2] + O * weights[3] + F * weights[4])

    score=data['总分']
    cityname=data[citycolumn]
    group=data['城市分类']
    newdf=pd.DataFrame()
    newdf['城市名']=cityname
    newdf['分组']=group
    newdf['P(规划)']=P
    newdf['I(实施)']=I
    newdf['C(检查)']=C
    newdf['O(结果)']=O
    newdf['F(反馈)']=F
    newdf['score']=score


    # 将newdf和cur按照城市名设置为索引
    newdf.set_index('城市名', inplace=True)
    cur.set_index('城市', inplace=True)

    # 使用cur的索引重新排列newdf
    sorted_newdf = newdf.reindex(cur.index)
    sorted_newdf.index.name = '城市名'

    # 重置索引，如果需要
    sorted_newdf.reset_index(inplace=True)
    ####删去三沙市####
    sorted_newdf=sorted_newdf.drop(sorted_newdf[sorted_newdf['城市名']=='三沙市'].index)
    sorted_newdf.to_excel('./各维度打分表/'+datapath.split('/')[-1][0:2]+'_处理后.xlsx',index=0)
    return sorted_newdf

