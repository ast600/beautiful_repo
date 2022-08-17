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
        item.setdefault('ean', [''])
        if not barcodenumber.check_code('ean13', item['ean']):
            raise DropItem(f"{item['ean']} doesn't match ean13 standard")
        else:
            try:
                self.cur.execute("INSERT INTO ean13_products (ean13, brand, prod_name) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
                                 (item['ean'], item['brand'], item['name_var']))
                self.conn.commit()
                match spider.name:
                    case 'fragrant':    
                        self.cur.execute("INSERT INTO prices_ean13 (product_id, price_eu, product_url, seller_id) VALUES (%s, %s, %s, %s)",
                        (item['ean'], item['price_eu'], item['url'], 1))
                        self.conn.commit()
                    case 'com_fragrant':
                        self.cur.execute("INSERT INTO prices_ean13 (product_id, price_eu, product_url, seller_id) VALUES (%s, %s, %s, %s)",
                        (item['ean'], item['price_eu'], item['url'], 1))
                        self.conn.commit()
                    case 'isabella':    
                        self.cur.execute("INSERT INTO prices_ean13 (product_id, price_eu, product_url, seller_id) VALUES (%s, %s, %s, %s)",
                        (item['ean'], item['price_eu'], item['url'], 2))
                        self.conn.commit()
                    case 'ares':    
                        self.cur.execute("INSERT INTO prices_ean13 (product_id, price_eu, product_url, seller_id) VALUES (%s, %s, %s, %s)",
                        (item['ean'], item['price_eu'], item['url'], 3))
                        self.conn.commit()
                    case 'julius':    
                        self.cur.execute("INSERT INTO prices_ean13 (product_id, price_eu, product_url, seller_id) VALUES (%s, %s, %s, %s)",
                        (item['ean'], item['price_eu'], item['url'], 4))
                        self.conn.commit()
                    case 'dan':    
                        self.cur.execute("INSERT INTO prices_ean13 (product_id, price_eu, product_url, seller_id) VALUES (%s, %s, %s, %s)",
                        (item['ean'], item['price_eu'], item['url'], 5))
                        self.conn.commit()
                    case other:
                        spider.logger.info('No seller match found')
            except:
                self.cur.execute("ROLLBACK;")
        return item
