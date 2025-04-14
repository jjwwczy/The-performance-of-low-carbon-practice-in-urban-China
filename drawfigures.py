import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pyecharts import options as opts
from pyecharts.charts import Radar
from pyecharts.charts import Map
from pyecharts.render import make_snapshot
import ptitprince as pt
from matplotlib.collections import PathCollection
import matplotlib.lines as mlines
from scipy.stats import linregress, norm, gaussian_kde
from fuzzywuzzy import process
import os
import itertools
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib_scalebar.scalebar import ScaleBar
font_size=24


# universal_colors = ['#4CAF50', '#2196F3', '#854085', '#737373']######绿蓝紫灰  版本一
# universal_colors = ['#008000', '#0000FF', '#800080', '#808080']######绿蓝紫灰  版本二
# universal_colors = ['#66c2a5', '#8da0cb', '#e78ac3', '#b3b3b3']######绿蓝紫灰  版本三

# universal_colors = ['#2ecc71', '#3498db', '#9b59b6', '#34495e']######绿蓝紫灰  版本四
# universal_colors = ['#2ecc71', '#3498db', '#9b59b6', '#95a5a6']######绿蓝紫灰  版本5
universal_colors = ['#c6dfb8', '#e8e7bb', '#bccbe8', '#d5ebf0']######

# universal_colors= ['#3BDC3C','#3770DB','#DB6100','#D40DDB']###########绿蓝橙红
# plt.rcParams['font.sans-serif']='Arial Unicode MS'###mac

plt.rcParams['font.sans-serif']='Arial Unicode MS'
plt.rcParams['axes.unicode_minus'] = False    # 解决无法显示符号的问题
plt.rcParams['font.size'] = font_size
title_fontsize=30


def parallel_coordinate_plot_PICOF(data, dimension_name, groupname):
    namelist = ['P(规划)', 'I(实施)', 'C(检查)', 'O(结果)', 'F(反馈)']
    
    # Calculate the mean for each group
    group_means = data.groupby(groupname)[namelist].mean().reset_index()
    group_means['城市名'] = '组均值'
    
    # Merge the group means with the original data
    plot_data = pd.concat([data, group_means], ignore_index=True)
    
    # Create a 2x2 grid of subplots
    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
    axs = axs.flatten()
    plt.subplots_adjust(wspace=0.3, hspace=0.3)

    sorted_groups = ['超大及特大城市', '大城市', '中等城市', '小城市'] if groupname == '分组' else ['第一梯队', '第二梯队', '第三梯队', '第四梯队']
    savename = '规模分组' if groupname == '分组' else '得分分组'
    prefixes = ['(a)', '(b)', '(c)', '(d)']  # 前缀列表

    # Loop over subplots to plot each group
    for idx, (ax, group) in enumerate(zip(axs, sorted_groups)):
        group_data = plot_data[plot_data[groupname] == group]
        if groupname == '分组':
            group_color='black'
        else:
            group_color = universal_colors[idx]
        
        custom_lines = []
        labels = []
        
        # Plot lines for each city
        for index, city_data in enumerate(group_data.iterrows()):
            _, city_data = city_data
            if city_data['城市名'] != '组均值':
                ax.plot(namelist, city_data[namelist], color=group_color, alpha=0.2)
        
        # Add custom line for individual cities
        custom_line = mlines.Line2D([], [], color=group_color, linewidth=1, alpha=0.8)
        custom_lines.append(custom_line)
        labels.append(f'{group}')
        
        # Plot line for group mean
        mean_data = group_data[group_data['城市名'] == '组均值']
        ax.plot(namelist, mean_data[namelist].values[0], color=group_color, linewidth=4)
        
        # Add custom line for group mean
        custom_line_mean = mlines.Line2D([], [], color=group_color, linewidth=4)
        custom_lines.append(custom_line_mean)
        labels.append(f'{group}平均水平')
        
        # Add custom legends
        ax.legend(custom_lines, labels, loc='upper right')
        
        # Move title below the subplot
        ax.set_title(f'{prefixes[idx]} {group}', y=-0.2)
        
        ax.set_xticks(range(len(namelist)))
        ax.set_xticklabels(namelist)
        ax.grid(color='grey', linestyle='--', linewidth=0.5)
        ax.set_xlabel('过程得分')
        ax.set_ylabel('得分值')
    
    # plt.tight_layout()
    plt.savefig(f'./figures/{savename}_{dimension_name}_平行坐标图.png', bbox_inches='tight')
    plt.close()



def parallel_coordinate_plot_total(data,groupname):
    group_means = data.groupby(groupname)[list(data.columns.values)[2:10]].mean().reset_index()
    group_means['城市名'] = '组均值'

    # 将组均值与原始数据合并
    plot_data = pd.concat([data, group_means], ignore_index=True)

    # 定义颜色调色板
    # palette = sns.color_palette("husl", n_colors=data[groupname].nunique())
    palette=universal_colors
    # 画布设置
    fig, ax = plt.subplots(figsize=(20, 10))
    if groupname=='分组':
        labels=['超大及特大城市','大城市','中等城市','小城市']

        sorted_groups=labels
        postfix=''
        savename='规模分组'
    else:
        labels = ['第四梯队', '第三梯队', '第二梯队', '第一梯队']
        postfix='城市'
        sorted_groups=labels[::-1]
        savename='得分分组'
    # 为每个组别绘制线条
    for idx, group in enumerate(sorted_groups):
        group_data = plot_data[plot_data[groupname] == group]
        group_color = palette[idx]
        # 为每个城市绘制线条，使用更高的透明度
        for index, city_data in enumerate(group_data.iterrows()):
            _, city_data = city_data
            if city_data['城市名'] != '组均值':
                plt.plot(city_data[list(data.columns.values)[2:10]], color=group_color, alpha=0.2)# 
        
        label= group
        
        # 为组均值绘制线条，使用更粗的线条
        mean_data = group_data[group_data['城市名'] == '组均值']
        plt.plot(mean_data[list(data.columns.values)[2:10]].values[0], color=group_color, linewidth=4)
    custom_lines = []
    labels = []
    for idx, group in enumerate(sorted_groups):
        custom_line = mlines.Line2D([], [], color=palette[idx], linewidth=1, alpha=0.8)
        custom_lines.append(custom_line)
        labels.append(f'{group}'+postfix)

        custom_line_mean = mlines.Line2D([], [], color=palette[idx], linewidth=4, label=f'{group}平均水平')
        custom_lines.append(custom_line_mean)
        labels.append(f'{group}平均水平')

    # 创建自定义图例
    plt.legend(custom_lines, labels, loc='upper left', bbox_to_anchor=(0.05, 1), ncol=len(sorted_groups),framealpha=0.5, fontsize=18)

    # plt.title('各维度得分情况')
    plt.xlabel('维度得分')
    plt.ylabel('分数')
    plt.grid()
    plt.xticks(ticks=range(len(list(data.columns.values)[2:10])), labels=list(data.columns.values)[2:10])
    # plt.legend(loc='upper left', bbox_to_anchor=(0.05, 1),ncol=len(sorted_groups), framealpha=0.5,fontsize=18)
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust the padding       
    plt.savefig(f'./figures/{savename}_八维度_平行坐标图.png',bbox_inches='tight')  # 保存图像到指定路径
    # plt.show()
    plt.close()


def scatter_plot_with_regression_lines(data, dimension_name):
    newdata=data.copy()
    hist_color = 'g'
    normal_curve_color = 'b'  # 正态曲线的颜色
    fig = plt.figure(figsize=(15, 15))
    grid = plt.GridSpec(4, 4, hspace=0.5, wspace=0.5)
    main_ax = fig.add_subplot(grid[1:-1, :-1])
    newdata['组别']=newdata['分组'].apply(lambda x: str(x))
    # 定义颜色映射
    hue_order = newdata['组别'].unique()
    # palette = sns.color_palette("husl", n_colors=len(hue_order))
    palette=universal_colors

    color_mapping = {group: color for group, color in zip(hue_order, palette)}

    # 先对每个组别拟合线性回归线，并使用与组别相同的颜色，并设置为实线
    for group, color in color_mapping.items():
        group_data = newdata[newdata['组别'] == group]
        slope, intercept, _, _, _ = linregress(group_data[dimension_name], group_data['score'])
        main_ax.plot(group_data[dimension_name], intercept + slope * group_data[dimension_name], color=color, linewidth=1)

    # 再绘制散点图
    cur_ax=sns.scatterplot(data=newdata, x=dimension_name, y="score", hue="组别", palette=color_mapping, ax=main_ax)
    main_ax.set_title(dimension_name+'得分与总分的关系分析')
    main_ax.set_ylabel('总分')
    main_ax.set_xlabel(dimension_name+'得分')


    main_ax.grid(True, linestyle='--')

    # 右侧的直方图
    right_hist_ax = fig.add_subplot(grid[1:-1, -1], xticklabels=[], sharey=main_ax)
    right_hist, right_bins = np.histogram(newdata["score"], bins=15, density=True)
    right_hist_ax.barh(right_bins[:-1], right_hist, height=np.diff(right_bins), color=hist_color, edgecolor='black', alpha=0.7)
    right_hist_ax.grid(True, linestyle='--')

    # 添加右侧直方图的正态分布拟合曲线
    mu, std = np.mean(newdata["score"]), np.std(newdata["score"])
    ymin, ymax = right_hist_ax.get_ylim()
    y = np.linspace(ymin, ymax, 100)
    p = norm.pdf(y, mu, std)
    right_hist_ax.plot(p * max(right_hist) / max(p), y, normal_curve_color, linewidth=2)
    right_hist_ax.text(0.1 * max(right_hist), ymax *0.8, f"μ={mu:.2f}\nσ={std:.2f}", color=normal_curve_color)

    # 上方的直方图
    top_hist_ax = fig.add_subplot(grid[0, :-1], yticklabels=[], sharex=main_ax)
    top_hist, top_bins = np.histogram(newdata[dimension_name], bins=15, density=True)
    top_hist_ax.bar(top_bins[:-1], top_hist, width=np.diff(top_bins), color=hist_color, edgecolor='black', alpha=0.7)
    top_hist_ax.grid(True, linestyle='--')

    # 添加上方直方图的正态分布拟合曲线
    mu, std = np.mean(newdata[dimension_name]), np.std(newdata[dimension_name])
    xmin, xmax = top_hist_ax.get_xlim()
    x = np.linspace(xmin, xmax, 100)
    p = norm.pdf(x, mu, std)
    top_hist_ax.plot(x, p * max(top_hist) / max(p), normal_curve_color, linewidth=2)
    top_hist_ax.text(mu * 1.2, 0.65 * max(top_hist), f"μ={mu:.0f}\nσ={std:.1f}", color=normal_curve_color)
    # print(dimension_name+' 均值:{},方差:{}'.format(mu, std))

    # 保存图像到指定路径
    # plt.savefig('./figures/' + str(dimension_name) + '_散点图.png',bbox_inches='tight')
    plt.close()  
    del newdata
    return mu, std


def match_city_data_final(shapefile_gdf, data_df, merge_cities=['重庆市']):
    """
    Match city data from a shapefile and an Excel file based on city names.
    First matches based on 'ct_name' and then 'pr_name' for unmatched cities.
    Optionally merges specific city regions into a single region.
    
    Parameters:
    - shapefile_path: str, path to the shapefile containing city geometries
    - excel_path: str, path to the Excel file containing city attributes
    - merge_cities: list of str, names of cities to be merged (default is None)
    
    Returns:
    - GeoDataFrame containing matched city data
    """
    # Load shapefile into a GeoDataFrame
    # shapefile_gdf = gpd.read_file(shapefile_path)
    
    # Load Excel file into a DataFrame
    excel_df = data_df
    
    # First match data based on 'ct_name'
    matched_gdf_ct = pd.merge(shapefile_gdf, excel_df, how='inner', left_on='地名', right_on='城市名')
    
    # Find the unmatched cities from excel_df
    unmatched_cities = excel_df.loc[~excel_df['城市名'].isin(matched_gdf_ct['地名'])]
    
    # Then match the unmatched cities based on 'pr_name'
    matched_gdf_pr = pd.merge(shapefile_gdf, unmatched_cities, how='inner', left_on='省级', right_on='城市名')
    
    # Concatenate the two matched GeoDataFrames to include all matched cities
    matched_gdf = pd.concat([matched_gdf_ct, matched_gdf_pr]).drop_duplicates().reset_index(drop=True)
    
    # Optionally merge specific city regions
    if merge_cities:
        for city in merge_cities:
            # Merge the geometries into a single region
            merged_city = matched_gdf[matched_gdf['城市名'] == city].dissolve(by='城市名')
            
            # Remove the separate entries
            matched_gdf = matched_gdf[matched_gdf['城市名'] != city]
            
            # Append the merged city entry to the GeoDataFrame
            matched_gdf = pd.concat([matched_gdf, merged_city]).reset_index(drop=True)
    
    return matched_gdf

def add_north(ax, labelsize=18, loc_x=0.1, loc_y=0.9, width=0.04, height=0.1, pad=0.14):
    """
    画一个比例尺带'N'文字注释
    主要参数如下
    :param ax: 要画的坐标区域 Axes实例 plt.gca()获取即可
    :param labelsize: 显示'N'文字的大小
    :param loc_x: 以文字下部为中心的占整个ax横向比例
    :param loc_y: 以文字下部为中心的占整个ax纵向比例
    :param width: 指南针占ax比例宽度
    :param height: 指南针占ax比例高度
    :param pad: 文字符号占ax比例间隙
    :return: None
    """
    minx, maxx = ax.get_xlim()
    miny, maxy = ax.get_ylim()
    ylen = maxy - miny
    xlen = maxx - minx
    left = [minx + xlen*(loc_x - width*.5), miny + ylen*(loc_y - pad)]
    right = [minx + xlen*(loc_x + width*.5), miny + ylen*(loc_y - pad)]
    top = [minx + xlen*loc_x, miny + ylen*(loc_y - pad + height)]
    center = [minx + xlen*loc_x, left[1] + (top[1] - left[1])*.4]
    triangle = mpatches.Polygon([left, top, right, center], color='k')
    ax.text(s='N',
            x=minx + xlen*loc_x,
            y=miny + ylen*(loc_y - pad + height),
            fontsize=labelsize,
            horizontalalignment='center',
            verticalalignment='bottom')
    ax.add_patch(triangle)

def custom_format_scale(value, unit):
    return f"{int(value / 1e3)} km"

def gpd_scoreheatmap(shapefile_gdf, matched_gdf, cmap='BuGn', column='score', title='得分热力图'):
    """
    Visualize the matched city data on a map with colors based on scores,
    including the nine-dash line (ten-dash line) and a north arrow.
    
    Parameters:
    - shapefile_gdf: GeoDataFrame, original shapefile data
    - matched_gdf: GeoDataFrame, matched city data with 'score' column
    - cmap: str, matplotlib colormap name
    - column: str, the column name in matched_gdf to visualize
    - title: str, the title of the map
    
    Returns:
    - Matplotlib plot
    """
    # Initialize the figure and axis for the plot
    fig, ax = plt.subplots(1, figsize=(15, 15))

    # Hide grid lines and axes
    ax.grid(False)
    ax.set_axis_off()

    # Plot all cities with white fill and black outline
    shapefile_gdf.plot(ax=ax, color='white', edgecolor='black', linewidth=1)

    # Plot matched_gdf with color based on score
    matched_gdf.plot(ax=ax, column=column, cmap=cmap, edgecolor='darkgrey', linewidth=0.5, legend=True)

    # Plot the ten-dash line
    tendashline = gpd.read_file("china-geospatial-data-GB2312/ten-dash-line.gmt")
    tendashline = tendashline.to_crs(epsg=4545)
    # tendashline.plot(ax=ax, color='black')
 #-----------添加指北针------------
    ax = plt.gca()
    add_north(ax, labelsize=18, loc_x=0.08, loc_y=0.98, width=0.04, height=0.1, pad=0.10)
    # 设置比例尺
    # 1 地图单位（这里是 cm）对应 10,000,000 地图单位（即 10 km，因为 10 km = 10,000,000 cm）

    scalebar = ScaleBar(1, units='m', fixed_value=1e6, fixed_units='m', scale_loc='bottom', location='lower left', scale_formatter=custom_format_scale)

    ax.add_artist(scalebar) 

    # plt.title(title, fontsize=20)
    plt.savefig('./figures/得分热力图.png', bbox_inches='tight')  # 保存图像到指定路径
    # plt.close()
    # plt.show()

def gpd_scoremap(cur_name,shapefile_gdf, matched_gdf, group_col, group_order=None):
    """
    Visualize the matched city data on a map with ordered group coloring.
    
    Parameters:
    - shapefile_gdf: GeoDataFrame, original shapefile data
    - matched_gdf: GeoDataFrame, matched city data
    - colors_list: list, sequence of colors for each group
    - group_col: str, the column name to be used for grouping in the matched_gdf
    - group_order: list or None, sequence of group names in the order they should be colored (default is None)
    
    Returns:
    - Matplotlib plot
    """
    # Initialize the figure and axis for the plot
    fig, ax = plt.subplots(1, figsize=(15, 15))
    if cur_name=='总分':
        titlename='城市总得分分布'
    else:
        titlename=cur_name+'维度城市得分分布'
    # Hide grid lines and axes
    ax.grid(False)
    ax.set_axis_off()
    colors_list=universal_colors
    # Plot all cities with white fill and black outline
    shapefile_gdf.plot(ax=ax, color='white', edgecolor='grey')
    tendashline = gpd.read_file("china-geospatial-data-GB2312/ten-dash-line.gmt")
    tendashline = tendashline.to_crs(epsg=4545)

    # tendashline.plot(ax=ax,color='black')

    # Determine the order of groups
    if group_order:
        ordered_groups = group_order
    else:
        ordered_groups = matched_gdf[group_col].dropna().unique()
    
    # Create a colors_dict from the ordered list of groups and provided colors
    colors_dict = dict(zip(ordered_groups, colors_list))
    
    # Plot matched cities with colors based on their groups
    for group, color in colors_dict.items():
        matched_gdf[matched_gdf[group_col] == group].plot(ax=ax, color=color,edgecolor='grey',linewidth=0.5)
    
    # Create custom legend without title
    legend_labels = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=17) for color in colors_dict.values()]
    ax.legend(legend_labels, ['Tier A', 'Tier B', 'Tier C', 'Tier D'], loc='center left', bbox_to_anchor=(-0.005, 0.13),fontsize=18,title='Legend', title_fontsize=20)


    ###
    ## 调用
    #-----------添加指北针------------
    ax = plt.gca()
    add_north(ax, labelsize=18, loc_x=0.08, loc_y=0.98, width=0.04, height=0.1, pad=0.10)
    # 设置比例尺
    # 1 地图单位（这里是 cm）对应 10,000,000 地图单位（即 10 km，因为 10 km = 10,000,000 cm）

    scalebar = ScaleBar(1, units='m', fixed_value=1e6, fixed_units='m', scale_loc='bottom', location='lower left', scale_formatter=custom_format_scale)

    ax.add_artist(scalebar) 
    # plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust the padding       
    plt.savefig(f'./figures/{titlename}.png',bbox_inches='tight')  # 保存图像到指定路径
    plt.close()
    # plt.show()
    
def score_map(df,cur_name):
    # 获取4个 'husl' 调色板颜色
    # colors = sns.husl_palette(4).as_hex()
    colors=universal_colors


    data=df.copy()
    mapdict={'第一梯队':1, '第二梯队':2, '第三梯队':3, '第四梯队':4}
    data['得分分组']=data['得分分组'].map(mapdict)
    data = data[['城市名', '得分分组']]
    # 将数据转换为列表形式
    data_list = [tuple(x) for x in data.values]
    if cur_name=='总分':
        titlename='城市总得分分布'
    else:
        titlename=cur_name+'维度城市得分分布'
    # 创建地图对象
    map_chart = (
        Map(init_opts=opts.InitOpts(width="800px", height="600px"))  # 调整画布大小
        .add("梯队", data_list, "china-cities")
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title='',
                pos_left="45%",  # 左侧位置
                pos_top="5%"  # 顶部位置
            ),
            visualmap_opts=opts.VisualMapOpts(
                max_=data['得分分组'].max(),
                min_=data['得分分组'].min(),
                # is_calculable=True,  # 允许用户通过滑动手柄来选择范围
                pos_left="80%",  # 左侧位置
                pos_top="10%",  # 顶部位置
                # range_text=["高", "低"],  # 文字描述
                is_piecewise=True,  # 添加这一行
                is_inverse=True,  # 添加这一行以反转图例顺序

                range_text=[],  # 空列表，移除“高”和“低”
                pieces=[
                    {"min": 4, "max": 4, "label": "第四梯队", "color": colors[3]},  # 改变顺序
                    {"min": 3, "max": 3, "label": "第三梯队", "color": colors[2]},
                    {"min": 2, "max": 2, "label": "第二梯队", "color": colors[1]},
                    {"min": 1, "max": 1, "label": "第一梯队", "color": colors[0]}
                ]

            ),

            legend_opts=opts.LegendOpts(is_show=False)  # 关闭图例显示
        )
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            itemstyle_opts=opts.ItemStyleOpts(color="transparent")  # 使点透明
        )
    )


    map_chart.render('./figures/'+titlename+'.html')
    # driver = webdriver.Chrome(executable_path='../chromedriver.exe')

    # make_snapshot(snapshot, './figures/'+titlename+'.html', './figures/'+titlename+'.png')

def plot_radar_chart_single_group_combine(data, groupname):
    dimensions = ['能源', '经济', '效率', '居民', '水域', '森林', '绿地', '技术']
    group_means = data.groupby(groupname)[dimensions].mean().reset_index()

    if groupname == '分组':
        labels = ['超大及特大城市', '大城市', '中等城市', '小城市']
        prefix = '规模'
        sorted_groups = labels
    else:
        labels = ['第四梯队', '第三梯队', '第二梯队', '第一梯队']
        prefix = ''
        sorted_groups = labels[::-1]

    fig, axs = plt.subplots(2, 2, figsize=(20, 20), subplot_kw=dict(polar=True))
    axs = axs.flatten()  # Flatten the 2x2 grid to 1D array for easy iteration
    plt.subplots_adjust(wspace=0.8, hspace=0.8)

    # Assuming universal_colors and font_size are predefined
    palette = universal_colors
    prefixes=['(a)','(b)','(c)','(d)']
    for idx, (ax, group) in enumerate(zip(axs, sorted_groups)):
        num_vars = len(dimensions)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]

        group_data = data[data[groupname] == group]
        if groupname == '分组':
            group_color='black'
        else:
            group_color = palette[idx]

        for _, city_data in group_data.iterrows():
            values = city_data[dimensions].values.flatten().tolist()
            values += values[:1]
            ax.plot(angles, values, color=group_color, alpha=0.2, linewidth=0.8)

        mean_values = group_means[group_means[groupname] == group][dimensions].values.flatten().tolist()
        mean_values += mean_values[:1]
        ax.plot(angles, mean_values, color=group_color, linewidth=3, linestyle='solid')

        custom_lines = [mlines.Line2D([], [], color=group_color, linewidth=1, alpha=0.8),
                        mlines.Line2D([], [], color=group_color, linewidth=4)]
        ax.legend(custom_lines, [f'{group}', f'{group}平均水平'], loc='upper left', bbox_to_anchor=(0.75, 1.1),
                  framealpha=0.5, fontsize=18)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(dimensions, fontsize=font_size)
        ax.set_yticks(np.arange(0, 101, 20))
        ax.set_yticklabels(np.arange(0, 101, 20), fontsize=font_size)
        ax.set_title(f'{prefixes[idx]} {group}',y=-0.2)
    plt.savefig('./figures/组合_' + prefix + groupname + '_雷达图.png', bbox_inches='tight')
    plt.close()

def plot_radar_chart_single_group(data,groupname,citydict):
    # 选择所有除城市名、分组和得分之外的列作为维度
    dimensions = ['能源', '经济', '效率','居民', '水域', '森林', '绿地', '技术']
    # 计算每个分组的均值
    group_means = data.groupby(groupname)[dimensions].mean().reset_index()
    if groupname=='分组':
        labels=['超大及特大城市','大城市','中等城市','小城市']
        prefix='规模'
        sorted_groups=labels
    else:
        labels = ['第四梯队', '第三梯队', '第二梯队', '第一梯队']
        prefix=''
        sorted_groups=labels[::-1]
    # 为每个分组绘制数据
    for idx, group in enumerate(sorted_groups):
            # 计算每个轴的角度
        num_vars = len(dimensions)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]
        # 设置图形和轴
        fig, ax = plt.subplots(figsize=(15, 15), subplot_kw=dict(polar=True))
        # 定义颜色调色板
        # palette = sns.color_palette("husl", n_colors=data[groupname].nunique())
        palette=universal_colors

        group_data = data[data[groupname] == group]
        if groupname=='分组':
            group_color='black'
        else:
            group_color = palette[idx]
        
        # 为组内的每个城市绘制较浅、更透明的线
        for _, city_data in group_data.iterrows():
            values = city_data[dimensions].values.flatten().tolist()
            values += values[:1]
            ax.plot(angles, values, color=group_color, alpha=0.2, linewidth=0.8)
        
        # 为组均值绘制较粗、更不透明的线
        mean_values = group_means[group_means[groupname] == group][dimensions].values.flatten().tolist()
        mean_values += mean_values[:1]
        ax.plot(angles, mean_values, color=group_color, linewidth=3, linestyle='solid',label=group)  
                #添加每个维度的标签
        
        custom_lines = []
        labels = []
        # for idx, group in enumerate(sorted(data[groupname].unique())):
        custom_line = mlines.Line2D([], [], color=group_color, linewidth=1, alpha=0.8)
        custom_lines.append(custom_line)
        labels.append(f'{group}')

        custom_line_mean = mlines.Line2D([], [], color=group_color, linewidth=4, label=f'{group}平均水平')
        custom_lines.append(custom_line_mean)
        labels.append(f'{group}平均水平')
        # 创建自定义图例
        plt.legend(custom_lines, labels, loc='upper left', bbox_to_anchor=(0.35, 1.2), ncol=1,framealpha=0.5, fontsize=font_size)

        plt.xticks(angles[:-1], dimensions,fontsize=font_size)
        plt.yticks(np.arange(0, 101, 20), fontsize=font_size)
        plt.grid(True, linestyle='--', linewidth=0.5)
        # plt.legend(loc='upper left', bbox_to_anchor=(1.0, 1.1))
        # plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust the padding            
        plt.savefig('./figures/单组别_'+prefix+groupname+'_'+f'{group}'+'_雷达图.png',bbox_inches='tight')  # 保存图像到指定路径
        plt.close()
       
        citylist=citydict[group]
        for idx, city in enumerate(citylist):
            # 设置图形和轴
            fig, ax = plt.subplots(figsize=(15, 15), subplot_kw=dict(polar=True))
            labelname=group+':\n'+city
            # 定义颜色调色板
            palette = sns.color_palette("Set2", n_colors=len(citylist))
            group_data = data[data['城市名'] == city]
            group_color = 'black'
            values = group_data[dimensions].values.flatten().tolist()
            values += values[:1]
            ax.plot(angles, values, color=group_color, alpha=1, linewidth=3,linestyle='solid',label=labelname)
            # ax.fill(angles, values, color=group_color, alpha=0.25)  # 增加填充
            ax.scatter(angles, values, color=group_color, s=100)  # 增加点，注意这里用的是 color
            #添加每个维度的标签
            plt.xticks(angles[:-1], dimensions,fontsize=font_size)
            plt.yticks(np.arange(0, 101, 20), fontsize=font_size)
            plt.grid(True, linestyle='--', linewidth=0.5)
            plt.legend(loc='upper left', bbox_to_anchor=(0.35, 1.2))
            # plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust the padding           
            plt.savefig('./figures/单城市_'+groupname+'_'+f'{city}'+'_雷达图.png',bbox_inches='tight')  # 保存图像到指定路径
            plt.close()

def plot_radar_chart(data,radar_name):

    
    # 选择所有除城市名、分组和得分之外的列作为维度
    dimensions = [col for col in data.columns if col not in ['城市名', '分组', 'score']]
    
    # 计算每个分组的均值
    group_means = data.groupby('分组')[dimensions].mean().reset_index()

    # 计算每个轴的角度
    num_vars = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    # 设置图形和轴
    fig, ax = plt.subplots(figsize=(15, 15), subplot_kw=dict(polar=True))
    # if radar_name=='各维度':
    #     plt.title('各城市及组均值在各维度的表现', y=1.1,fontsize=title_fontsize)
    # else:
    #     plt.title('各城市及组均值在'+radar_name+'维度各环节的表现', y=1.1,fontsize=title_fontsize)
    # 定义颜色调色板
    # palette = sns.color_palette("husl", n_colors=data['分组'].nunique())
    palette=universal_colors

    labels=['超大及特大城市','大城市','中等城市','小城市']

    # 为每个分组绘制数据
    for idx, group in enumerate(labels):
        group_data = data[data['分组'] == group]
        group_color = palette[idx]
        # 为组内的每个城市绘制较浅、更透明的线
        for _, city_data in group_data.iterrows():
            values = city_data[dimensions].values.flatten().tolist()
            values += values[:1]
            ax.plot(angles, values, color=group_color, alpha=0.2, linewidth=0.8)
        # 为组均值绘制较粗、更不透明的线
        mean_values = group_means[group_means['分组'] == group][dimensions].values.flatten().tolist()
        mean_values += mean_values[:1]

        ax.plot(angles, mean_values, color=group_color, linewidth=3, linestyle='solid',label=group)

    custom_lines = []
    labels = []
    for idx, group in enumerate(['超大及特大城市','大城市','中等城市','小城市']):
        custom_line = mlines.Line2D([], [], color=palette[idx], linewidth=1, alpha=0.8)
        custom_lines.append(custom_line)
        labels.append(f'{group}')

        custom_line_mean = mlines.Line2D([], [], color=palette[idx], linewidth=4)
        custom_lines.append(custom_line_mean)
        labels.append(f'{group}平均水平')
    # 创建自定义图例
    plt.legend(custom_lines, labels, loc='upper left', bbox_to_anchor=(-0.2, 1.2), ncol=4,framealpha=0.5, fontsize=20)

    #添加每个维度的标签
    plt.xticks(angles[:-1], dimensions,fontsize=font_size)
    # ax.set_thetagrids(np.degrees(angles[:-1]), dimensions, fontsize=font_size, y=1.05)

    plt.yticks(np.arange(0, 101, 20), fontsize=font_size)
    plt.grid(True, linestyle='--', linewidth=0.5)
    # plt.legend(loc='upper left', bbox_to_anchor=(1, 1.1))
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust the padding

    plt.savefig('./figures/'+radar_name+'_雷达图.png',bbox_inches='tight')  # 保存图像到指定路径
    plt.close()

def analyze_city_groups_with_intervals(data, dimensionname):
    max_score = data['score'].max()
    min_score = data['score'].min()
    range_score = max_score - min_score
    interval = range_score / 4
    bins = [min_score + i * interval for i in range(5)]
    labels = ['第一梯队', '第二梯队', '第三梯队', '第四梯队']
    data['得分分组'] = pd.cut(data['score'], bins=bins, labels=labels[::-1], include_lowest=True)

    labels2 = ['超大及特大城市', '大城市', '中等城市', '小城市']
    grouped_data = data.groupby(['得分分组', '分组']).size().reset_index(name='城市数')

    plt.figure(figsize=(15, 10))
    ax = sns.barplot(x='得分分组', y='城市数', hue='分组', data=grouped_data, 
                        palette=universal_colors, dodge=True, 
                        order=labels, hue_order=labels2, saturation=0.8)
    plt.legend(loc='upper left', bbox_to_anchor=(0.1, 1.1), ncol=4, framealpha=0.5, fontsize=18)
    ax.set_yticklabels([])
    ax.set_xlabel('')
    ax.set_yticks([])
    ax.set_ylabel('')
    
    for container in ax.containers:
        for bar in container.patches:
            bar.set_width(0.15)
            
    for p in ax.patches:
        ax.annotate(f'{int(p.get_height())}', 
                    (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='baseline', fontsize=18)

    # plt.savefig(f'./figures/{dimensionname}_规模与得分分组直方图.png', bbox_inches='tight')
    plt.close()

    score_intervals = {}
    for i in range(len(labels)):
       
        min_score = "{:.2f}".format(bins[i])
        max_score = "{:.2f}".format(bins[i + 1])
        score_intervals[labels[len(labels)-i-1]] = f"[{min_score}, {max_score})"

    score_intervals = {label: score_intervals[label] for label in labels}

    return data, score_intervals####第四梯队到第一梯队要反过来

# Integrating the adjust_percentages function into the current version of create_pie_charts function

def adjust_percentages(percentages):
    rounded_percentages = [round(p) for p in percentages]
    error = 100 - sum(rounded_percentages)
    
    for i in range(abs(error)):
        idx = i % len(percentages)
        if error > 0:
            rounded_percentages[idx] += 1
        else:
            rounded_percentages[idx] -= 1

    return rounded_percentages
def create_pie_charts(data, dimension_name, mode='梯队', single_figure=True):
    # plt.rcParams['font.size'] = 18
    label_translations = {
        '第一梯队': 'Tier A',
        '第二梯队': 'Tier B',
        '第三梯队': 'Tier C',
        '第四梯队': 'Tier D',
        '超大及特大城市': 'Mega city(Ⅰ)',
        '大城市': 'Large city(Ⅱ)',
        '中等城市': 'Medium city(Ⅲ)',
        '小城市': 'Small city(Ⅳ)'
    }
    grouped_data = data.groupby(['得分分组', '分组']).size().reset_index(name='城市数')
    pivot_data = pd.pivot_table(grouped_data, values='城市数', index=['分组'], columns=['得分分组'], fill_value=0)
    
    column_order = ['第一梯队', '第二梯队', '第三梯队', '第四梯队']
    row_order = ['超大及特大城市', '大城市', '中等城市', '小城市']
    pivot_data = pivot_data.reindex(columns=column_order, index=row_order)
    
    fixed_colors = universal_colors
    
    if mode == '梯队':
        iterate_over = column_order
        guimocolors=['#7B87FF','#79ADED','#B1C5FD','#D7E3F2']
        # Adjust transparency by converting Hex to RGBA with alpha (transparency)
        colors_with_alpha = [(123/255, 135/255, 255/255, 0.5),  # 50% transparency
                     (121/255, 173/255, 237/255, 0.3),  # 30% transparency
                     (177/255, 197/255, 253/255, 0.4),  # 40% transparency
                     (215/255, 227/255, 242/255, 0.6)]  # 60% transparency
        color_mapping = {size: color for size, color in zip(row_order, colors_with_alpha)}
        size_mapping = {'超大及特大城市': 'Ⅰ', '大城市': 'Ⅱ', '中等城市': 'Ⅲ', '小城市': 'Ⅳ'}

    elif mode == '规模':
        iterate_over = row_order
        color_mapping = {tier: color for tier, color in zip(column_order, fixed_colors)}
        size_mapping = {'第一梯队': 'A', '第二梯队': 'B', '第三梯队': 'C', '第四梯队': 'D'}


    else:
        raise ValueError("Invalid mode. Choose either '梯队' or '规模'")
    
    if single_figure:
        fig, axs = plt.subplots(2, 2, figsize=(15, 15))
        axs = axs.flatten()
        plt.subplots_adjust(wspace=0.5, hspace=0.5)

    
    label_prefixes = ['(a) ', '(b) ', '(c) ', '(d) ']
    
    for i, item in enumerate(iterate_over):
        if not single_figure:
            plt.figure(figsize=(10, 8))
        else:
            plt.sca(axs[i])
        
        if mode == '梯队':
            non_zero_data = pivot_data.loc[:, item][pivot_data.loc[:, item] > 0]
        else:
            non_zero_data = pivot_data.loc[item, :][pivot_data.loc[item, :] > 0]
        
        sizes = non_zero_data.values
        percentages = 100 * sizes / np.sum(sizes)
        adjusted_percentages = adjust_percentages(percentages)
        labels = [f"{size_mapping[label]}:{p}%" for label, p in zip(non_zero_data.index, adjusted_percentages)]

        colors = [color_mapping.get(label, 'grey') for label in non_zero_data.index]

        if mode == '梯队':
            # Draw the outer ring with hatch patterns
            plt.pie([1], radius=1, startangle=90, colors=[fixed_colors[i]], 
                                    wedgeprops=dict(edgecolor='white', width=0.3))
            
            # Draw the inner pie chart
            wedges, texts=plt.pie(sizes, colors=colors, radius=0.7, startangle=90, 
                    labeldistance=0.5)
        else:
            wedges, texts=plt.pie(sizes, colors=colors, startangle=90, labeldistance=0.6,wedgeprops=dict(edgecolor='white'))
        
        # Compute angles for annotation
        start_angle = 90  # in degrees
        theta1s, theta2s = zip(*[(w.theta1, w.theta2) for w in wedges])
        mid_angles = [(t1 + t2) / 2 for t1, t2 in zip(theta1s, theta2s)]

        for mid_angle, label, size in zip(mid_angles, labels, sizes):

            angle_rad = np.deg2rad(mid_angle)
            if len(labels)==1:
                x=0
                y=0
                angle_rad=90
            else:
                x = 0.6 * 0.75 * np.cos(angle_rad)  # 0.5 * radius of the wedge
                y = 0.6 * 0.75 * np.sin(angle_rad)  # 0.5 * radius of the wedge
            ha = "left" if x > 0 else "right"

            plt.annotate(
                f"{label}",
                xy=(x, y),
                xycoords="data",
                xytext=(1.2 * np.cos(angle_rad), 1.2 * np.sin(angle_rad)),
                textcoords="data",
                arrowprops=dict(
                    arrowstyle="-|>",
                    connectionstyle="arc3,rad=0",
                    linestyle="-",
                    color="grey",
                    linewidth=1,       # 线宽
                    mutation_scale=20  # 箭头头部大小
                ),
                ha=ha,
                fontsize=24  # 这里设置字体大小

            )

        plt.axis('equal')
        if single_figure:
            
            axs[i].text(0, -1.45, label_prefixes[i] + label_translations[item], ha='center')
        else:
            pass
            
        if not single_figure:
            plt.savefig(f'./figures/{dimension_name}_{item}_饼图.png', bbox_inches='tight')
            plt.close()
    
    if single_figure:
        plt.savefig(f'./figures/{dimension_name}_{mode}_combined_饼图.png', bbox_inches='tight')
        plt.close()
        # plt.show()
    
    pivot_data['城市总数'] = pivot_data.sum(axis=1)

    return pivot_data




def plot_cloud_rain_ptitprince(data, value_column, group_column, prefix=''):
    sns.set(rc={'font.family':'Arial Unicode MS', 'font.sans-serif':['Arial Unicode MS']}, style="whitegrid", font_scale=3)  # 设置风格，包括网格线
    
    # Sort the unique values in the group column for ordered plotting
    if group_column == '得分分组':
        labels = ['第四梯队', '第三梯队', '第二梯队', '第一梯队']
        sorted_groups = labels[::-1]
        groupname = '得分分组'
        palette2=universal_colors
    else:
        sorted_groups = ['超大及特大城市','大城市','中等城市','小城市']
        groupname = '规模分组'
        palette2= [
                        "#7B87FF",  # 50% transparency
                        "#79ADED",  # 30% transparency
                        "#B1C5FD",  # 40% transparency
                        "#D7E3F2"   # 60% transparency
                    ]
        # palatte= [(123/255, 135/255, 255/255, 0.5),  # 50% transparency
                    #  (121/255, 173/255, 237/255, 0.3),  # 30% transparency
                    #  (177/255, 197/255, 253/255, 0.4),  # 40% transparency
                    #  (215/255, 227/255, 242/255, 0.6)]  # 60% transparency
    
    plt.figure(figsize=(15, 15))
    
    # Create the RainCloud plot using ptitprince
    ax = pt.RainCloud(x=group_column, y=value_column, data=data, order=sorted_groups, width_viol=0.7, width_box=0.2, orient='v', palette=palette2,point_size=4)
    for child in ax.get_children():
        if isinstance(child, PathCollection):  # Check if the child is a scatter plot
            child.set_alpha(0.5)  # Adjust the alpha value for scatter plot
    # Enable y-axis grid lines
    ax.yaxis.grid(True)

    # Annotate the number of observations in each group
    group_counts = data[group_column].value_counts()
    for i, group in enumerate(sorted_groups):
        count = group_counts.get(group, 0)  # Use 0 if the group is not found
        ax.text(i, ax.get_ylim()[0], f'n={count}', ha='center', va='bottom', color='black')

    # plt.title(prefix + f"按{groupname}的得分对比")
    plt.xlabel('')
    plt.ylabel('Score')
    
    if group_column == '分组':
        plt.xticks(range(4), ['Mega City','Large City','Medium City','Small City'])  # 设置刻度位置和标签
    else:
        plt.xticks(range(4), ['Tier D', 'Tier C', 'Tier B', 'Tier A'][::-1])
    plt.savefig(f'./figures/{prefix}_{group_column}_{value_column}_云雨图.png',bbox_inches='tight')
    plt.close()


# Define a function to format the score and rank for each city in each dimension
def format_score_and_rank(df, dimensions, top_header="维度（得分|排名)"):
    # 创建一个仅包含 '城市名' 的空 DataFrame
    df_modified = df[['城市名']].copy()
    
    for dimension in dimensions:
        # 先进行排序和排名
        # rank_column = df[dimension].rank(ascending=False).astype(int)
        rank_column = df[dimension].rank(method='min', ascending=False).astype(int)

        # 格式化为两位小数
        score_column = df[dimension].apply(lambda x: "{:.2f}".format(x))
        
        # 将 dimension 和 dimension + '排名' 添加到 df_modified 中
        df_modified[dimension] = score_column
        df_modified[dimension + '排名'] = rank_column
    
    return df_modified



def plot_single_distribution(df, column, label, save_filename, fit_method='kde'):
    fig, ax = plt.subplots(figsize=(10, 8))
    # plt.subplots_adjust(wspace=0.8, hspace=0.8)
    y_min_global = float('inf')  # 初始化为正无穷
    y_max_global = -float('inf')  # 初始化为负无穷

    data = df[column]
    ax.hist(data, bins=10, density=True, alpha=0.6, color='skyblue', edgecolor='black')
    
    # Remove y-axis ticks
    ax.set_yticks([])  # <--- This line removes the y-axis ticks
    
    # 使用实际数据的最大最小值
    xmin, xmax = data.min(), data.max()
    x = np.linspace(xmin, xmax, 100)
    
    peak_x = None  # Initialize variable to store x value of the peak
    
    if fit_method == 'normal':
        mu, std = norm.fit(data)
        p = norm.pdf(x, mu, std)
        ax.plot(x, p, 'k', linewidth=2)
        peak_x = mu  # For normal distribution, peak is at the mean (mu)
    
    elif fit_method == 'kde':
        kde = gaussian_kde(data)
        p = kde.evaluate(x)
        ax.plot(x, p, 'k', linewidth=2)
        peak_x = x[np.argmax(p)]  # Find the x value where the PDF is maximum
    
    # 在x轴上标注出最大最小值和峰值
    x_ticks = [xmin, xmax]
    # if peak_x is not None:
    #     x_ticks.append(peak_x)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([str(int(val)) if val.is_integer() else f"{val:.2f}" for val in x_ticks])
    y_min, y_max = ax.get_ylim()
    y_max_global = max(y_max, y_max_global)   
    ax.set_ylim([0, 1.1*y_max_global])
    ax.set_xlim([10, 90])
    fig.text(0.85, 0.01, 'Score', ha='center', va='center')
    fig.text(0.07, 0.75, 'Frequency', ha='center', va='center', rotation='vertical')
    
    # plt.tight_layout()
    plt.savefig(f'./figures/{save_filename}_分布图.png', bbox_inches='tight')
    plt.close()

    return fig



def plot_distribution(df, columns, labels, save_filename, fit_method='kde'):
    n = len(columns)
    n_cols = 2
    n_rows = int(np.ceil(n / n_cols))
    y_min_global = float('inf')  # 初始化为正无穷
    y_max_global = -float('inf')  # 初始化为负无穷

    fig, axs = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
    axs = axs.flatten()
    plt.subplots_adjust(wspace=0.3, hspace=0.8)

    for i in range(n, n_rows * n_cols):
        axs[i].axis('off')
    
    for i, col in enumerate(columns):

        ax = axs[i]
        data = df[col]
        ax.hist(data, bins=10, density=True, alpha=0.6, color='skyblue', edgecolor='black')
        
        # Remove y-axis ticks
        ax.set_yticks([])
        
        # 使用实际数据的最大最小值
        xmin, xmax = data.min(), data.max()
        # print(final_X_max)
        x = np.linspace(xmin, xmax, 100)
        peak_x = None  # Initialize variable to store x value of the peak
        
        if fit_method == 'normal':
            mu, std = norm.fit(data)
            p = norm.pdf(x, mu, std)
            ax.plot(x, p, 'k', linewidth=2)
            peak_x = mu  # For normal distribution, peak is at the mean (mu)
        
        elif fit_method == 'kde':
            kde = gaussian_kde(data)
            p = kde.evaluate(x)
            ax.plot(x, p, 'k', linewidth=2)
            peak_x = x[np.argmax(p)]  # Find the x value where the PDF is maximum
        
        # 在每个子图的x轴上都标注出最大最小值和峰值
        x_ticks = [xmin, xmax]
        # if peak_x is not None:
        #     x_ticks.append(peak_x)
        ax.set_xticks(x_ticks)
        ax.set_xticklabels([str(int(val)) if float(val).is_integer() else f"{val:.2f}" for val in x_ticks])

        ax.set_xlabel('Score')
        ax.xaxis.set_label_coords(0.85, -0.15)
        ax.set_ylabel('Frequency')

        ax.yaxis.set_label_coords(-0.05, 0.85)
        
        ax.set_title(labels[i], y=-0.5)
        y_min, y_max = ax.get_ylim()
        y_min_global = min(y_min, y_min_global)
        y_max_global = max(y_max, y_max_global)      
        # if (i % n_cols) != 0:
        #     ax.tick_params(labelleft=False)
        
    for ax in axs:
        ax.set_ylim([y_min_global, 1.1*y_max_global])
        ax.set_xlim([0, 110])

    # fig.text(0.85, 0.04, '得分值', ha='center', va='center')
    # fig.text(0.1, 0.85, '频率', ha='center', va='center', rotation='vertical')
    # plt.tight_layout()
    plt.savefig(f'./figures/{save_filename}_分布图.png', bbox_inches='tight')
    # plt.show()
    plt.close()

    return fig






#######################画城市群蛛网图用到的函数#########################################
# Define a function to read the Excel file and return a dictionary mapping citygroups to citylists
def extract_citygroup_citylist(excel_path):
    # Read the Excel file
    df = pd.read_excel(excel_path)
    
    # Initialize an empty dictionary to hold the citygroups and their corresponding citylists
    citygroup_citylist_dict = {}
    
    # Loop through each row in the DataFrame to populate the dictionary
    for index, row in df.iterrows():
        citygroup = row['城市群']
        citylist_str = row['城市名单']
        citylist = citylist_str.split('、')  # Assuming the city names are separated by '、'
        
        # No need for fuzzy matching here as we are directly using the city names from the Excel file
        citygroup_citylist_dict[citygroup] = citylist
    
    return citygroup_citylist_dict
def abbr_match(abbr_df,full_df):###传入缩写的列和完整的待匹配的列
    # 创建一个空字典来保存匹配结果
    matches = []
    unmatch=[]
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
            unmatch.append(abbreviation)
            print('{} 未匹配成功！匹配对象为{}, 匹配得分为{}!'.format(abbreviation,match,score))

    # 将结果转换为DataFrame
    matched_df = pd.DataFrame(matches,columns=['full'])
    return matched_df['full'], ','.join(unmatch)

def create_folder_if_not_exists(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

def plot_and_save_single_city(data, dimensions, angles, city, group_color, folder_name):
    fig, ax = plt.subplots(figsize=(15, 15), subplot_kw=dict(polar=True))
    city_data = data[data['城市名'] == city]
    values = city_data[dimensions].values.flatten().tolist()
    values += values[:1]
    ax.plot(angles, values, color=group_color, linewidth=3, linestyle='solid')
    ax.scatter(angles, values, color=group_color, s=50)
    plt.xticks(angles[:-1], dimensions)
    plt.yticks(np.arange(0, 101, 20))
    plt.grid(True, linestyle='--', linewidth=0.5)
    plt.legend([city], loc='upper left', bbox_to_anchor=(0.4, 1.15))
    plt.tight_layout()
    plt.savefig(f"{folder_name}/{city}.png", bbox_inches='tight')
    plt.close()

def plot_citygroup_radar_chart(data, citygroup, citylist,group_color):
    dimensions = ['能源', '经济', '效率','居民', '水域', '森林', '绿地', '技术']
    num_vars = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    
    folder_name = f"./城市群/{citygroup}"
    create_folder_if_not_exists(folder_name)
    
    # palette = sns.color_palette("Set2", n_colors=len(citylist))
    
    for idx, city in enumerate(citylist):
        if city in data['城市名'].values:
            # group_color = palette[idx]
            plot_and_save_single_city(data, dimensions, angles, city, group_color, folder_name)

def plot_all_cities_in_one_figure(data, citygroup, citylist, group_color):
    data = data.sort_values(by='score', ascending=False)
    dimensions = ['能源', '经济', '效率','居民', '水域', '森林', '绿地', '技术']
    num_vars = len(dimensions)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    valid_cities = [city for city in data['城市名'].values if city in citylist]
    num_cities = len(valid_cities)

    num_cols = 5
    num_rows = int(np.ceil((num_cities + 1) / num_cols))  # +1 for the extra plot
    
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(15, 3 * num_rows), subplot_kw=dict(polar=True))
    
    if num_rows == 1:
        axes = np.expand_dims(axes, axis=0)
    
    axes = axes.flatten()
    for idx, ax in enumerate(axes):
        if idx == 0:  # Extra plot for dimension names (Move to the first position)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(dimensions, fontsize=15)
            ax.set_yticks([])
            ax.set_yticklabels([])
            ax.grid(False)
        elif 0 < idx <= num_cities:  # Adjust index for city plots
            city = valid_cities[idx-1]  # Adjust index
            city_data = data[data['城市名'] == city]
            values = city_data[dimensions].values.flatten().tolist()
            values += values[:1]
            
            ax.plot(angles, values, color=group_color, linewidth=3, linestyle='solid')
            ax.fill(angles, values, color=group_color, alpha=0.2)
            ax.scatter(angles, values, color=group_color, s=50)
            
            ax.set_ylim([0, 100])
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xticklabels([])
            ax.set_yticklabels([])
            ax.grid(False)
            ax.set_title(city, y=-0.3)
        else:
            ax.axis('off')
    
    folder_name = f"./城市群/{citygroup}"
    create_folder_if_not_exists(folder_name)
    plt.tight_layout()
    plt.savefig(f"./城市群/{citygroup}/all_cities.png", bbox_inches='tight')
    plt.close()

#######################画城市群蛛网图用到的函数#########################################


######################################城市群总体分析#############################################
def plot_grouped_boxplot(group_stats, dimension, y_min=20, y_max=80):
    plt.figure(figsize=(15, 10))
    
    # Prepare data
    box_data = []
    labels = []
    for group, df in group_stats.items():
        box_data.append(df[dimension].dropna().values)  # Ensure there are no NaN values
        labels.append(group)
    
    # Create boxplot with transparent boxes
    bp = plt.boxplot(box_data, vert=True, patch_artist=True, labels=labels)
    
    for box in bp['boxes']:
        box.set_facecolor('none')  # Make box transparent
    for whisker in bp['whiskers']:
        whisker.set(linestyle='--', linewidth=0.5)
    
    # Set marker style for outliers
    for flier in bp['fliers']:
        flier.set(marker='x', color='#e7298a', alpha=0.5)

    # for median in bp['medians']:
    #     median.set(color='red', linewidth=2)
    # Add scatter plot for raw data points
    for i, data in enumerate(box_data):
        y = data
        x = np.random.normal(i + 1, 0.04, len(y))  # Add some jitter for better visualization
        plt.scatter(x, y, alpha=0.5)
    
    # Add labels and title
    plt.xticks(rotation=45)
    plt.xlabel('城市群')
    plt.ylabel(f'分值')
    
    # Set y-axis limits if specified
    if y_min is not None and y_max is not None:
        plt.ylim(y_min, y_max)
    
    # Show grid
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(f'./城市群/{dimension}_箱线图_散点.png', bbox_inches='tight')
    plt.close()

def plot_grouped_scatter_with_mean_line(group_stats, dimension, y_min=20, y_max=80):
    plt.figure(figsize=(15, 10))
    
    # Prepare data
    box_data = []
    labels = []
    means = []
    for group, df in group_stats.items():
        data_values = df[dimension].dropna().values  # Ensure there are no NaN values
        box_data.append(data_values)
        labels.append(group)
        means.append(np.mean(data_values))
    
    # Add scatter plot for raw data points
    for i, data in enumerate(box_data):
        y = data
        x = np.random.normal(i + 1, 0.04, len(y))  # Add some jitter for better visualization
        plt.scatter(x, y, alpha=0.5,s=100)
        
        # Draw bounding box
        min_val = np.min(data)
        max_val = np.max(data)
        plt.gca().add_patch(plt.Rectangle((i + 0.8, min_val), 0.4, max_val - min_val, fill=None, edgecolor='black', linewidth=1))
    
    # Add a line plot for the mean values
    plt.plot(range(1, len(means) + 1), means, marker='*', linestyle='--', color='black',markersize=10,alpha=0.8, label='均值')
    # Add labels and title
    plt.xticks(ticks=range(1, len(labels) + 1), labels=labels, rotation=45)
    plt.xlabel('城市群')
    plt.ylabel(f'分值')
    plt.legend(loc='upper left', bbox_to_anchor=(0.05, 1),ncol=4, framealpha=0.5,fontsize=18)

    # Set y-axis limits if specified
    plt.ylim(y_min, y_max)
    
    # Show grid
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(f'./城市群/{dimension}_散点_均值折线_框.png', bbox_inches='tight')
    plt.close()

# 定义函数用于绘制特定维度上的均值和标准差
def plot_mean_and_std(mean_df, std_df, dimension_name):
    plt.figure(figsize=(15, 8))

    # 获取城市群名称和对应的维度的均值和标准差
    city_group_names = mean_df['城市群']
    mean_values = mean_df[dimension_name]
    std_values = std_df[dimension_name]

    # 绘制均值折线图
    plt.plot(city_group_names, mean_values, marker='o', linestyle='-', color='g', label='均值',markersize=8)

    # 使用带状图（填充区域）表示标准差
    plt.fill_between(city_group_names, mean_values - std_values, mean_values + std_values, color='g', alpha=0.1, label='标准差范围')

    # 显式地绘制标准差的上下折线
    plt.plot(city_group_names, mean_values - std_values, marker='', linestyle='--', color='g', alpha=0.2, label='标准差下界')
    plt.plot(city_group_names, mean_values + std_values, marker='', linestyle='--', color='g', alpha=0.2, label='标准差上界')

    # 添加标签和标题
    plt.xticks(rotation=45)
    # plt.ylim(0, 100)  # 设置纵坐标范围为0-100

    plt.xlabel('城市群')
    plt.ylabel('分值')
    # plt.title(f'城市群在{dimension_name}维度上的均值和标准差')
    plt.legend(loc='upper left', bbox_to_anchor=(0.05, 1),ncol=4, framealpha=0.5,fontsize=18)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust the padding       
    plt.savefig(f'./城市群/总体_平行坐标图.png',bbox_inches='tight')  # 保存图像到指定路径
    # plt.show()
    plt.close()
######################################城市群总体分析#############################################


####################################城市群内部#######################################
def inside_citygroup_parallel_coordinates(citygroup,citygroup_data, dimensions, marker_size=8):
    # 初始化图像
    plt.figure(figsize=(20, 10))
    
    # 创建不同的标记和颜色生成器
    markers = itertools.cycle(('o', 'v', '^', '<', '>', 's', 'p', '*'))
    colors = itertools.cycle(('b', 'g', 'r', 'c', 'm', 'y', 'k', '#FFA500'))
    
    # 遍历每个维度，绘制平行坐标图
    for dimension, marker, color in zip(dimensions, markers, colors):
        plt.plot(citygroup_data['城市名'], citygroup_data[dimension], marker=marker, linestyle='-', color=color, label=dimension, markersize=marker_size)
    
    # 设置图像标签和标题
    plt.xticks(rotation=45)
    plt.ylim(0, 100)  # 设置纵坐标范围为0-100

    plt.xlabel(f'{citygroup}城市群')
    plt.ylabel('分值')
    # plt.title('城市在不同维度上的分值')
    plt.legend(loc='upper left', bbox_to_anchor=(0.05, 1),ncol=4, framealpha=0.5,fontsize=18)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    folder_name = f"./城市群/{citygroup}"
    plt.tight_layout()
    citygroup_data.to_excel(f'{folder_name}/{citygroup}城市群.xlsx', index=False)
    plt.savefig(f"{folder_name}/{citygroup}_平行坐标图.png", bbox_inches='tight')
    plt.close()
    ####################################城市群内部#######################################
def calculate_and_save_cv_to_excel(group_stats, dimension):
    cv_dict = {}
    mean_dict={}
    std_dict={}
    for group, df in group_stats.items():
        data_values = df[dimension].dropna().values
        mean_value = np.mean(data_values)
        std_value = np.std(data_values)
        
        if mean_value == 0:
            cv_value = np.nan
        else:
            cv_value = (std_value / mean_value) * 100  # Coefficient of Variation
        cv_dict[group] = cv_value
        mean_dict[group]=mean_value
        std_dict[group]=std_value
    
    cv_df = pd.DataFrame(list(cv_dict.items()), columns=['城市群', 'CV'])
    cv_df.to_excel(f'城市群/CV_{dimension}.xlsx', index=False)
    mean_df=pd.DataFrame(list(mean_dict.items()), columns=['城市群', 'Mean'])
    mean_df.to_excel(f'城市群/Mean_{dimension}.xlsx', index=False)

