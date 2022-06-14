import numpy as np
import barcodenumber
import psycopg2
from dotenv import dotenv_values
from scrapy.exceptions import DropItem
from scrapy.exceptions import CloseSpider


class FragrantPipeline:

    def open_spider(self, spider):
        conf = dotenv_values()
        self.conn = psycopg2.connect(dbname=conf['DB_NAME'], user=conf['USERNAME'],
                                   password=conf['DB_PASSWORD'], host=conf['HOST'])
        self.cur = self.conn.cursor()
        try:
            self.cur.execute("CREATE TABLE IF NOT EXISTS ean13_products (ean13 varchar(13) PRIMARY KEY, brand varchar, prod_name varchar);")
            self.conn.commit()
        except:
            raise CloseSpider(reason="Couldn't create the table in the database")

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()


    def process_item(self, item, spider):
        item.setdefault('brand', [''])
        item.setdefault('ean', [np.nan])
        if not barcodenumber.check_code('ean13', item['ean'][0]) or not bool(item['brand'][0]):
            raise DropItem(f"{item['ean'][0]} doesn't match ean13 standard or brand field is empty")
        else:
            try:
                self.cur.execute("INSERT INTO ean13_products (ean13, brand, prod_name) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                                 (item['ean'][0], item['brand'][0], item['name_var'][0]))
                self.conn.commit()
            except:
                self.cur.execute("ROLLBACK;")
        return item
