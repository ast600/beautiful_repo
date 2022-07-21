import re, scrapy, unidecode
from scrapy.exceptions import DropItem
from itemloaders.processors import Compose, Identity


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
    brand = scrapy.Field(input_processor = Compose(normalize_string), output_processor = Identity())
    name_var = scrapy.Field(input_processor = Compose(clean_tags, normalize_string), output_processor = Identity())
    lilial = scrapy.Field()
    spf = scrapy.Field()
    price_eu = scrapy.Field(input_processor = Compose(float), output_processor = Identity())
    ean = scrapy.Field(input_processor = Compose(str), output_processor = Identity())
    url = scrapy.Field()