import time
import threading


class CWatchdog(object):
    def __init__(self, trigger_cb, seconds):
        self.trigger_cb = trigger_cb
        self.seconds = seconds
        self.stopped = True
        self.init = True

    def start(self):
        if self.stopped or self.init:
            self.init = False
            self.time_last_reset = time.time()
            self.worker_kill = False
            self.stopped = False
            self.worker = threading.Thread(target=self.worker_func)
            self.worker.start()
        else:
            raise Exception('CWatchdog start(): was not stopped.')

    def worker_func(self):
        while not self.worker_kill:
            if time.time() - self.time_last_reset > self.seconds:
                self.trigger_cb()
                self.worker_kill = True
            else:
                time.sleep(1)

        print("CWatchdog thread done.")

    def reset(self):
        self.time_last_reset = time.time()

    def stop(self):
        self.worker_kill = True
        self.stopped = True
        self.worker.join()
