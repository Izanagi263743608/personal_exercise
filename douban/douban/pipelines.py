# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
import settings


class DoubanPipeline(object):
    def __init__(self):
        self.conn = MongoClient(settings.MONGODB_IP, settings.MONGODB_PORT)
        self.db = self.conn[settings.MONGODB_DB]
        self.movies = self.db[settings.MONGODB_COLLECTION]

    def process_item(self, item, spider):
        self.movies.insert({'ID': item['id'], '电影名': item['title'], '类型': item['types'],
                            '制片国家/地区': item['region'], '导演': item['directors'], '片长': item['duration'],
                            '评分': item['rate'], '链接': item['url']})
        self.conn.close()
        return item
