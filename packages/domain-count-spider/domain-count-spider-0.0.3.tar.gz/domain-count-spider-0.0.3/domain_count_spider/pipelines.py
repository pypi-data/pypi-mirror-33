class PlainFilePipeline(object):
    """
    This pipeline is in charge of persisting into a file
    every item that is yield byt the Scrapy Spider.

    TODO: we need to add some entropy to the results filename so in the
    case this runs multiple times in the same node (queues, multiprocess,
    etc) the results files do not get overwritten by different invocations.
    """

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = item['url'] + "\n"
        self.file.write(line)
        return item
