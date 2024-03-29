from dotenv import dotenv_values

conf = dotenv_values()

BOT_NAME = 'perfume'
SPIDER_MODULES = ['perfume.spiders']
NEWSPIDER_MODULE = 'perfume.spiders'
ROBOTSTXT_OBEY = True
SPLASH_URL = conf['SPLASH_LINK']
SPLASH_USER = conf['SPLASH_USR']
SPLASH_PASS = conf['SPLASH_PASSWD']
DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'
ITEM_PIPELINES = {
    'perfume.pipelines.FragrantPipeline': 800}
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 400]
HTTPCACHE_ENABLED = False
COOKIES_ENABLED = False