# -*- coding: utf-8 -*-
# 完成时间：2017/8/25
# 功能：获取豆瓣电影中热门电影按热度排序的电影信息并保存到MongoDB
from scrapy import Request
from ..items import DoubanItem
import scrapy
import json


class Douban_Spider(scrapy.Spider):
    # 定义爬虫名字
    name = 'douban'
    # 限定在该域名下进行爬取
    allowed_domain = ['movie.douban.com']
    # 每页电影列表的基础api
    base_movies_url = 'https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=20&page_start='
    # 电影详细信息的基础api
    base_movie_url = 'https://movie.douban.com/j/subject_abstract?subject_id='

    def start_requests(self):
        # 爬取入口为第一页电影列表的api，其中limit表示每页显示20部电影，
        # page_start为当前页第一部电影与第一页第一部电影的偏移量，第一页第一部电影的position为0
        yield Request('https://movie.douban.com/j/search_subjects?type=movie&tag=%E7%83%AD%E9%97%A8&sort=recommend&page_limit=20&page_start=0',
                      callback=self.parse_movies)

    def parse_movies(self, response):
        # 获取每页的偏移量
        page_start = int(response.url.split('=')[-1])
        # 解析JSON格式的电影列表
        movies = json.loads(response.text)['subjects']
        for movie in movies:
            # 获取电影ID
            movie_id = movie['id']
            # 拼接每部电影的api
            movie_api_url = self.base_movie_url + movie_id
            # 发送获取电影信息的request
            yield Request(movie_api_url, callback=self.parse_movie)
        # print(page_start)

        if page_start <= 300:  # 设定最大偏移量为300
            # 获取下一页的偏移量
            page_start += 20
            # 拼接下一页电影列表的api
            movies_api_url = self.base_movies_url + str(page_start)
            # print(movies_api_url)
            # 发送获取电影列表的request
            yield Request(movies_api_url, callback=self.parse_movies)

    def parse_movie(self, response):
        # 实例化item对象
        item = DoubanItem()
        # 解析json格式的电影信息
        movie = json.loads(response.text)['subject']
        # id = movie['id']
        # title = movie['title']
        # types = movie['types']
        # region = movie['region']
        # directors = movie['directors']
        # duration = movie['duration']
        # rate = movie['rate']
        # url = movie['url']
        # print(id, title, types, region, directors, duration, rate, url)
        item['id'] = movie['id']
        item['title'] = movie['title']
        item['types'] = movie['types']
        item['region'] = movie['region']
        item['directors'] = movie['directors']
        item['duration'] = movie['duration']
        item['rate'] = movie['rate']
        item['url'] = movie['url']
        yield item
