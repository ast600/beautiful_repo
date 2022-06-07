import re
import numpy as np
import scrapy
from itemloaders.processors import MapCompose, Identity


def clean_tags(string):
    if bool(re.search('<.*?>', string))==True:
        clean_str=re.sub('<.*?>', '', string)
        return clean_str
    else:
        return string


class PerfumeItem(scrapy.Item):
    brand = scrapy.Field()
    name_var = scrapy.Field(input_processor=MapCompose(clean_tags), output_processor=Identity())
    lilial = scrapy.Field()
    spf = scrapy.Field()
    price_eu = scrapy.Field(input_processor=MapCompose(float), output_processor=Identity())
    ean = scrapy.Field(input_processor=MapCompose(str), output_processor=Identity())
    url = scrapy.Field()