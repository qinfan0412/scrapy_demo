import logging
import json
import re

import requests
from lxml import etree


class ContentCleanPipeline:
    def process_item(self, item, spider):
        itemdata = item['data']

        self.logger = logging.getLogger(itemdata.get('spidername'))
        self.r = spider.server
        self.logger.debug('strat pipeline')

        self.qrcode_sync = itemdata.get('qrcode_sync', None)
        data = dict()
        if itemdata.get('original_flag', True):
            data['type'] = 'original'
        else:
            data['type'] = 'repost'

        if itemdata.get('from') == 'wechat':
            con_clean_url = 'http://192.168.80.159:9015/v1/con_clean'
            con_clean_headers = {
                'X-Request-AppID': '1573452953'
            }

            con_clean_body = {
                'title': itemdata['title'],
                'editor': 1,
                'userName': itemdata['username'],
                'artDate': itemdata.get('date', ''),
                'itemID': itemdata['aid'],
                'artFrom': 'wechat',
                'artType': data['type'],
                'content': itemdata['article'],
                'mode': 'VideoFormatter,HTMLPurifier,codeSnippet,convertImg,blogWechatUrl'
            }
            if itemdata.get('svg_info'):
                con_clean_body['svg'] = json.dumps(itemdata.get('svg_info'))

            if item['crawler'] == 'wechat':
                con_clean_body['originURL'] = itemdata.get('msg_source_url')

            self.logger.debug('Post con_clean_url body is:')
            self.logger.debug(con_clean_body)
            with open('demo_json.json', 'w') as f:
                f.write(json.dumps(con_clean_body))
            # return

            con_clean_resp = requests.post(con_clean_url, headers=con_clean_headers, json=con_clean_body)
            self.logger.debug('con clean resp: {}, code is {}'.format(con_clean_resp.text, con_clean_resp.status_code))

            con_clean_resp_dict = con_clean_resp.json()
            if con_clean_resp_dict.get('code') == 200 and con_clean_resp_dict.get('message') == '成功':
                self.logger.info('Add <{origin_url}> in redis set ({crawler}:exists_article)'.format(
                    origin_url=item.get('origin_url'), crawler=item.get('crawler'))
                )
                self.r.sadd('{crawler}:exists_article'.format(crawler=item.get('crawler')), item.get('origin_url'))


class CsdnBlogApiPipeline:
    def process_item(self, item, spider):
        itemdata = item['data']

        self.logger = logging.getLogger(itemdata.get('spidername'))
        self.r = spider.server
        self.logger.debug('strat pipeline')
        # self.logger.debug(itemdata)
        # self.logger.info('start pipeline')

        self.qrcode_sync = itemdata.get('qrcode_sync', None)

        self.img_add_host = itemdata.get('img_add_host', None)
        self.img_url_replace_dict = itemdata.get('img_url_replace_dict', None)
        self.img_url_replace_label_dict = itemdata.get('IMG_REPLACE_LABEL_DICT', {'data-src': 'src'})
        self.repalce_attr = itemdata.get('CSDN_BLOG_REPLACE_IMG_ATTR', '')
        self.img_url_replace_completion = itemdata.get('CSDN_BLOG_IMG_URL_COMPLETION', None)
        data = dict()
        if itemdata.get('original_flag', True):
            data['type'] = 'original'
        else:
            data['type'] = 'repost'

        if itemdata.get('from') == 'wechat' or (itemdata.get('from') == 'move_blog' and itemdata.get('sub_from') == 'single'):
            con_clean_url = 'http://csdn-imgconvert.internal.csdn.net/v1/con_clean'
            con_clean_headers = {
                'X-Request-AppID': '1573452953'
            }

            con_clean_body = {
                'title': itemdata['title'],
                'editor': 1,
                'userName': itemdata['username'],
                'artDate': itemdata.get('date', ''),
                'itemID': itemdata['aid'],
                'artFrom': itemdata['from'],
                'artType': data['type'],
                'content': itemdata['article'],
                'mode': 'VideoFormatter,HTMLPurifier,codeSnippet,convertImg,blogWechatUrl'
            }
            if itemdata.get('svg_info'):
                con_clean_body['svg'] = json.dumps(itemdata.get('svg_info'))
            if item['crawler'] == 'wechat':
                con_clean_body['originURL'] = itemdata.get('msg_source_url')
            if itemdata.get('sub_from'):
                con_clean_body['subFrom'] = itemdata.get('sub_from')
            self.logger.debug('Post con_clean_url body is:')
            self.logger.debug(con_clean_body)
            con_clean_resp = requests.post(con_clean_url, headers=con_clean_headers, json=con_clean_body)
            self.logger.debug('con clean resp: {}, code is {}'.format(con_clean_resp.text, con_clean_resp.status_code))
            con_clean_resp_dict = con_clean_resp.json()
            if con_clean_resp_dict.get('code') == 200 and con_clean_resp_dict.get('message') == '成功':
                self.logger.info('Add <{origin_url}> in redis set ({crawler}:exists_article)'.format(
                    origin_url=item.get('origin_url'), crawler=item.get('crawler'))
                )
                self.r.sadd('{crawler}:exists_article'.format(crawler=item.get('crawler')), item.get('origin_url'))
            return

        data['title'] = itemdata.get('title', '')
        raw_content = itemdata.get('article', '')
        if (self.img_url_replace_dict is not None and len(
                self.img_url_replace_dict) != 0) or self.img_add_host is not None:
            new_content = self.replace_img_url(raw_content)
            data['content'] = new_content.replace('&#13;', '')
        else:
            data['content'] = raw_content.replace('&#13;', '')

        data['userName'] = itemdata.get('username', '')
        data['aid'] = itemdata.get('aid', '')
        data['from'] = itemdata.get('from', '')
        data['date'] = itemdata.get('date', '')
        data['channel'] = itemdata.get('channel', '')
        data['crawler'] = itemdata.get('spidername')
        data['sub_from'] = itemdata.get('spidername')
        if itemdata.get('spidername') == 'wechat':
            data['wechaturl'] = itemdata.get('msg_source_url', '')

        data['comment'] = itemdata.get('comment', '')

        httpsession = requests.session()
        CSDN_BLOG_SERVER_TOKEN = 'Nk6K0Buq5LpksfGuJEYoPpnC5zkK'
        CSDN_BLOG_SERVER_HEADER = {'x-acl-token': CSDN_BLOG_SERVER_TOKEN}

        self.httpheaders = {'content-type': 'charset=utf8'}
        # print data
        self.logger.debug(json.dumps(data))
        response = httpsession.post(
            url='http://internalapi.csdn.net/blog-phoenix/MoveBlogApi/api/MoveBlogApi/setArticle',
            headers=CSDN_BLOG_SERVER_HEADER, data=data)
        self.logger.debug(response.text)

        if item.get('crawler') and item.get('origin_url'):
            if json.loads(response.text).get('article_id'):
                self.logger.info('Add <{origin_url}> in redis set ({crawler}:exists_article)'.format(
                    origin_url=item.get('origin_url'), crawler=item.get('crawler'))
                )
                self.r.sadd('{crawler}:exists_article'.format(crawler=item.get('crawler')), item.get('origin_url'))
            return

        json_body = json.loads(response.content)

        self.logger.debug(itemdata.get('source_type', ''))
        self.logger.debug(json_body)

    def replace_img_url(self, html_content):
        self.logger.debug('start dual img')
        try:

            new_content = html_content

            self.logger.debug('step1')
            self.logger.debug(html_content)
            self.logger.debug('==')
            if self.img_url_replace_dict:
                for url_str, url_prefix in self.img_url_replace_dict.items():
                    self.logger.debug(url_str)
                    self.logger.debug(url_prefix)
                    self.logger.debug(new_content)

                    new_content = re.sub(r"\"" + url_str, '"' + url_prefix + url_str, new_content)
                    self.logger.debug(new_content)
            try:
                dom = etree.HTML(new_content)
            except:
                dom = etree.HTML(new_content)
            img_node_list = dom.xpath('//img')

            for img_node in img_node_list:
                attrs = img_node.attrib

                if self.img_add_host:
                    self.logger.debug('step5')
                    if attrs['src'].startswith('/'):
                        attrs['src'] = self.img_add_host + attrs['src']

                if 'data:image' in attrs.get('src', ''):
                    self.logger.debug('step2')
                    for src_label, dest_label in self.img_url_replace_label_dict.items():
                        if attrs.get(src_label, None) is not None:
                            attrs[dest_label] = attrs.get(src_label)
                if self.img_url_replace_completion is not None:
                    self.logger.debug('step3')
                    attrs = img_node.attrib
                    self.logger.debug(attrs)
                    self.logger.debug(self.img_url_replace_completion)
                    attrs['src'] = self.img_url_replace_completion + attrs.get(self.repalce_attr, '')
                self.logger.debug('step6')
            return etree.tostring(dom, pretty_print=True, encoding='utf-8').decode('utf-8')

        except Exception as e:
            self.logger.error(e, exc_info=True)
            # raise StandardError('replace_img_url error')


def verify_datetime(datetime):
    pattern = r'((?!0000)[0-9]{4}-((0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-8])|(0[13-9]|1[0-2])-(29|30)|(0[13578]|1[02])-31)|([0-9]{2}(0[48]|[2468][048]|[13579][26])|(0[48]|[2468][048]|[13579][26])00)-02-29) (20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d$'  # noqa
    if re.match(pattern, datetime):
        return True
