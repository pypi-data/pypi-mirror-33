import requests


class Request(object):
    def __init__(self, label, url):
        self.url = url
        self.label = label
        self.resp = None

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "<Task label='{}' url='{}'>".format(self.label, self.url)

    def fetch_content(self):
        self.resp = requests.get(self.url)

    def use_extractor(self, extract):
        return extract.extract(self.resp.text)

    def __hash__(self):
        return hash(self.label + self.url)


class ResultTask(object):
    def __init__(self, result):
        self.result = result
