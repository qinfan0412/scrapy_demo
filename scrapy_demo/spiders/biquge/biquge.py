from scrapy_redis.spiders import RedisSpider
from scrapy.http import TextResponse
from scrapy import Request


class Biquge(RedisSpider):
    name = 'biquge'
    redis_key = 'biquge:start_urls'

    def start_requests(self):
        url = 'http://www.xbiquge.la/xiaoshuodaquan/'
        yield Request(url, callback=self.get_article_list, dont_filter=True)

    def get_article_list(self, response: TextResponse):
        article_url_list = response.xpath('//div[@class="novellist"]/ul/li/a/@href').extract()
        for article_url in article_url_list:
            yield Request(article_url, callback=self.get_chapter_list, dont_filter=True)

    def get_chapter_list(self, response: TextResponse):
        chapter_url_list = response.xpath('//div[@id="list"]/dl/dd/a/@href').extract()
        chapter_url_list = ['http://www.xbiquge.la' + i for i in chapter_url_list]
        for chapter_url in chapter_url_list:
            print(chapter_url)
            yield Request(chapter_url, callback=self.get_content, dont_filter=True)

    def get_content(self, response: TextResponse):
        book_name = response.xpath('//div[@class="con_top"]/a[3]/text()').extract_first()
        title_name = response.xpath('//div[@class="bookname"]/h1/text()').extract_first().strip('正文')
        article = ''.join(response.xpath('string(//div[@id="content"])').extract())
        if book_name and title_name and article:
            with open('/Users/csdn/Desktop/book/{}_{}.txt'.format(book_name, title_name), 'w') as f:
                f.write(article)
                print(book_name + title_name + '下载成功')
