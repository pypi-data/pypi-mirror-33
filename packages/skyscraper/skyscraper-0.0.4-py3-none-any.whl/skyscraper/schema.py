import json
import os
import queue
import threading
from urllib.parse import urljoin

import bs4

from skyscraper.exceptions import ExtractFailed
from skyscraper.results import Json, Console
from skyscraper.task import Request, ResultTask
from wattle import String, Nested, Integer, Choice, List, Boolean, Union


class ExtractRules(object):
    select = String(default="")
    attr = String(default="")
    text = Boolean(default=False)
    single = Boolean(default=False)

    def extract(self, content, overrides=None):
        if overrides:
            self.override_attrs(overrides)
        parsed = bs4.BeautifulSoup(content, 'html.parser')
        items = parsed.select(self.select)
        if self.attr:
            func = lambda i: i.get(self.attr)
        elif self.text:
            func = lambda i: i.text
        else:
            raise ValueError('Invalid Extract configuration')
        results = [func(i) for i in items]
        results = list(filter(lambda x: x is not None, results))
        if self.single:
            return results[0].strip()
        return [r.strip() for r in results]

    def override_attrs(self, overrides):
        for k, v in overrides.items():
            setattr(self, k, v)


class ResultExtractRules(object):
    name = String()
    rules = Nested(ExtractRules)


class Extract(object):
    # the type of the extraction method
    type = Choice(['element_attr', 'ahrefs', 'result'])
    # the label for the results
    label = String()
    # the ExtractRules used to extract content from page
    rules = Nested(ExtractRules)

    def extract(self, text):
        if self.type == 'element_attr':
            return self.element_attr(text)
        elif self.type == 'ahrefs':
            return self.ahrefs(text)

    def element_attr(self, text):
        return self.rules.extract(text)

    def ahrefs(self, text):
        items = self.rules.extract(text, overrides={'attr': 'href'})
        if isinstance(items, str):
            return items
        hrefs = [i for i in items if i != '#']
        return hrefs


class CrawlStep(object):
    name = String()
    extract = List(Extract)
    label = String()


class ResultExtractor(object):
    fields = List(ResultExtractRules)

    def extract_results(self, task):
        result = {}
        for field in self.fields:
            result[field.name] = task.use_extractor(field.rules)
        return result
