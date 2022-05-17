import re
import numpy as np
import scrapy
from itemloaders.processors import MapCompose, Identity


def clean_ean(stin):
    if type(stin)=='string':
        if len(stin)==13 and bool(re.match(r"[0-9]+", stin))==True:
            return stin
        else:
            my_list = stin.split(' /')
            my_list=[*[s.strip() for s in my_list]]
            return my_list
    else:
        return stin


class PerfumeItem(scrapy.Item):
    brand = scrapy.Field()
    name_var = scrapy.Field()
    price_eu = scrapy.Field(input_processor=MapCompose(float), output_processor=Identity())
    ean = scrapy.Field(input_processor=MapCompose(clean_ean), output_processor=Identity())
