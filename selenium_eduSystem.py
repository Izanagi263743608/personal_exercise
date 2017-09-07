# -*- coding: utf-8 -*-
# 完成时间:2017/8/25
# 功能:登录教务系统并获取并学生每学年的各科学分和绩点(验证采用人工打码)
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from urllib import quote
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import sys

# 中文编码设置
reload(sys)
sys.setdefaultencoding('utf-8')

# 设置浏览器的请求头
headers = {'Accept': '*/*',
           'Accept-Encoding': 'gzip',
           'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
           'Cache-Control': 'max-age=0',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36'
           }
params = DesiredCapabilities.PHANTOMJS

# 设置浏览器的Headers反反爬虫
params['phantomjs.page.customHeaders'] = headers
driver = webdriver.PhantomJS(executable_path=r'D:\Python2\phantomjs\phantomjs-2.1.1-windows\bin\phantomjs.exe',
                             desired_capabilities=params)


def parse_score(page_source):
    page = BeautifulSoup(page_source, 'lxml')
    academic_year = page.find('span', id="lbl_bt").text
    # 初始化总学分
    credit_sum = 0
    # 初始化总绩点
    grade_point_sum = 0
    # 获取每行的课程内容
    courses = page.find('table', id="Datagrid1").find('tbody').find_all('tr')
    print('- - - - - - - - - - %s - - - - - - - - - ' % academic_year)
    for i in range(1, len(courses)):
        # 获取学期数
        term = courses[i].find_all('td')[1].text
        # 获取课程名
        name = courses[i].find_all('td')[3].text
        # 获取课程性质
        category = courses[i].find_all('td')[4].text
        credit = courses[i].find_all('td')[6].text
        if credit == ' ':
            credit = 0
        credit = float(credit)
        grade_point = courses[i].find_all('td')[7].text
        if grade_point == ' ':
            grade_point = 0
        grade_point = float(grade_point)
        print('学期:%s 课程名称:%s 课程性质:%s 学分:%s 绩点:%s'.encode('utf-8') % (term, name, category, credit, grade_point))
        credit_sum += credit
        grade_point_sum += grade_point
    print('该学年总学分为:%s 总绩点为:%s'.encode('utf-8') % (credit_sum, grade_point_sum))
    print('- - - - - - - - - - 神奇的分割线 - - - - - - - - - ')


def main():
    # 设置打开的浏览器窗口大小
    driver.set_window_size(1366, 768)
    # 打开教务系统登录页面
    driver.get('http://jwxt.gcu.edu.cn/default2.aspx')
    try:
        # 等待页面加载完登录按钮才进行后面的操作
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'Button1')))
    finally:
        print('开始登录教务系统...')
        # 获取用户名输入框并输入帐号
        user = raw_input('请输入学号:')
        driver.find_element_by_id('txtUserName').send_keys(user)
        time.sleep(1)
        # 获取密码框并输入密码
        psw = raw_input('请输入密码:')
        driver.find_element_by_id('Textbox1').send_keys(psw)
        time.sleep(1)
        # 截屏查看验证码
        driver.save_screenshot(r'C:\Users\Administrator\Desktop\test\captcha.png')
        # 手动输入验证码
        captcha = raw_input('请输入验证码:')
        # 选取验证码输入框
        driver.find_element_by_id('txtSecretCode').send_keys(captcha)
        # 选取并点击登录按钮
        driver.find_element_by_name('Button1').click()
        print('登录成功，已经进入教务系统主界面...')
        # 跳转到查询成绩的链接，该链接由抓网页发送获取学年成绩的get请求的包获得
        try:
            name = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_id('xhxm')).text.encode('gb2312')
        except TimeoutException:
            print('页面加载失败，请检查网络状态是否正常...')
            return
        driver.get('http://jwxt.gcu.edu.cn/xscjcx.aspx?xh=%s&xm=%s&gnmkdm=N121605' % (user, quote(name)))
        print('正跳转到查询成绩界面...')
        # 点击新页面的链接标签跳转到真正查询成绩的页面
        driver.find_element_by_tag_name('a').click()
        time.sleep(1)
        # 获取学年下拉框的所有可选选项
        options = driver.find_elements_by_xpath('//*[@id="ddlXN"]/option')
        print('成功进入查询成绩界面')
        # 循环获取并点击学年下拉框的每个选项，接着点击学年成绩按钮查询每个的学年成绩
        for i in range(1, len(options)):
            driver.find_elements_by_xpath('//*[@id="ddlXN"]/option')[i].click()
            driver.find_element_by_id('btn_xn').click()
            time.sleep(1)
            # 解析查询学年成绩后的网页内容
            parse_score(driver.page_source)
            # 截图查看学年成绩
            # driver.save_screenshot(r'C:\Users\Administrator\Desktop\test\%s.png' % str(i))
        driver.close()


if __name__ == '__main__':
    main()
