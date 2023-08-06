import click
from wattle import Schema

from skyscraper.web_crawler import WebCrawler


@click.group()
def cli():
    pass


@cli.command('run')
@click.argument('crawler_definition')
def run_crawler(crawler_definition):
    print('Running {}'.format(crawler_definition))
    schema = Schema(WebCrawler)
    crawler = schema.read_yml(crawler_definition)
    crawler.run()
