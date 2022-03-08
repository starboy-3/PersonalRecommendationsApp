from scrapy.exporters import CsvItemExporter


def item_type(item):
    return type(item).__name__.replace('Item', '').lower()  # ProductItem => product


class MultiCSVItemPipeline:
    SaveTypes = ['page', 'product']

    def __init__(self):
        self.files = dict([(name, open('./csvs/' + name + '.csv', 'w+b')) for name in self.SaveTypes])
        self.exporters = dict([(name, CsvItemExporter(self.files[name])) for name in self.SaveTypes])

    def spider_opened(self, spider):
        [e.start_exporting() for e in self.exporters.values()]

    def spider_closed(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        item_t = item_type(item)
        if item_t in set(self.SaveTypes):
            self.exporters[item_t].export_item(item)
        return item
