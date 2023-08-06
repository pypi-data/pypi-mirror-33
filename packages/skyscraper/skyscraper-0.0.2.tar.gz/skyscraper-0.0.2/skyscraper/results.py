import json

from wattle import String


class ResultProcessor(object):
    def initialize(self):
        pass

    def finish(self):
        pass


class Json(ResultProcessor):
    file = String()

    def __init__(self):
        self._fp = None

    def get_file(self):
        if not self._fp:
            self._fp = open(self.file, 'w')
        return self._fp

    def submit(self, result):
        formatted = json.dumps(result)
        self.get_file().write(formatted)
        self.get_file().write('\n')

    def finish(self):
        self.get_file().close()


class Console(ResultProcessor):
    def submit(self, result):
        print(json.dumps(result))
