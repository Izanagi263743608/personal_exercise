# -*- coding: utf-8 -*-
# 完成时间：2017/8/20
# 功能：根据小说分类爬取顶点小说网中小说的信息(小说名，分类，作者，小说链接，小说连载状态，小说当前总字数，小说ID)
# 并以JSON格式保存到本地
import scrapy
import sys
from bs4 import BeautifulSoup
from scrapy.http import Request
from scrapy.selector import Selector
from ..items import CrawlDingdianItem

reload(sys)
sys.setdefaultencoding('utf-8')


class Myspider(scrapy.Spider):
    name = 'dingdian_spider'
    download_delay = 3
    allowed_domians = ['x23us.com']
    base_url = 'http://www.x23us.com/class/'
    url_suffix = '.html'

    def start_requests(self):
        for i in range(1, 11):
            url = self.base_url + str(i) + '_1' + self.url_suffix
            # 请求不同分类的小说页面
            yield Request(url, self.parse)
            # yield Request('http://www.x23us.com/quanben/1', self.parse)

    def parse(self, response):
        page = BeautifulSoup(response.text, 'lxml')
        page_nums = page.find('div', id='pagelink').find_all('a')[-1].get_text()
        base_url = str(response.url)[:-6]
        for page_num in range(1, int(page_nums) + 1):
            url = base_url + str(page_num) + self.url_suffix
            # 请求某分类小说某页的全部小说
            yield Request(url, self.get_novel)

    def get_novel(self, response):
        page = BeautifulSoup(response.text, 'lxml')
        novels = page.find('dl', id='content').find('table').find_all('tr', bgcolor='#FFFFFF')
        for novel in novels:
            # 获取小说链接
            novel_url = novel.find_all('a')[1]['href']
            # 获取小说名
            name = novel.find_all('a')[1].text
            # 获取小说字数
            serial_word_number = novel.find_all('td')[-3].get_text()
            # 获取小说ID
            novel_id = novel_url[-6:-1]
            # 获取小说简介链接
            brief_url = novel.find_all('a')[0]['href']
            # 请求某部小说简介页面内容
            yield Request(brief_url, self.get_detail, meta={'novel_url': novel_url,
                                                            'name': name,
                                                            'serial_number': serial_word_number,
                                                            'novel_id': novel_id})

    def get_detail(self, response):
        novel = Selector(response)
        item = CrawlDingdianItem()
        # 获取小说类别
        category = novel.xpath('//table[@id="at"]//tr[1]/td[1]/a/text()')[0].extract()
        # 获取小说作者
        author = novel.xpath('//table[@id="at"]//tr[1]/td[2]/text()')[0].extract()
        # 获取小说连载状态
        serial_status = novel.xpath('//table[@id="at"]//tr[1]/td[3]/text()')[0].extract()
        # print(category)
        # print(author)
        # print(serial_status)
        item['name'] = response.meta['name']
        item['category'] = category
        item['author'] = author
        item['novel_url'] = response.meta['novel_url']
        item['serial_status'] = serial_status
        item['serial_number'] = response.meta['serial_number']
        item['novel_id'] = response.meta['novel_id']
        return item
