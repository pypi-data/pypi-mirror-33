from celery import Celery

from web_crawler.config import Config
from web_crawler.launch import launch_crawler

redis_server = 'redis://{}'.format(Config.REDIS_QUEUE_SERVER)

celery = Celery('tasks', broker=redis_server, backend=redis_server)

def init_celery():
    return celery

@celery.task(bind=True)
def add(self, url):
    launch_crawler(self.request.id, url)
