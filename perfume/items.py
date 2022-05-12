import scrapy
from itemloaders.processors import MapCompose, Identity


def clean_ean(stin):
    return stin.split(' /')


class PerfumeItem(scrapy.Item):
    brand = scrapy.Field()
    name_var = scrapy.Field()
    price_eu = scrapy.Field(input_processor=MapCompose(float), output_processor=Identity())
    ean = scrapy.Field(input_processor=MapCompose(str.strip, clean_ean), output_processor=Identity())
