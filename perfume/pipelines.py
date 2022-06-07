import numpy as np
import barcodenumber
import psycopg2
from dotenv import dotenv_values
from scrapy.exceptions import DropItem


class FragrantPipeline:

    def open_spider(self, spider):
        conf=dotenv_values()
        self.conn=psycopg2.connect(dbname=conf['DB_NAME'], user=conf['USERNAME'],
                                   password=conf['DB_PASSWORD'], host=conf['HOST'])
        self.cur=self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS ean13_products (ean13 varchar(13) PRIMARY KEY, brand varchar, prod_name varchar);")

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()


    def process_item(self, item, spider):
        for field in item.fields:
            item.setdefault(field, [np.nan])
        code_check = barcodenumber.check_code('ean13', item['ean'][0])
        if not code_check:
            raise DropItem(f"{item['ean'][0]} doesn't match ean13 standard")
        else:
            try:
                self.cur.execute("INSERT INTO ean13_products (ean13, brand, prod_name) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                                 (item['ean'][0], item['brand'][0], item['name_var'][0]))
                self.conn.commit()
            except:
                self.cur.execute("ROLLBACK;")
        return item