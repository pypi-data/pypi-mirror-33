import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.python import unique

class URLRetriever(scrapy.Spider):
    name = 'domain-count'
    custom_settings = {
        'ITEM_PIPELINES': {
            'domain_count_spider.pipelines.PlainFilePipeline': 400,
        },
    }

    def __init__(self, start_urls=None):
        self.start_urls = start_urls

    def _extract_links(self, response):
        link_extractor = LinkExtractor()
        return unique(link_extractor.extract_links(response))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_l0)

    def parse_l0(self, response):

        links = self._extract_links(response)
        self.logger.info('[parse] Found %s links to follow on %s', len(links), response.url)
        for link in links:
            self.logger.info('[parse L0] Following link %s', link.url)
            yield {'url': link.url}
            yield scrapy.Request(link.url, callback=self.parse_l1)

    def parse_l1(self, response):

        links = self._extract_links(response)
        for link in links:
            self.logger.info('[parse L1] Following link %s', link.url)
            yield {'url': link.url}
