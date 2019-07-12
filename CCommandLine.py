import threading
import time


class CCommandLine():
    def __init__(self):
        self.cmd = ""
        self.done = True
        self.kill = False
        self.thread = threading.Thread(target=self.worker)
        self.thread.start()

    def worker(self):
        while not self.kill:
            self.cmd = input("> ")
            if not self.cmd:
                continue
            self.done = False
            while not self.done:
                time.sleep(0.1)
        print("CommandLine thread done")

    def close(self):
        self.kill = True
        self.done = True
        self.thread.join()

    def setDone(self):
        self.done = True

    def getDone(self):
        return self.done

    def getCommand(self):
        if self.done:
            return None
        else:
            return self.cmd
