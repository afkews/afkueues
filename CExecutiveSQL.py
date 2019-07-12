import sqlite3
import threading
import time


class CExecutiveSQL():
    def __init__(self, database_file):
        self.verbose = False
        self.command_to_execute = ""
        self.command_is_done = threading.Event()
        self.thread_is_free = threading.Event()
        self.thread_is_free.set()
        self.connected = False
        self.database_file = database_file
        self.fetch = None
        self.kill = False
        self.rowcount = 0
        self.command_is_done.clear()
        self.thread_handler = threading.Thread(target=self.thread_sql)
        self.thread_handler.start()
        self.command_is_done.wait()

    def thread_sql(self):
        while not self.kill:
            if not self.command_is_done.isSet():
                if not self.connected:
                    if self.verbose:
                        print("Connecting database")
                    self.db = sqlite3.connect(self.database_file)
                    self.connected = True
                else:
                    if self.verbose:
                        print('SQL("%s")' % self.command_to_execute)
                    while True:
                        try:
                            self.cur = self.db.cursor().execute(self.command_to_execute)
                            self.rowcount = self.cur.rowcount
                            self.fetch = self.cur.fetchall()
                            self.db.commit()
                        except Exception as e:
                            print("HELP i'm stuck on SQL '%s'\n" % e)
                            time.sleep(0.2)
                            continue
                        break
                self.command_is_done.set()
            else:
                time.sleep(0.1)
        print("SQLite thread done")

    def execute(self, sql):
        self.thread_is_free.wait()
        self.thread_is_free.clear()
        self.command_to_execute = sql
        self.command_is_done.clear()
        self.command_is_done.wait()
        fetch = self.fetch
        self.thread_is_free.set()
        return fetch

    def stop(self):
        self.kill = True
        self.thread_handler.join()

    def setVerbose(self, is_on):
        self.verbose = is_on
