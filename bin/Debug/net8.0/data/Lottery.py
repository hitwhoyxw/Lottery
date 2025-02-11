# -*- coding:utf-8 -*-
"""
Author: BigCat
"""
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
    current_date = datetime.now().strftime("%Y%m%d")
    df.to_csv("{}{}".format(name, current_date), encoding="utf-8")
    return pd.DataFrame(data)

def run(name):
    """
    :param name: 玩法名称
    :return:
    """
    current_number = get_current_number(name)
    print("【{}】最新一期期号：{}".format(name,current_number))
    if not os.path.exists(fold):
        os.makedirs(fold)
    data = spider(name, 1, current_number)
    dataFolder= os.path.join(os.getcwd(),fold)
    current_date = datetime.now().strftime("%Y%m%d")
    if "{}{}".format(name, current_date) in os.listdir(dataFolder):
        print("【{}】数据准备就绪，共{}期, ...".format(current_number, len(data)))

if __name__ == "__main__":
    if not args.name:
        raise Exception("玩法名称不能为空！")
    else:
        run(name=args.name)