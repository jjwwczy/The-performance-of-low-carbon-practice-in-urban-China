from process import get_df
from drawfigures import parallel_coordinate_plot_PICOF,parallel_coordinate_plot_total,score_map,plot_radar_chart, \
scatter_plot_with_regression_lines,analyze_city_groups_with_intervals,plot_radar_chart_single_group,plot_cloud_rain_ptitprince,create_pie_charts,format_score_and_rank,\
plot_distribution,plot_all_cities_in_one_figure,abbr_match,extract_citygroup_citylist,plot_citygroup_radar_chart,inside_citygroup_parallel_coordinates,plot_grouped_boxplot,\
plot_grouped_scatter_with_mean_line,plot_single_distribution,match_city_data_final,gpd_scoremap,plot_radar_chart_single_group_combine,calculate_and_save_cv_to_excel,gpd_scoreheatmap
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import boxcox
import geopandas as gpd
# import geoplot as gplt
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

####指定PICOF分数的列数###
indexdicts={
            '能源':[4,9,14,18,22],
            '经济':[6,12,16,25,28],
            '效率':[2,3,4,5,6],
            '居民':[7,12,17,36,39],

           '水域':[5,10,15,19,22],
           '森林':[13,2,3,14,5],
           '绿地':[7,1,2,5,3],
           '技术':[1,2,3,4,5],
           }
newdf=pd.DataFrame()
cur=pd.read_excel('./基于七普城区人口的城市分组(4组).xlsx')
newdf['城市名']=cur['城市']


newdf['分组']=cur['分组']
# 定义映射关系
group_mapping = {1: '超大及特大城市', 2: '大城市', 3: '中等城市', 4: '小城市'}

# 应用映射
newdf['分组'] = newdf['分组'].map(group_mapping)
for dimension_name in indexdicts.keys():
    data=get_df(datapath='./各维度打分表/'+dimension_name+'.xlsx',indexdict=indexdicts[dimension_name])

    # 选择 '城市名' 和 '能源' 列进行合并
    dimension_data = data[['城市名', 'score']].rename(columns={'score': dimension_name})
    newdf = pd.merge(newdf,dimension_data, on='城市名', how='left')
    parallel_coordinate_plot_PICOF(data,dimension_name,'分组')#####画各维度内的环节图
    # plot_radar_chart(data,dimension_name)



total_data = newdf.dropna().copy()####删去含有空值的行


#能源结构	经济发展	城市居民	生产效率	水域碳汇	森林碳汇	绿地碳汇	低碳技术
weight=[0.25,	0.1,	0.1,	0.1,	0.1,	0.1,	0.1,	0.15]
# weight=[0.125,0.125,0.125,0.125,0.125,0.125,0.125,0.125]
if len(weight) == total_data.iloc[:, 2:].shape[1]:
    total_data['score'] = np.dot(total_data.iloc[:, 2:], weight)
else:
    print("权重数量与列数量不匹配")

parallel_coordinate_plot_total(total_data,'分组')#####画8维度的平行坐标图


with open('运行记录.txt', 'w',encoding='utf-8') as file:
    file.write('p值取0.05\n')
####画八维度与总分的散点图##########
for dimension_name in indexdicts.keys():
    mu, std=scatter_plot_with_regression_lines(total_data,dimension_name)
    # 执行 Shapiro-Wilk 测试

    shapiro_test_stat, shapiro_p_value = stats.shapiro(total_data[dimension_name])
    # 判断 p 值
    if shapiro_p_value > 0.05:
        with open('运行记录.txt', 'a',encoding='utf-8') as file:
            file.write((dimension_name+"数据看似符合正态分布, p:{:.4f}, mu(均值):{:.2f}, std(方差):{:.2f}\n".format(shapiro_p_value,mu,std)))
    else:
        with open('运行记录.txt', 'a',encoding='utf-8') as file:
            file.write(dimension_name+"数据看似不符合正态分布, p:{:.4f}, mu(均值):{:.2f}, std(方差):{:.2f}\n".format(shapiro_p_value,mu,std))

mu, std = np.mean(total_data["score"]), np.std(total_data["score"])
shapiro_test_stat, shapiro_p_value = stats.shapiro(total_data['score'])

# 判断 p 值
if shapiro_p_value > 0.05:
    with open('运行记录.txt', 'a',encoding='utf-8') as file:
        file.write(("总分数据看似符合正态分布, p:{:.4f}, mu(均值):{:.2f}, std(方差):{:.2f}\n".format(shapiro_p_value,mu,std)))
else:
    with open('运行记录.txt', 'a',encoding='utf-8') as file:
        file.write("总分数据看似不符合正态分布, p:{:.4f}, mu(均值):{:.2f}, std(方差):{:.2f}\n".format(shapiro_p_value,mu,std))


######画八维度的雷达图########
# radar_name='八维度'
# plot_radar_chart(total_data,radar_name)

#######画八维度的组别占比矩阵并保存excel#######
total_data, _ =analyze_city_groups_with_intervals(total_data,'八维度')
dimension_rank=format_score_and_rank(total_data,dimensions=['能源', '经济', '效率','居民', '水域', '森林', '绿地', '技术'])
pivot_total_data=create_pie_charts(total_data,'八维度', mode='梯队')
pivot_total_data2=create_pie_charts(total_data,'八维度', mode='规模')

with pd.ExcelWriter('./各维度打分表/'+'汇总表.xlsx') as writer:
    # Write the main DataFrame to the first sheet
    total_data.to_excel(writer, sheet_name='Sheet1', index=False)
    dimension_rank.to_excel(writer, sheet_name='维度得分与排名',index=False)
    pivot_total_data.to_excel(writer, sheet_name=f'八维度_梯队分布表')


##############画城市群的蛛网图##################
cur=pd.read_excel('./基于七普城区人口的城市分组(4组).xlsx')
match_path='城市群/匹配结果记录.txt'
with open(match_path, 'w',encoding='utf-8') as file:
    file.write('城市群      未匹配到的城市\n')
# Test the function
extracted_dict = extract_citygroup_citylist('城市群名单.xlsx')
group_stats = {}
#####城市群颜色表############
group_colors=list(sns.color_palette("husl", 11).as_hex())

for idx,citygroup in enumerate(extracted_dict.keys()):
    citygroup_cities_df = pd.DataFrame(extracted_dict[citygroup], columns=['城市名'])
    citycolumn=citygroup_cities_df.columns[0]
    fullcityname,unmatch=abbr_match(citygroup_cities_df[citycolumn],cur['城市'])
    with open(match_path, 'a',encoding='utf-8') as file:
        file.write(f'{citygroup}        {unmatch}\n')
    citygroup_cities_df[citycolumn]=fullcityname
    citygroup_cities_df = citygroup_cities_df.dropna().reset_index(drop=True)
    citylist=citygroup_cities_df['城市名'].tolist()
    # plot_citygroup_radar_chart(total_data, citygroup, citylist)
    group_color=group_colors[idx]
    plot_all_cities_in_one_figure(total_data, citygroup, citylist,group_color)
    
    citygroup_data = total_data[total_data['城市名'].isin(citylist)]
    selected_dimensions = citygroup_data.columns[2:10]  # 这里选择了前8个维度作为示例，你可以根据实际情况进行选择
    # inside_citygroup_parallel_coordinates(citygroup,citygroup_data, selected_dimensions, marker_size=8)
    group_stats[citygroup] = citygroup_data
##########城市群################
# plot_grouped_boxplot(group_stats, 'score')
plot_grouped_scatter_with_mean_line(group_stats, 'score')
calculate_and_save_cv_to_excel(group_stats, 'score')




# shapefile_path='./city.shp'
shapefile_path='./2023年地级.shp'

shapefile_gdf=gpd.read_file(shapefile_path)
shapefile_gdf = shapefile_gdf.to_crs(epsg=4545)

# Test the updated match_city_data function
matched_gdf= match_city_data_final(shapefile_gdf, total_data)

cur_name='总分'
# score_map(total_data,cur_name)
gpd_scoremap(cur_name,shapefile_gdf, matched_gdf,group_col= '得分分组', group_order=['第一梯队', '第二梯队', '第三梯队', '第四梯队'])
# gpd_scoremap('规模分布',shapefile_gdf, matched_gdf,group_col= '分组', group_order=['超大及特大城市', '大城市', '中等城市', '小城市'])
gpd_scoreheatmap(shapefile_gdf, matched_gdf)

# parallel_coordinate_plot_total(total_data,'得分分组')#####画8维度的平行坐标图


####画各维度的分布图########

####画各维度的分布图########
columns = 'score'
labels = '(a) Overall Score'

plot_single_distribution(total_data, columns, labels, save_filename='总分')


columns = ['能源', '经济', '效率','居民', '水域', '森林', '绿地', '技术']
labels = ['(a) Energy Structure', '(b) Economic Development', '(c) Production Efficiency', '(d) Urban Population', '(e) Water Carbon Sink', '(f) Forest Carbon Sink', '(g) Green Space Carbon Sink', '(h) Low-carbon Technology']

plot_distribution(total_data, columns, labels, save_filename='八维度')


####画单组别的雷达图####
citydict1={'超大及特大城市':['北京市','杭州市','上海市'],
           '大城市':['宁波市','吉林市','温州市'],
           '中等城市':['荆门市','六安市','湖州市'],
           '小城市':['广元市','嘉峪关市','吉安市']}
plot_radar_chart_single_group(total_data,'分组',citydict1)
plot_radar_chart_single_group_combine(total_data, '分组')#####画各维度内的环节图
citydict2={'第一梯队':['北京市','杭州市','上海市'],
           '第二梯队':['宁波市','南京市','成都市'],
           '第三梯队':['包头市','泉州市','常德市'],
           '第四梯队':['鸡西市','常州市','濮阳市']}
plot_radar_chart_single_group(total_data,'得分分组',citydict2)
plot_radar_chart_single_group_combine(total_data, '得分分组')#####画各维度内的环节图


 
interval_data = []


##分析各维度的组别并保存excel#####
for dimension_name in indexdicts.keys():
    df=pd.read_excel('./各维度打分表/'+dimension_name+'_处理后.xlsx')
    df, score_intervals = analyze_city_groups_with_intervals(df,dimension_name+'维度')
    pivot_data=create_pie_charts(df,dimension_name, mode='梯队')
    pivot_data2=create_pie_charts(df,dimension_name, mode='规模')
    columns=['P(规划)','I(实施)','C(检查)','O(结果)','F(反馈)']
    labels=['(a) P(规划)','(b) I(实施)','(c) C(检查)','(d) O(结果)','(e) F(反馈)']
    plot_distribution(df, columns, labels, save_filename=dimension_name)

    # Add a new row to the result DataFrame
    new_row = {'低碳建设维度': dimension_name}
    new_row.update(score_intervals)
    # print(new_row)
    interval_data.append(new_row)
    PICOF_rank=format_score_and_rank(df,['P(规划)','I(实施)','C(检查)','O(结果)','F(反馈)'],top_header="环节（得分|排名)")
    citydict={'超大及特大城市':1,
           '大城市':2,
           '中等城市':3,
           '小城市':4}
    PICOF_rank['城市规模组']=df['分组'].map(citydict)
    with pd.ExcelWriter(f'./各维度打分表/{dimension_name}_处理后.xlsx') as writer:
        # Write the main DataFrame to the first sheet
        df.to_excel(writer, sheet_name='sheet1', index=False)
        
        # Write the pivot table to another sheet
        pivot_data.to_excel(writer, sheet_name=f'{dimension_name}_梯队分布表')
        PICOF_rank.to_excel(writer, sheet_name='环节得分与排名',index=False)

    # plot_cloud_rain_ptitprince(df, 'score', '分组',dimension_name+'维度')
    # plot_cloud_rain_ptitprince(df, 'score', '得分分组',dimension_name+'维度')
    # parallel_coordinate_plot_PICOF(df,dimension_name,'得分分组')#####画各维度内的环节图
    # score_map(df,dimension_name)
    matched_gdf= match_city_data_final(shapefile_gdf, df)

    gpd_scoremap(dimension_name,shapefile_gdf, matched_gdf,group_col= '得分分组', group_order=['第一梯队', '第二梯队', '第三梯队', '第四梯队'])


interval_df = pd.DataFrame(interval_data)

with pd.ExcelWriter('./各维度打分表/'+'汇总表.xlsx',mode='a',engine='openpyxl') as writer:
    # Write the main DataFrame to the first sheet
    interval_df.to_excel(writer, sheet_name='梯队区间', index=False)


plot_cloud_rain_ptitprince(total_data, 'score', '分组')
plot_cloud_rain_ptitprince(total_data, 'score', '得分分组')




# Step 1: 对DataFrame按照'score'列进行排序并添加排名列
def add_ranking_column(df):
    df_sorted = df.sort_values(by='score', ascending=False)
    df_sorted['排名'] = range(1, len(df_sorted) + 1)
    return df_sorted

# 对total_data添加排名列
total_data_ranked = add_ranking_column(total_data)

# 对每一个维度的数据添加排名列
dimension_dfs_ranked = {}
tiduidict={'第一梯队':'A',
           '第二梯队':'B',
           '第三梯队':'C',
           '第四梯队':'D'}

tidui_df=pd.DataFrame()
for dimension_name in indexdicts.keys():
    df = pd.read_excel('./各维度打分表/'+dimension_name+'_处理后.xlsx')
    dimension_dfs_ranked[dimension_name] = add_ranking_column(df)
    df = df[['城市名', '得分分组']]
    df['得分分组']=df['得分分组'].map(tiduidict)
    df.rename(columns={'得分分组': f'{dimension_name}'}, inplace=True)
    
    # 如果final_df为空，则填充第一个维度的数据
    if tidui_df.empty:
        tidui_df = df
    else:
        # 合并数据
        tidui_df = pd.merge(tidui_df, df, on='城市名', how='outer')



# Step 2: 使用ExcelWriter保存到一个Excel文件的不同工作表里
with pd.ExcelWriter('./各维度打分表/总分及各维度整合表.xlsx') as writer:
    total_data_ranked.to_excel(writer, sheet_name='总分', index=False)
    tidui_df.to_excel(writer, sheet_name='梯队等级表', index=False)

    for dimension_name, df_ranked in dimension_dfs_ranked.items():
        df_ranked.to_excel(writer, sheet_name=f'{dimension_name}', index=False)

