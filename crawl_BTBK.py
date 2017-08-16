# -*- coding: utf-8 -*-
# 单线程爬虫
import sys
import requests
from time import ctime
from bs4 import BeautifulSoup

# 中文编码设置
reload(sys)
sys.setdefaultencoding('utf-8')


class Spider:
    def __init__(self, url):
        self.base_url = 'https://baike.baidu.com'
        self.crawl_url = []
        self.crawl_url.append(url)
        self.has_crawl_url = set()

    def parser(self, url):
        resp = requests.get(url)
        html = BeautifulSoup(resp.content, 'lxml')
        try:
            title = html.find('dd', {'class': 'lemmaWgt-lemmaTitle-title'}).find_all('h1')[0].text
            content = html.find('div', {'class': 'lemma-summary'}).text
            new_urls = html.find('div', {'class': 'lemma-summary'}).find_all('a')
        except AttributeError:
            print('没有找到指定的标签')
            return None
        else:
            print('[%s]%s %s' % (ctime(), title, content))
            return new_urls

    def crawl(self):
        while self.crawl_url:
            url = self.crawl_url.pop()
            print '%s%s' % (self.base_url, url)
            self.has_crawl_url.add(url)
            new_urls = self.parser(url)
            if new_urls is None:
                continue
            for new_url in new_urls:
                if new_url.has_attr('href'):
                    new_url = '%s%s' % (self.base_url, new_url['href'])
                    if new_url not in self.has_crawl_url:
                        if new_url not in self.crawl_url:
                            self.crawl_url.append(new_url)


def main():
    spider = Spider('https://baike.baidu.com/item/%E4%BA%8C%E6%AC%A1%E5%85%83/85064')
    spider.crawl()


if __name__ == '__main__':
    main()