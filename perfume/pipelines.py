import numpy as np

class FragrantPipeline:
    def process_item(self, item, spider):
        item.setdefault('ean', [np.nan])
        if len(item['ean']) != len(item['price_eu']):
            if len(item['ean']) < len(item['price_eu']):
                while not (len(item['ean']) == len(item['price_eu'])):
                    item['ean'].append(np.nan)
            else:
                while not (len(item['ean']) == len(item['price_eu'])):
                    item['ean'].pop()
        else:
            pass
        return item
