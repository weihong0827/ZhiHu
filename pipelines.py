# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo

class ZhihuPipeline:
    def __init__(self):
        client = pymongo.MongoClient('localhost', 27017)
        first_db = client['zhihu']  # connect to or create database
        self.coll = first_db['comment']  # connect to or create collection

    def process_item(self, item, spider):
        self.coll.insert_one(item)
        return item
