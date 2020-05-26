# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ZhihuItem(scrapy.Item):
    _id = scrapy.Field()
    question = scrapy.Field()
    title = scrapy.Field()
    cat = scrapy.Field()
    topic = scrapy.Field()
    answer = scrapy.Field()
    content = scrapy.Field()
    author = scrapy.Field()



