import re
import numpy as np
import scrapy
from itemloaders.processors import MapCompose, Identity


def split_ean(myString):
    newList = myString.replace(' ','').replace('\n', '').split('/')
    nan_list = [*[np.nan if x=='...' else x for x in newList]]
    return nan_list


def clean_ean(stin):
    if isinstance(stin, str):
        if len(stin)==13 and bool(re.match(r"[0-9]+", stin))==True:
            return stin
        else:
            return split_ean(stin)
    else:
        return stin


class PerfumeItem(scrapy.Item):
    brand = scrapy.Field()
    name_var = scrapy.Field()
    price_eu = scrapy.Field(input_processor=MapCompose(float), output_processor=Identity())
    ean = scrapy.Field(input_processor=MapCompose(clean_ean), output_processor=Identity())
