
# selenium
# https://blog.csdn.net/weixin_41671907/article/details/125601580

import pymysql

import time

from selenium.webdriver.common.by import By
import pandas as pd
import ddddocr

from tool.common import get_driver, get_soup


def get_page(driver, flag):
    '''
    获取该页面的数据
    :param flag:
    :return:
    '''
    contents = []
    # 获取每页检索结果
    print("第" + str(flag) + "页")
    list_fz14 = driver.find_elements(By.CLASS_NAME, "fz14")
    time.sleep(2)
    l_fz14 = len(list_fz14)
    print(f'list_fz14长度为{l_fz14}')

    if l_fz14 == 0:  # 为空即为出现验证码
        get_verify(driver)

        # 输入验证码后再次获取页面专利信息
        list_fz14 = driver.find_elements(By.CLASS_NAME, "fz14")

    for l in list_fz14:
        # print(f'第{l}条信息')
        time.sleep(2)
        l_link = l.get_attribute("href")
        # 获取页面专利信息
        content, dict_content = get_data(l_link)
        # print('将该条数据写入csv文件中')
        # write_csv(content, path + csv_name)
        # 创建表头
        # write_excel_title(path + excel_name, excel_name, title)
        # write_excel_value(path + excel_name, content)
        contents.append(content)
        # urls.append(l_link)
        # print("-----urls-----" + str(urls))
        # time.sleep(1)
    print("当前页专利数据获取完成")

    return contents


def get_directory(driver, begin_date, end_date):
    directorys = driver.find_element(By.XPATH, '//*[@id="xkdh"]')
    lis = directorys.find_elements(By.TAG_NAME, 'li')
    for l in lis:
        directory = l.find_element(By.XPATH, './div/i[2]')
        directory_text = l.text
        print(directory_text)
        directory.click()
        time.sleep(1)
    return directory_text


def get_search(driver, begin_date, end_date):
    begin_id = 'datebox2'
    end_id = 'datebox3'
    deal_calendar(driver, begin_id)

    # 公开日检索
    driver.find_element(By.ID, begin_id).send_keys(begin_date)
    deal_calendar(driver, end_id)
    driver.find_element(By.ID, end_id).send_keys(end_date)

    try:
        driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div[3]/div[2]/div[1]/div[7]').click()
    except Exception as e:
        print(e)

    # 页数
    # page = int(driver.find_element(By.XPATH, '//*[@id="countPageDiv"]/span[2]').text.split('/')[-1])
    # print(f'当前搜索结果共{page}页')


def get_subjects(driver):
    # 展开学科分类
    driver.find_element(By.XPATH, '//*[@id="groupPager"]').click()

    # 获取所有学科
    subject_lists = driver.find_elements(By.CLASS_NAME, 'lishow')
    return subject_lists


def get_themes(driver):
    # 展开主题分类
    themes = driver.find_element(By.XPATH, '//*[@id="alink1"]')
    themes.click()

    # 获取所有学科
    themes_lists = driver.find_elements(By.CLASS_NAME, 'lishow')
    return themes_lists


def get_subject(driver, subjects, i):
    '''
    subjects[i]学科下的数据
    :param driver:
    :param subjects:
    :param i:
    :return:
    '''
    subject = subjects[i]
    subject.click()
    time.sleep(1)
    print(f'获取{subject.text}')
    # 当前学科数据页数
    page = int(driver.find_element(By.XPATH, '//*[@id="countPageDiv"]/span[2]').text.split('/')[-1])
    print(f'{subject.text}共{page}页')
    return page, subject.text


def get_pages(driver, page, excel_name, path, flag):
    '''
    获取该学科下的所有数据
    :param driver:
    :param page:
    :param excel_name:
    :param path:
    :return:
    '''
    title = ["url", "名称", "专利类型", "专利号", " 申请日",
             "申请公布号", "授权公告日", "多次公布", "申请人", "地址",
             "发明人", "专辑", "专题", "主分类号", "分类号",
             "国省代码", "页数", "代理机构", "代理人", "优先权",
             "国际申请", "国际公布", "进入国家日期",
             "主权项", "摘要"]
    old = pd.DataFrame(columns=title)
    while flag <= page:
        print(f"开始获取第{flag}页")
        # 获取当前页数据
        contents = get_page(driver, flag)
        new = pd.DataFrame(contents, columns=title)

        # 将本页数据写入表格中
        old = pd.concat([old, new])
        print(f'本页数据开始写入{excel_name}')
        old.to_excel(path + excel_name, index=False)
        # 下一页
        next_page(driver)
        flag += 1
        # print(f"学科数据爬取完成")

    # write_csv(contents)
    # return contents


# 获取专利具体内容
def get_data(url):
    soup = get_soup(url)
    title = soup.find("title").text.split('-')[0]
    dict_content = {}
    titles = []
    values = []
    # 获取专利类型
    item_titles = soup.find_all('span', class_='rowtit')
    item_values = soup.find_all('p', class_='funds')

    for item_title in item_titles:
        # print(item_title.text.strip())
        titles.append(item_title.text.strip().replace('：', ''))

    for item_value in item_values:
        values.append(item_value.text.strip().replace('：', ''))

    # 生成dict
    # print(f'titles:{titles}')
    # print(f'values:{values}')
    dict_content = {i: j for i, j in zip(titles, values)}
    dict_content["名称"] = title

    # 生成list
    content = soup.find_all('p', attrs={'class': 'funds'})
    list_content = [url, title]
    for itme in content:
        list_content.append(itme.text)

    l = len(list_content)

    if l == 17:
        print(f'专利信息长度为{l} 代理机、构代理人、优先权为none')
        list_content.append(None)
        list_content.append(None)
        list_content.append(None)

    if l == 16:
        print(f'专利信息长度为{l} 授权公告号、代理机、构代理人、优先权为none')
        list_content.insert(7, None)
        list_content.append(None)
        list_content.append(None)
        list_content.append(None)
        list_content.append(None)
        list_content.append(None)
        list_content.append(None)

    if l == 18:
        print(f'专利信息长度为{l} 授权公告号、优先权为none')
        list_content.insert(7, None)
        list_content.append(None)
        list_content.append(None)
        list_content.append(None)
        list_content.append(None)

    if l == 19:
        print(f"长度为{l}")
        list_content.insert(7, None)
        list_content.append(None)
        list_content.append(None)
        list_content.append(None)

    if l == 21:
        print(f"长度为{l}")
        list_content.append(None)
        list_content.append(None)

    if l == 23:
        print(l)

    else:
        print(f"长度为{l}数据{list_content}")

    if soup.find('div', attrs={'class': 'claim-text'}):
        try:
            zqx = soup.find('div', attrs={'class': 'claim-text'}).text
            list_content.append(zqx)
            dict_content['主权项'] = zqx
        except Exception as e:
            print(f'主权项{e}')

    else:
        print('主权项为None')
        list_content.append(None)

    if soup.find('div', attrs={'class': 'abstract-text'}):
        try:
            zy = soup.find('div', attrs={'class': 'abstract-text'}).text
            list_content.append(zy)
            dict_content['摘要'] = zy
        except Exception as e:
            print(f'摘要{e}')
    else:
        print('摘要为None')
        list_content.append(None)

    return list_content, dict_content


def next_page(driver):
    try:
        next = driver.find_element('xpath', '//*[@id="PageNext"]')
        # next.click()
        driver.execute_script("arguments[0].click();", next)
        time.sleep(10)
    except Exception as e:
        print(e)


def writer_db(content):
    try:
        conn = pymysql.connect(host="localhost", user="root", password="root@123", db="cnki_patents", port=3306, charset="utf-8")
    except Exception as e:
        print(e)

    cur = conn.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS cnki2023(name VARCHAR(50), type VARCHAR(10));'
    cur.execute(sql, content)
    conn.commit()
    cur.close()


def get_verify(driver):
    img = driver.find_element('xpath', '//*[@id="changeVercode"]')
    input_code = driver.find_element('xpath', '//*[@id="vericode"]')
    button = driver.find_element('xpath', '//*[@id="checkCodeBtn"]')

    # 验证码截图
    img.screenshot("imgCode.png")
    # 识别图片
    ocr = ddddocr.DdddOcr()
    with open("imgCode.png", "rb") as f:
        img_code = f.read()
    res_code = ocr.classification(img_code)
    print(f'验证码是{res_code}')
    input_code.clear()
    input_code.send_keys(res_code)
    time.sleep(2)
    button.click()
    time.sleep(2)
    # 验证码识别错误
    while True:
        try:
            res_err = driver.find_element(By.XPATH, '//*[@id="briefBox"]/div/div[1]/div[1]/label[2]')
        except Exception as e:
            print(f'{e}')
            # no such element说明验证码识别正确
            break
        # 刷新验证码重新识别
        img.click()
        get_verify(driver)


def deal_calendar(driver, id):
    # 删除readonly属性
    script = "document.getElementById('{}').removeAttribute('readonly')".format(id)
    # 执行JavaScript脚本
    driver.execute_script(script)  # 这一步执行后日期就能手动编辑了
    driver.find_element(By.ID, id).clear()  # 清空之前的数据


# if __name__ == '__main__':
#     # 基础科学数据
#     url = "https://epub.cnki.net/kns/brief/result.aspx?dbprefix=SCPD"
#     begin_date = '2023-01-01'
#     end_date = '2023-01-07'
#     path = f'/chain/data/'
#     date = (begin_date + end_date).split('-')
#     date = ''.join(date)
#     csv_name = f'cnki{date}.csv'
#     temp = 141
#     flag = 1
#     # 学科参考位置
#     i = 2
#
#     driver = get_driver(url)
#
#     # 按日期进行检索
#     get_search(driver, begin_date, end_date)
#
#     # 判断检索出的结果数量
#     num = int(driver.find_element(By.XPATH, '//*[@id="countPageDiv"]/span[1]/em').text)
#
#     # if num > 6000:
#     # 定位主题
#     subjects = get_subjects(driver)
#     page, text = get_subject(driver, subjects, i)
#     # 获取该学科下的数据
#     text = text.split('\n')[0]
#     print(text)
#     excel_name = f'cnki{date}{text}3.xlsx'
#
#     try:
#         page = int(driver.find_element(By.XPATH, '//*[@id="countPageDiv"]/span[2]').text.split('/')[-1])
#         print(f'共{page}页')
#     except Exception as e:
#         print(e)
#
#     while flag < temp:
#         next_page(driver)
#         flag += 1
#
#     else:
#         get_pages(driver, page, excel_name, path, flag)
