# This is a sample Python script.
from selenium.webdriver.common.by import By

from src.cnki_all_subjects import next_page, get_pages, get_subjects, get_subject, get_search
from tool.common import get_driver


# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # 基础科学数据
    url = "https://epub.cnki.net/kns/brief/result.aspx?dbprefix=SCPD"
    begin_date = '2023-01-01'
    end_date = '2023-01-07'
    path = f'./data/'
    date = (begin_date + end_date).split('-')
    date = ''.join(date)
    csv_name = f'cnki{date}.csv'
    temp = 141
    flag = 1
    # 学科参考位置
    i = 2

    driver = get_driver(url)

    # 按日期进行检索
    get_search(driver, begin_date, end_date)

    # 判断检索出的结果数量
    num = int(driver.find_element(By.XPATH, '//*[@id="countPageDiv"]/span[1]/em').text)

    # if num > 6000:
    # 定位主题
    subjects = get_subjects(driver)
    page, text = get_subject(driver, subjects, i)
    # 获取该学科下的数据
    text = text.split('\n')[0]
    print(text)
    excel_name = f'cnki{date}{text}.xlsx'

    try:
        page = int(driver.find_element(By.XPATH, '//*[@id="countPageDiv"]/span[2]').text.split('/')[-1])
        print(f'共{page}页')
    except Exception as e:
        print(e)

    # while flag < temp:
    #     next_page(driver)
    #     flag += 1
    #
    # else:
    #     get_pages(driver, page, excel_name, path, flag)

    get_pages(driver, page, excel_name, path, flag)
