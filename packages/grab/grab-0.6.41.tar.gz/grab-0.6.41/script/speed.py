import logging
from grab.spider import Spider, Task
import yappi

class MiniSpider(Spider):
    def task_generator(self):
        for x in range(30):
            yield Task('page', url='http://localhost')

    def task_page(self, grab, task):
        assert grab.doc.body.strip() == b'127.0.0.1'


def main(**kwargs):
    #yappi.start()
    logging.getLogger('grab.network').setLevel(logging.INFO)
    bot = MiniSpider(thread_number=10, grab_transport='pycurl',
                     transport='threaded')
    bot.run()
    #yappi.get_thread_stats().print_all()
