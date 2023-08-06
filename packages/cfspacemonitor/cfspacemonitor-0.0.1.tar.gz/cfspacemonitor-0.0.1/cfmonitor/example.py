import os
import sys
import time
import signal
from cfmonitor.space import AppConfig


class Example(object):
    def __init__(self):
        self.who_started = os.getenv('WHOSTARTED')
        self.config = AppConfig('example')
        self.logger = self.config.logger
        self.is_stopped = False

    def run(self):
        while not self.is_stopped:
            self.logger.debug('working for {0}...'.format(self.who_started))
            time.sleep(1)

    def start(self):
        self.config.log_starting()
        self.config.log_started()
        self.run()

    def stop(self):
        self.config.log_stopping()
        self.is_stopped = True
        self.config.log_stopped()


def main():
    app = Example()
    app.config.validate()

    def handler(*args):
        app.stop()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handler)

    app.start()


if '__main__' == __name__:
    main()
