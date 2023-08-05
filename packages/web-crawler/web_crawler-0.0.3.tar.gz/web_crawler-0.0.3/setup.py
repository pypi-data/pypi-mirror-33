import inspect
import os

from setuptools import setup, find_packages

__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    requires = [req for req in content.split('\\n') if req != '']
    return requires

setup(
    name='web_crawler',
    version='0.0.3',
    description='Web crawler',
    url='https://github.com/ricbartm/web-crawler',
    author='Ricardo Bartolome',
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        'scrapy==1.5.0',
        'celery==4.2.0',
        'redis==2.10.6',
        'domain-count-spider==0.0.3',
    ]
)
