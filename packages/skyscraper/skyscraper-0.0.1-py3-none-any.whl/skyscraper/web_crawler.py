import os
import queue
import threading
from urllib.parse import urljoin

from wattle import Nested, Union, List, Integer, String

from skyscraper.exceptions import ExtractFailed
from skyscraper.results import Json, Console
from skyscraper.schema import CrawlStep, ResultExtractor
from skyscraper.task import Request, ResultTask


class CrawlParams(object):
    start_url = String()


class WebCrawler(object):
    name = String()
    threads = Integer(default=(os.cpu_count() * 2 + 1))
    params = Nested(CrawlParams)
    result_extractor = Nested(ResultExtractor)
    results = Union(Json, Console, default=lambda: Console())
    errors = Union(Json, Console, default=lambda: Console())
    steps = List(CrawlStep)

    FINISHED = 'finished'

    def __init__(self):
        self.queue = queue.LifoQueue()
        self.result_queue = queue.Queue()
        self.pool = []
        self.seen = set()

    def _result_processor(self):
        while True:
            result = self.result_queue.get()
            if result == self.FINISHED:
                self.results.finish()
                print('Got FINISHED. Result processor is exiting')
                return
            self.results.submit(result.result)
            self.result_queue.task_done()

    def _worker(self):
        while True:
            task = self.queue.get()
            if task == self.FINISHED:
                print('Got FINISHED')
                return
            print('Got job {}'.format(task))
            steps = list(self.get_crawl_steps_by_label(task.label))
            task.fetch_content()
            self.seen.add(task)
            if task.label == 'result':
                # process with result extractor
                try:
                    result = self.result_extractor.extract_results(task)
                except Exception as e:
                    print("Failed to extract result on {} ({})".format(
                        task.url, e))
                else:
                    self.result_queue.put(ResultTask(result))
            else:
                try:
                    self.process_simple_step(steps, task)
                except ExtractFailed as e:
                    print("Extraction failed: {}".format(e))
            self.queue.task_done()

    def process_simple_step(self, steps, task):
        for crawl_step in steps:
            for extract in crawl_step.extract:
                try:
                    results = task.use_extractor(extract)
                except Exception as e:
                    raise ExtractFailed(e)
                if isinstance(results, str):
                    self.process_single_result(extract, results, task)
                else:
                    for res in results:
                        self.process_single_result(extract, res, task)

    def process_single_result(self, extract, result, task):
        new_task = Request(label=extract.label,
                           url=urljoin(task.url, result))
        if new_task not in self.seen:
            self.queue.put(new_task)

    def run(self):
        self.generate_initial_tasks()
        for _ in range(self.threads):
            worker = threading.Thread(target=self._worker)
            worker.start()
            self.pool.append(worker)
        threading.Thread(target=self._result_processor).start()
        self.queue.join()
        self.result_queue.join()
        for _ in range(self.threads):
            self.queue.put(self.FINISHED)
            self.result_queue.put(self.FINISHED)

    def generate_initial_tasks(self):
        self.queue.put(Request(label='start', url=self.params.start_url))

    def get_crawl_steps_by_label(self, label):
        for crawl_step in self.steps:
            if crawl_step.label == label:
                yield crawl_step
