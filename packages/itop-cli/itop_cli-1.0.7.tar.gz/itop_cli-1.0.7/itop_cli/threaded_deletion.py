"""
Deletes object with threads
"""
from threading import Thread, Lock
from uuid import uuid4

from itop_cli.safe_delete import SafeDelete

from .find import find


class ThreadDelete(Thread):
    """
    Deletes object with threads
    """

    lock = Lock()
    cursors = {}

    def __init__(self, itop, class_name, elements, operation_uuid):
        Thread.__init__(self)
        self.itop = itop
        self.class_name = class_name
        self.instance = SafeDelete(itop, class_name)
        self.operation_uuid = operation_uuid
        self.elements = elements
        self.uuid = uuid4()

    def run(self):
        ThreadDelete.lock.acquire()
        if self.operation_uuid not in ThreadDelete.cursors:
            ThreadDelete.cursors[self.operation_uuid] = 0
        i = ThreadDelete.cursors[self.operation_uuid]
        ThreadDelete.cursors[self.operation_uuid] += 1
        ThreadDelete.lock.release()
        items = self.elements
        while i < len(items):
            object_ = items[i][1]
            self.instance.delete(object_)
            ThreadDelete.lock.acquire()
            ThreadDelete.cursors[self.operation_uuid] += 1
            i = ThreadDelete.cursors[self.operation_uuid]
            ThreadDelete.lock.release()


class ThreadedDeletion():
    """
    Utility to launch deletetions with threads
    """
    nb_threads = 4

    def __init__(self, itop, class_name, query):
        self.itop = itop
        self.class_name = class_name
        self.instance = SafeDelete(itop, class_name, query)
        self.uuid = uuid4()
        self.query = query
        self.threads = []

    def run(self):
        """
        Launches threads
        :return: None
        """
        elements = find(self.itop, self.class_name, self.query)
        if elements is None:
            raise RuntimeError("Nothing to do !")
        for i in range(0, ThreadedDeletion.nb_threads):
            self.threads.append(ThreadDelete(self.itop, self.class_name, elements, self.uuid))
        for thread in self.threads:
            thread.start()
        for thread in self.threads:
            thread.join()
        SafeDelete.elements = []

def delete(itop, class_name, query):
    ThreadedDeletion(itop, class_name, query).run()
