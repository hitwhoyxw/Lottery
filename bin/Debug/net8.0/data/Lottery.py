# -*- coding:utf-8 -*-

import argparse
import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
fold = '/data'
parser = argparse.ArgumentParser()
parser.add_argument('--name', default="ssq", type=str, help="选择爬取数据: 双色球/大乐透")
args = parser.parse_args()


def get_url(name):
    """
    :param name: 玩法名称
    :return:
    """
    url = "https://datachart.500.com/{}/history/".format(name)
    path = "newinc/history.php?start={}&end="
    return url, path


def get_current_number(name):
    """ 获取最新一期数字
    :return: int
    """
    url, _ = get_url(name)
    r = requests.get("{}{}".format(url, "history.shtml"), verify=False)
    r.encoding = "gb2312"
    soup = BeautifulSoup(r.text, "lxml")
    current_num = soup.find("div", class_="wrap_datachart").find("input", id="end")["value"]
    return current_num


def spider(name, start, end):
    """ 爬取历史数据
    :param name 玩法
    :param start 开始一期
    :param end 最近一期
    :return:
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }
    url, path = get_url(name)
    url = "{}{}{}".format(url, path.format(start), end)
    r = requests.get(url=url,headers=headers, verify=False)
    r.encoding = "gb2312"
    soup = BeautifulSoup(r.text, "lxml")
    trs = soup.find("tbody", attrs={"id": "tdata"}).find_all("tr")
    data = []
    for tr in trs:
        item = dict()
        if name == "ssq":
            item[u"期数"] = tr.find_all("td")[0].get_text().strip()
            for i in range(6):
                item[u"红球_{}".format(i+1)] = tr.find_all("td")[i+1].get_text().strip()
            item[u"蓝球"] = tr.find_all("td")[7].get_text().strip()
            data.append(item)
        elif name == "dlt":
            item[u"期数"] = tr.find_all("td")[0].get_text().strip()
            for i in range(5):
                item[u"红球_{}".format(i+1)] = tr.find_all("td")[i+1].get_text().strip()
            for j in range(2):
                item[u"蓝球_{}".format(j+1)] = tr.find_all("td")[6+j].get_text().strip()
            data.append(item)
        else:
            print("抱歉，没有找到数据源！")

    df = pd.DataFrame(data)
    df.to_csv("{}{}.csv".format(name, end), encoding="utf-8",index=False)
    return pd.DataFrame(data)


def process_data(path,current_num):
    df = pd.read_csv(path)
    results=calculate_all_periods(df,current_num)
        # 输出文件路径
    output_file = 'ssq{}.csv'.format(current_num)
    write_results_to_csv(df, results, output_file)
    print(f"统计结果已写入文件: {output_file}")

def calculate_statistics(df):
    # 提取红球和蓝球数据
    red_balls = df[['红球_1', '红球_2', '红球_3', '红球_4', '红球_5', '红球_6']]
    blue_balls = df['蓝球']
    
    # 计算红球和蓝球的出现次数
    red_counts = red_balls.apply(pd.Series.value_counts).sum(axis=1).sort_index()
    blue_counts = blue_balls.value_counts().sort_index()
    
    # 计算红球和蓝球的出现频率（平均概率）
    red_freq = red_counts / len(df)
    blue_freq = blue_counts / len(df)
    
    return red_counts, red_freq, blue_counts, blue_freq

# 计算不同时间段的统计数据
def calculate_all_periods(df):
    # 所有期
    all_red_counts, all_red_freq, all_blue_counts, all_blue_freq = calculate_statistics(df)
    
    # 近100期
    recent_100 = df.iloc[-100:]
    recent_100_red_counts, recent_100_red_freq, recent_100_blue_counts, recent_100_blue_freq = calculate_statistics(recent_100)
    
    # 近50期
    recent_50 = df.iloc[-50:]
    recent_50_red_counts, recent_50_red_freq, recent_50_blue_counts, recent_50_blue_freq = calculate_statistics(recent_50)
    
    # 近30期
    recent_30 = df.iloc[-30:]
    recent_30_red_counts, recent_30_red_freq, recent_30_blue_counts, recent_30_blue_freq = calculate_statistics(recent_30)
    
    return {
        'all_red_counts': all_red_counts,
        'all_red_freq': all_red_freq,
        'all_blue_counts': all_blue_counts,
        'all_blue_freq': all_blue_freq,
        'recent_100_red_counts': recent_100_red_counts,
        'recent_100_red_freq': recent_100_red_freq,
        'recent_100_blue_counts': recent_100_blue_counts,
        'recent_100_blue_freq': recent_100_blue_freq,
        'recent_50_red_counts': recent_50_red_counts,
        'recent_50_red_freq': recent_50_red_freq,
        'recent_50_blue_counts': recent_50_blue_counts,
        'recent_50_blue_freq': recent_50_blue_freq,
        'recent_30_red_counts': recent_30_red_counts,
        'recent_30_red_freq': recent_30_red_freq,
        'recent_30_blue_counts': recent_30_blue_counts,
        'recent_30_blue_freq': recent_30_blue_freq,
    }
# 将结果写入CSV文件的新列中
def write_results_to_csv(df, results, output_file):
    # 创建一个新的DataFrame来存储结果
    result_df = pd.DataFrame(index=range(1, 34))  # 红球范围是1-33，蓝球范围是1-16
    
    # 填充结果
    result_df['all_red_counts'] = results['all_red_counts']
    result_df['all_red_freq'] = results['all_red_freq']
    result_df['recent_100_red_counts'] = results['recent_100_red_counts']
    result_df['recent_100_red_freq'] = results['recent_100_red_freq']
    result_df['recent_50_red_counts'] = results['recent_50_red_counts']
    result_df['recent_50_red_freq'] = results['recent_50_red_freq']
    result_df['recent_30_red_counts'] = results['recent_30_red_counts']
    result_df['recent_30_red_freq'] = results['recent_30_red_freq']
    
    # 蓝球的范围是1-16
    blue_result_df = pd.DataFrame(index=range(1, 17))
    blue_result_df['all_blue_counts'] = results['all_blue_counts']
    blue_result_df['all_blue_freq'] = results['all_blue_freq']
    blue_result_df['recent_100_blue_counts'] = results['recent_100_blue_counts']
    blue_result_df['recent_100_blue_freq'] = results['recent_100_blue_freq']
    blue_result_df['recent_50_blue_counts'] = results['recent_50_blue_counts']
    blue_result_df['recent_50_blue_freq'] = results['recent_50_blue_freq']
    blue_result_df['recent_30_blue_counts'] = results['recent_30_blue_counts']
    blue_result_df['recent_30_blue_freq'] = results['recent_30_blue_freq']
    
    # 将红球和蓝球的结果合并到一个CSV文件中
    result_df.to_csv(output_file, index_label='号码')
    blue_result_df.to_csv(output_file, mode='a', index_label='号码')  # 追加蓝球数据

def run(name):
    current_number = get_current_number(name)
    print("【{}】最新一期期号：{}".format(name,current_number))
    if not os.path.exists(fold):
        os.makedirs(fold)
    dataFolder= os.path.join(os.getcwd(),fold)

    if "{}{}".format(name, current_number) in os.listdir(dataFolder):
        print("【{}】数据已经存在，共{}期, ...".format(current_number, len(data)))
    data = spider(name, 1, current_number)
    dataFile = "{}{}".format(name, current_number)
    if dataFile in os.listdir(dataFolder):
        print("【{}】数据准备就绪，共{}期, ...".format(current_number, len(data)))
        process_data(dataFile,current_number)
if __name__ == "__main__":
    if not args.name:
        raise Exception("玩法名称不能为空！")
    else:
        run(name=args.name)