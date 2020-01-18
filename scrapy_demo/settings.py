BOT_NAME = 'scrapy_demo'

SPIDER_MODULES = ['scrapy_demo.spiders']
NEWSPIDER_MODULE = 'scrapy_demo.spiders'

# 客户端标示
# USER_AGENT = 'move (+http://www.yourdomain.com)'

# robot协议
ROBOTSTXT_OBEY = False

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# 默认请求头
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'cookie': '_ga=GA1.2.525269487.1576475974; _gid=GA1.2.966413974.1576475974; _dx_uzZo5y=c8a44eeb6f8dd4ce783ec796364b853d4668bcc1364dec2bf11d87baca6db650a44046b7; __gads=ID=0533e4fb98a95a2f:T=1576475974:S=ALNI_MY7WudKG4RtCP6GE-XctjL5eDtxwQ; night=0; .Cnblogs.AspNetCore.Cookies=CfDJ8FKe-Oc4rmBCjdz4t-OOIu3djROmZZt2JV8EsfDrZpQE-RK8k4UvhCjeXxKq7fI_Qs5TTxwzRsF3XKLBfYNnSQB6vkinjRWFyPTgO4hGdS0rLwJX0hU-XAf6rpkTQXFZ_d0IA2QLijDKXB6lGSyV3xCg8UeQwdObU1scv4E2PgMT2ABOc6NuHn58mU7z8KefqCYj70H_GFp0Gbt8wW648FqIALaui9yuqd4DbXDLXC-AvrbjugZHCsYlR1KNPf8KCLHRVqY_4e0JcwyfzAuOwUbUk3q1syteiHRxm1I6Lil3GvmJlcT9i1pRdoSOv6P6A84__zcqP9btshl8vM8xKTmmMdWTkyN3kplS2yLRPRYrYEK272yI9GDRT_eHOVPB77gEv0x0QFna5WzQVi73MeQGLi7XQ9jKewq0i8stAjuYl8j1tFI37hM8VaZA4afBm_Y7ihX4Qy8byef0YnH2qcgv1cY2uGyU6eWSQI85iHQKg5XUAbi7-6MbjD6-Y1_cadK6psn585EL-IKky9pzhtQhPt-O9_qActQp5AuRTjW9; .CNBlogsCookie=756FF7D46B6F8617D7BB8B50AB22BF60DC67781C4179D53AAD7CED1514ECCC7F12356CE524B7787B86EAEDAEA318B3BE8EEC3310B17D96BE7D2A777DC1B94CC5170D904021F4A3EC376CFB9E5BEF34D1E7EA01FC',
}

# 管道和中间件
DOWNLOADER_MIDDLEWARES = {
    'scrapy_demo.middlewares.MayiProxyMiddleware': 553,
}
ITEM_PIPELINES = {
    'scrapy_demo.pipelines.CsdnBlogApiPipeline': 300,
}

# 日志
import datetime

now = datetime.datetime.now()
LOG_ENABLED = True
LOG_LEVEL = 'DEBUG'
LOG_FILE = "{}_{}_{}.log".format(now.year, now.month, now.day)

# scrapy-redis分布式搭建
# 去重
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True
# 优先级队列
SCHEDULER_QUEUE_CLASS = "scrapy_redis.queue.SpiderPriorityQueue"
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_START_URLS_AS_SET = True
