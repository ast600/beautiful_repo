BOT_NAME = 'perfume'
SPIDER_MODULES = ['perfume.spiders']
NEWSPIDER_MODULE = 'perfume.spiders'
ROBOTSTXT_OBEY = True
SPLASH_URL = 'http://localhost:8050/'
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
TELNETCONSOLE_PORT = [5000, 65000]
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 400]
HTTPCACHE_ENABLED = True