import re, scrapy, unidecode
from scrapy.exceptions import DropItem
from itemloaders.processors import MapCompose, TakeFirst


def clean_tags(string):
    if bool(re.search('<.*?>', string))==True:
        clean_str=re.sub('<.*?>', '', string)
        return clean_str
    else:
        return string

def normalize_string(string):
    if len(string) > 0:
        norm_string = unidecode.unidecode(string).title().encode('utf8')
        return norm_string
    else:
        raise DropItem('Empty strings are not allowed!')


class PerfumeItem(scrapy.Item):

    default_output_processor = TakeFirst()

    brand = scrapy.Field(input_processor = MapCompose(normalize_string))
    name_var = scrapy.Field(input_processor = MapCompose(clean_tags, normalize_string))
    lilial = scrapy.Field()
    spf = scrapy.Field()
    price_eu = scrapy.Field(input_processor = MapCompose(float))
    ean = scrapy.Field(input_processor = MapCompose(str))
    url = scrapy.Field()