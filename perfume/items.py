import re, scrapy, unidecode
from scrapy.exceptions import DropItem
from itemloaders.processors import MapCompose, TakeFirst, Identity


def clean_tags(string):
    if bool(re.search('<.*?>', string))==True:
        clean_str=re.sub('<.*?>', '', string)
        return clean_str
    else:
        return string

def normalize_string(string):
    if len(string) > 0:
        norm_string = unidecode.unidecode(string).title()
        return norm_string
    else:
        raise DropItem('Empty strings are not allowed!')


class PerfumeItem(scrapy.Item):
    brand = scrapy.Field(input_processor = MapCompose(normalize_string), output_processor = TakeFirst())
    name_var = scrapy.Field(input_processor = MapCompose(clean_tags, normalize_string), output_processor = TakeFirst())
    price_eu = scrapy.Field(input_processor = MapCompose(float), output_processor = TakeFirst())
    ean = scrapy.Field(input_processor = MapCompose(str), output_processor = TakeFirst())
    url = scrapy.Field(input_processor=Identity(), output_processor = TakeFirst())