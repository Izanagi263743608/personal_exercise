# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DoubanItem(scrapy.Item):
    id = scrapy.Field()  # 保存电影ID
    title = scrapy.Field()  # 保存电影名
    types = scrapy.Field()  # 保存电影类型
    region = scrapy.Field()  # 保存制片国家/地区
    directors = scrapy.Field()  # 保存导演名字
    duration = scrapy.Field()  # 保存电影时长
    rate = scrapy.Field()  # 保存电影排名
    url = scrapy.Field()  # 保存电影链接


