from scrapy.exporters import CsvItemExporter


class FragrantPipeline:
    def process_item(self, item, spider):
        return item
