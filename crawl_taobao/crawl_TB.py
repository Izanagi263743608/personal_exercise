# -*- coding: utf-8 -*-
# 完成时间： 2017/8/29
# 功能描述：使用selenium+phantomjs模拟浏览器根据关键词搜索商品并获取所有相关的商品信息存储到redis
from selenium import webdriver
import redis
import time
import re
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import sys

# 中文编码设置
reload(sys)
sys.setdefaultencoding('utf-8')


class Crawler(object):
    def __init__(self):
        # 设置phantomjs的headers，防止服务器识别phantomjs爬虫
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.8',
            'referer': 'https://www.taobao.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        }
        params = DesiredCapabilities.PHANTOMJS
        params['phantomjs.page.customHeaders'] = headers
        self.base_url = 'https://www.taobao.com/'
        self.driver = webdriver.PhantomJS(
            executable_path=r'D:\Python2\phantomjs\phantomjs-2.1.1-windows\bin\phantomjs.exe',
            desired_capabilities=params)
        # 连接redis
        self.r = redis.Redis(host='localhost', port='6379', password='6668428', db=2)
        # 初始化关键词
        self.keyword = ''
        # 记录页数
        self.count = 0

    # 清理数据
    def clear_data(self, data):
        data = re.sub('[\t\n]', '', data)
        data = data.strip(' ')
        return data

    def get_results(self, page_source):
        self.count += 1
        print('收集第%s页所有商品的信息中...'.encode('utf-8') % self.count)
        page = BeautifulSoup(page_source, 'lxml')
        # 获取某页商品列表(其中第二个商品列表的数据是由ajax动态加载的所以BeautifulSoup使用不同的方式提取数据)
        goods_list1 = page.find('div', {'class': 'grid g-clearfix'}).find_all('div', {'class': 'items'})[0].find_all(
            'div', {'data-category': 'auctions'})
        goods_list2 = page.find('div', {'class': 'grid g-clearfix'}).find_all('div', {'class': 'items'})[1].find_all(
            'div', {'data-category': 'personalityData'})
        for goods in goods_list1:
            # 获取商品ID
            goods_id = goods.find('div', {'class': 'row row-2 title'}).find('a')['data-nid']
            # 获取商品名字
            goods_name = goods.find('div', {'class': 'row row-2 title'}).find('a').text.encode('utf-8')
            goods_name = self.clear_data(goods_name)
            # 获取商品链接
            goods_url = goods.find('div', {'class': 'row row-2 title'}).find('a')['href']
            goods_url = self.clear_data(goods_url)
            # 获取商品价格
            price = goods.find('div', {'class': 'price g_price g_price-highlight'}).text.encode('utf-8')
            price = self.clear_data(price)
            # 获取商品支付情况
            paid_off = goods.find('div', {'class': 'deal-cnt'}).text.encode('utf-8')
            paid_off = self.clear_data(paid_off)
            # 获取商家名字
            shop_name = goods.find('div', {'class': 'shop'}).find('a').text.encode('utf-8')
            shop_name = self.clear_data(shop_name)
            # 获取商家链接
            shop_url = goods.find('div', {'class': 'shop'}).find('a')['href']
            shop_url = self.clear_data(shop_url)
            # 获取商家低点
            location = goods.find('div', {'class': 'location'}).text.encode('utf-8')
            location = self.clear_data(location)
            # 将数据存储到redis中
            self.r.hset(goods_id, '商品ID'.encode('utf-8'), goods_id)
            self.r.hset(goods_id, '商品名'.encode('utf-8'), goods_name)
            self.r.hset(goods_id, '商品链接'.encode('utf-8'), goods_url)
            self.r.hset(goods_id, '商品价格'.encode('utf-8'), price)
            self.r.hset(goods_id, '出售情况'.encode('utf-8'), paid_off)
            self.r.hset(goods_id, '商店名'.encode('utf-8'), shop_name)
            self.r.hset(goods_id, '商店链接'.encode('utf-8'), shop_url)
            self.r.hset(goods_id, '商店地点'.encode('utf-8'), location)
            # print(goods_name)
            # print(goods_url)
            # print(price)
            # print(paid_off)
            # print(shop_name)
            # print(shop_url)
            # print(location)
            # print('')

        for goods in goods_list2:
            # 获取商品ID
            goods_id = goods.find('div', {'class': 'row row-2 title'}).find('a')['data-nid']
            # 获取商品名字
            goods_name = goods.find('div', {'class': 'row row-2 title'}).find('a').text.encode('utf-8')
            goods_name = self.clear_data(goods_name)
            # 获取商品链接
            goods_url = goods.find('div', {'class': 'row row-2 title'}).find('a')['href']
            goods_url = self.clear_data(goods_url)
            # 获取商品价格
            price = goods.find('div', {'class': 'price g_price g_price-highlight'}).text.encode('utf-8')
            price = self.clear_data(price)
            # 获取商品支付情况
            paid_off = goods.find('div', {'class': 'deal-cnt'}).text.encode('utf-8')
            paid_off = self.clear_data(paid_off)
            # 获取商家名字
            shop_name = goods.find('div', {'class': 'shop'}).find('a').text.encode('utf-8')
            shop_name = self.clear_data(shop_name)
            # 获取商家链接
            shop_url = goods.find('div', {'class': 'shop'}).find('a')['href']
            shop_url = self.clear_data(shop_url)
            # 获取商家地点
            location = goods.find('div', {'class': 'location'}).text.encode('utf-8')
            location = self.clear_data(location)
            # 将数据存储的袄redis中
            self.r.hset(goods_id, '商品ID'.encode('utf-8'), goods_id)
            self.r.hset(goods_id, '商品名'.encode('utf-8'), goods_name)
            self.r.hset(goods_id, '商品链接'.encode('utf-8'), goods_url)
            self.r.hset(goods_id, '商品价格'.encode('utf-8'), price)
            self.r.hset(goods_id, '出售情况'.encode('utf-8'), paid_off)
            self.r.hset(goods_id, '商店名'.encode('utf-8'), shop_name)
            self.r.hset(goods_id, '商店链接'.encode('utf-8'), shop_url)
            self.r.hset(goods_id, '商店地点'.encode('utf-8'), location)
            # print(goods_id)
            # print(goods_name)
            # print(goods_url)
            # print(price)
            # print(paid_off)
            # print(shop_name)
            # print(shop_url)
            # print(location)
            # print('')

        print('第%s页商品信息收集完成...'.encode('utf-8') % self.count)

    def start_search(self):
        # 打开淘宝主页
        self.driver.get('https://www.taobao.com/')
        # 等待页面加载完搜索框才进行下面的操作
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'q')))
        except TimeoutException:
            print('页面加载失败')
            self.start_search()

        try:
            # 获取搜索框并输入关键词后点击回车键进行搜索
            search = self.driver.find_element_by_xpath('//*[@id="q"]')
            self.keyword = raw_input('请输入商品的关键字:')
            search.send_keys(self.keyword.decode('utf-8'))
            search.send_keys(Keys.ENTER)
        except NoSuchElementException:
            print('没有找到搜索框')
            self.start_search()
        print('正在加载搜索页面...')

        # 如果页面加载失败则重新搜索
        try:
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'mainsrp-itemlist')))
        except TimeoutException:
            print('页面加载失败')
            self.start_search()
        # 如果没有找到与关键字相关的商品列表则结束操作
        try:
            self.driver.find_element_by_xpath('//*[@class="m-itemlist"]')
            print('开始搜集商品信息...')
        except NoSuchElementException:
            print('查询失败,没有找到与该关键字相关的商品...')
            return

        while True:
            try:
                # 获取商品页面内容
                self.get_results(self.driver.page_source)
                time.sleep(3)
                # 搜索下一页的链接并点击
                next_btn = self.driver.find_element_by_xpath('//li[@class="item next"]/a')
                next_btn.click()
            # 已经到达最后一页，结束数据采集
            except NoSuchElementException:
                print('已经到达最后一页...')
                break
            except TimeoutException:
                print('页面加载失败')
                break

        self.driver.close()
        print('商品信息搜集完成....')
        # self.driver.quit()


def main():
    crawler = Crawler()
    crawler.start_search()


if __name__ == '__main__':
    main()
