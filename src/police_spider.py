#!/usr/bin/python

import scrapy
import pytz

from scrapy.crawler import CrawlerProcess
from datetime import datetime, timedelta
from database import actions as db



class MySpider(scrapy.Spider):

    name = 'police_spider'
    allowed_domains = ['http://sledcom.ru/']
    today = datetime.now(pytz.timezone('Europe/Moscow'))
    yesterday = today - timedelta(days=1)

    def start_requests(self):
        #http://sledcom.ru/news/?type=news&dates=15.05.2018%20-%2016.05.2018
        #http://sledcom.ru/news/1/?to=16.06.2018&from=01.06.2018&type=news
        urls = list()
        for i in range(1,4):
            to = self.today.strftime("%d.%m.%Y")
            fromm = self.yesterday.strftime("%d.%m.%Y")
            bs_url = "http://sledcom.ru/news/" + str(i) + "/?to=" + to + "&from=" + fromm + "&type=news"
            urls.append(bs_url)

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        t_list = list()
        h_list = list()
        titles = response.xpath("/html/body//div[@class = 'news-item__title']/a/text()").extract()
        for tits in titles:
            tits.encode('utf-8')
            t_list.append(tits)
        hrefs = response.xpath("/html/body//div[@class = 'news-item__title']/a/@href").extract()
        print(hrefs)
        for href in hrefs:
            h_list.append(href)
        print("\n LENGTH!!!!!!!!!!!!!!!!!")
        print(len(t_list))
        tip = dict(zip(t_list, h_list))
        for key, val in tip.items():
            link = "http://sledcom.ru" + val;
            print(key)
            print(link)
            db.db_insert_raw(self.today, key, link)
        print('url:', response.url)

def main():
    c = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0',
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'output.csv',
    })

    c.crawl(MySpider)
    c.start()

if __name__ == '__main__':
    main()


