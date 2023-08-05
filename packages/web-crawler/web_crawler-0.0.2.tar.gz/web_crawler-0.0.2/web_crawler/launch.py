from scrapy.crawler import CrawlerProcess
from domain_count_spider.spiders.urlretriever import URLRetriever
from web_crawler.aggregators import DomainCountAggregator
from web_crawler.redis_pool import RedisPool


def launch_crawler(request_id, url):
    crawler = CrawlerProcess()
    crawler.crawl(URLRetriever(), start_urls=[url])
    crawler.start()

    redis_conn = RedisPool()

    aggregator = DomainCountAggregator(
        input_file='items.jl',
    )

    result = aggregator.get_result()

    redis_conn.set(request_id, result)
