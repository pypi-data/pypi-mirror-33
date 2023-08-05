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
    result_list = []
    for key, value in result.iteritems():
        result_list.append('{}:{}'.format(key, value))

    result_as_string = '\n'.join(result_list)

    redis_conn.set(request_id, result_as_string)
