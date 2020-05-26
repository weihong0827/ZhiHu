# -*- coding: utf-8 -*-
import scrapy
from lxml import etree
import json
from zhihu.items import ZhihuItem

class ZhihuSpiderSpider(scrapy.Spider):
    name = 'zhihu_spider'
    allowed_domains = ['zhihu.com']
    start_urls = ['https://www.zhihu.com/topics']
    premap = 'http://www.zhihu.com/api/v4/topics/{}/feeds/essence?limit=10&offset=0'
    question_link = 'https://www.zhihu.com/api/v4/questions/{}/answers?include=data%5B%2A%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Crelevant_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cis_labeled%2Cis_recognized%2Cpaid_info%2Cpaid_info_content%3Bdata%5B%2A%5D.mark_infos%5B%2A%5D.url%3Bdata%5B%2A%5D.author.follower_count%2Cbadge%5B%2A%5D.topics&limit=5&offset=0&platform=desktop&sort_by=default'

    def get_comment(self, response):

        data = json.loads(response.text)
        paging = data['paging']

        for info in data['data']:
            voteup = info['voteup_count']
            item = ZhihuItem()
            item['title'] = response.meta.get('title')
            item['question'] = response.meta.get('question')
            item['cat'] = response.meta.get('cat')
            item['topic'] = response.meta.get('topic')
            item['author'] = info['author']['name']
            content = info['content']
            content = etree.HTML(content)
            content = '\n'.join(content.xpath('.//p/text()'))
            item['answer'] = info['id']
            item['content'] = content
            yield item

        if not paging['is_end']:
            yield scrapy.Request(paging['next'], callback=self.get_comment,
                                 dont_filter=True,
                                 meta={'title': item['title'], 'question': item['question'], 'cat': item['cat'],
                                       'topic': item['topic']})

    def get_top_ans(self, response):
        cat = response.meta.get('cat')
        topic = response.meta.get('topic')
        data = json.loads(response.text)
        paging = data['paging']

        for num in data['data']:
            try:

                title = num['target']['question']['title']
                question_id = num['target']['question']['id']
                question_url = self.question_link.format(question_id)
                yield scrapy.Request(question_url, callback=self.get_comment,
                                     dont_filter=True,
                                     meta={'title': title, 'question': question_id, 'cat': cat, 'topic': topic})
            except KeyError:
                pass

        if not paging['is_end']:
            yield scrapy.Request(paging['next'], callback=self.get_top_ans,
                                 dont_filter=True,
                                 meta={'cat': cat, 'topic': topic})

    def get_topic(self, response):
        id = response.meta.get('id')
        offset = response.meta.get('offset')
        print(id)
        cat = response.meta.get('cat')

        data = json.loads(response.text)
        offset += len(data['msg'])
        print(offset)
        for msg in data['msg']:
            html = etree.HTML(msg)
            url = html.xpath('.//a/@href')[0].split('/')[-1]
            #print(url)
            topic = html.xpath('.//strong/text()')[0]
            yield scrapy.Request(self.premap.format(url), callback=self.get_top_ans,
                                 dont_filter=True,
                                 meta={'cat': cat, 'topic': topic})
        if data['msg']:

            yield scrapy.FormRequest('https://www.zhihu.com/node/TopicsPlazzaListV2', callback=self.get_topic,
                                     dont_filter=True,
                                     meta={'id': id, 'offset': offset, 'cat': cat},
                                     formdata={
                                         'method': 'next',
                                         'params': json.dumps({"topic_id": id, "offset": offset, "hash_id": ""})
                                     })
        else:
            print(offset, id)

    def parse(self, response):
        lis = response.xpath('.//div[@class="zu-main-content"]//ul/li')
        for li in lis:
            id = li.xpath('./@data-id').extract_first()
            cat = li.xpath('./a/text()').extract_first()
            print(cat)
            yield scrapy.FormRequest('https://www.zhihu.com/node/TopicsPlazzaListV2', callback=self.get_topic,
                                     dont_filter=True,
                                     meta={'id': id, 'offset': 0, 'cat': cat},  # changed position
                                     formdata={
                                         'method': 'next',
                                         'params': json.dumps({"topic_id": id, "offset": 0, "hash_id": ""})
                                     })
