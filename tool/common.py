import csv
import json
import os
from copy import copy

import ddddocr
import jaydebeapi
import pandas as pd
import requests
import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import WebDriverException
import xlrd
import xlwt
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from urllib import parse


def get_soup(url):  # 获取专利具体内容
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = requests.request('GET', url, headers=header)
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    return soup


def get_html_page(url):
    '''
    根据url获取页面数据
    :param url:
    :return:
    '''
    page = requests.get(url)
    content = page.content
    # 将bytes转换成字符串
    content = content.decode('utf-8')
    return content


def get_driver(url):
    try:
        driver = ''
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        # service = Service('/root/1/chain/chromedriver')
        # driver = webdriver.Chrome(service=service, options=options)
        driver = webdriver.Chrome()
        driver.implicitly_wait(30)
        driver.maximize_window()
        driver.get(url)
    except WebDriverException as e:
        print(f"WebDriver异常: {e}")
    finally:
        if driver:
            return driver


def write_csv(content, path):
    f = open(path, 'a', encoding='UTF-8')
    writer = csv.writer(f)
    writer.writerow(content)
    f.close()


def write_excel_value(path, value):
    # 打开工作簿
    workbook = xlrd.open_workbook(path)  # 打开工作簿
    sheets = workbook.sheet_names()  # 获取工作簿中的所有表格

    # 获取工作簿中所有表格中的的第一个表
    worksheet = workbook.sheet_by_name(sheets[0])
    # 获取表格中已存在的数据的行数
    rows_old = worksheet.nrows
    # 将xlrd对象拷贝转化为xlwt对象
    new_workbook = copy(workbook)
    # 获取转化后工作簿中的第一个表格
    new_worksheet = new_workbook.get_sheet(0)
    for i in range(0, len(value)):
        new_worksheet.write(rows_old, i, value[i])  # 追加写入数据，注意是从i+rows_old行开始写入
    new_workbook.save(path)  # 保存工作簿
    # new_workbook.closed()


# 用于创建表头
def write_excel_title(path, name, title):
    index = len(title)  # 获取需要写入数据的行数
    workbook = xlwt.Workbook()  # 新建一个工作簿
    sheet = workbook.add_sheet(name)  # 在工作簿中新建一个表格
    for i in range(0, index):
        for j in range(0, len(title[i])):
            sheet.write(i, j, title[i][j])  # 像表格中写入数据（对应的行和列）
    workbook.save(path)  # 保存工作簿
    print("表头写入数据成功！")


def write_exel(path, name, title, contents, old):
    new = pd.DataFrame(contents, columns=title)
    # 将本页数据写入表格中
    old = pd.concat([old, new])
    print(f'本页数据开始写入{name}')
    try:
        old.to_excel(path + name, index=False)
    except Exception as e:
        print(f"写入excel错误{e}")


def write_pandas(path, value):
    df = pd.DataFrame()
    return df


def connect_db(host, username, password, dbname, port):
    conn = jaydebeapi.connect(
        # host=host,  # 数据库主机地址
        # user=user,  # 数据库用户名
        # password=password,  # 数据库密码
        # database=dbname  # 数据库名
        "com.yashandb.jdbc.YasDriver",
        "jdbc:yashan://" + host + ":" + port + "/" + dbname,
        [username, password],
        "~/1/chain/chain/libs/yashandb-jdbc-1.5.1.jar"
    )
    return conn


def verification_code(driver):
    ocr = ddddocr.DdddOcr()
    with open("", 'rb') as f:
        image = f.read()
    res = ocr.classification(image)
    print(res)


def elements_expand(driver):
    # 删除readonly属性
    script = "document.getElementById('{}').removeAttribute('readonly')".format(id)
    # 执行JavaScript脚本
    driver.execute_script(script)  # 这一步执行后日期就能手动编辑了
    driver.find_element(By.ID, id).clear()  # 清空之前的数据


def decode(s):
    s_encode = s.encode('unicode_escape')
    s_utf8 = s_encode.decode('utf-8').replace('\\x', '%')
    s_un = parse.unquote(s_utf8)
    return s_un


def read_yaml(path):
    with open(path, 'r', encoding='utf-8') as f:
        result = yaml.load(f.read(), Loader=yaml.FullLoader)
        return result


def get_path():
    curpath = os.path.dirname(os.path.realpath(__file__))
    yamlpath = os.path.join(curpath, "park_info.yaml")
    return yamlpath


def json_dict(str):
    '''
    将json字符串转化成dict
    :param str:
    :return:
    '''
    superHeroSquad = json.load(str)


def write_db(url, dbname, tbname, items):
    '''
    通过接口写db
    :param url:
    :param data:
    :return:
    '''
    try:
        data = {'dbname': dbname, 'tbname': tbname, 'items': json.dumps(items)}
        # json_data = json.dumps(data)
        res_interface = requests.post(url, data=data)
    except Exception as e:
        print(e)

    return res_interface









