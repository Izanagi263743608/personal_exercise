# -*- coding: utf-8 -*-
# 完成时间：2017/8/10
# 功能描述：通过从给定的链接开始进行多线程爬取词条标题和简介，并从简介中提取链接进行自动多网页爬取
import sys
import re
import MySQLdb
import requests
import time
from time import ctime
from bs4 import BeautifulSoup
from threading import Thread, Lock


# 中文编码设置
reload(sys)
sys.setdefaultencoding('utf-8')


class Spider:
    def __init__(self, urls):
        self.conn = MySQLdb.connect('localhost', 'root', 'yyj', 'bdbk', charset='utf8')
        self.cursor = self.conn.cursor()
        self.insert_sql = "INSERT INTO lemma(title, content, url) VALUES('%s', '%s', '%s')"
        self.base_url = 'https://baike.baidu.com'
        self.urls = urls
        # 待爬取的url列表
        self.crawl_url = urls
        # 线程列表
        self.threads = []
        # 已爬取的url列表
        self.has_crawl_url = []

    # 清理数据
    def clear_data(self, data):
        data = re.sub('[\n\t]', '', data)
        data = re.sub('\[\d+\]', '', data)
        data = data.strip()
        return data

    # 发送请求并解析html内容提取数据
    def parser(self, url, thread_name, lock):
        resp = requests.get(url)
        # 设置网页内容编码格式为utf-8
        resp.encoding = 'utf-8'
        html = BeautifulSoup(resp.content, 'lxml')
        try:
            # 获取词条标题
            title = html.find('dd', {'class': 'lemmaWgt-lemmaTitle-title'}).find_all('h1')[0].text
            title = self.clear_data(title)
            # 获取词条简介
            content = html.find('div', {'class': 'lemma-summary'}).text
            content = self.clear_data(content)
            # 获取词条简介中的其他链接
            new_urls = html.find('div', {'class': 'lemma-summary'}).find_all('a')
        except AttributeError:
            print('没有找到指定的标签')
            return None
        else:
            lock.acquire()
            print('%s gets %s' % (thread_name, url))
            print('[%s]%s %s' % (ctime(), title, content))
            print('')
            self.cursor.execute(self.insert_sql % (title, content, url))
            self.conn.commit()
            lock.release()
            return new_urls

    def crawl(self, thread_id, lock):
        thread_name = '%s-%s' % ('Thread', thread_id)
        # 当队列有新请求就取出一个请求进行爬取
        while self.crawl_url:
            url = self.crawl_url.pop()
            # 把新请求传给parser函数进行发送并获取从parser返回的新请求列表
            new_urls = self.parser(url, thread_name, lock)
            # 如果爬取失败则将该新请求加入待爬取url列表以便下次重新爬取
            if new_urls is None:
                self.crawl_url.append(url)
                continue
            # 爬取成功则将该新请求加入已爬取url列表中
            self.has_crawl_url.append(url)
            # 对新请求列表进行去重
            for new_url in new_urls:
                if new_url.has_attr('href'):
                    new_url = '%s%s' % (self.base_url, new_url['href'])
                    if new_url not in self.has_crawl_url:
                        if new_url not in self.crawl_url:
                            self.crawl_url.append(new_url)
            # 延迟2s发送请求
            time.sleep(2)

    def start(self):
        # 实例同步锁对象
        lock = Lock()
        # 创建5个线程实例并添加到线程列表中
        for i in range(0, 5):
            thread = Thread(target=self.crawl, args=(i, lock))
            self.threads.append(thread)
        # 启动线程
        for i in range(0, len(self.threads)):
            self.threads[i].start()
        # 等待所有线程执行完
        for i in range(0, len(self.threads)):
            self.threads[i].join()
        self.cursor.close()
        self.conn.close()


def main():
    # 初始化待爬取的url
    urls = ['https://baike.baidu.com/item/%E4%BA%8C%E6%AC%A1%E5%85%83/85064',
            'https://baike.baidu.com/item/Python/407313',
            'https://baike.baidu.com/item/Java/85979',
            'https://baike.baidu.com/item/C++/99272'
            ]
    spider = Spider(urls)
    spider.start()


if __name__ == '__main__':
    main()
