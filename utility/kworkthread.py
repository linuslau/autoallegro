
from utility.klogger import *

from threading import Thread, Event
from queue import Queue
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDateTime, QObject

klogger = KLogger()
logger = klogger.getlog()

class KWorkThread(QThread):
    signal_to_ui = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        self.queue = Queue()
        pass
    def __del__(self):
        pass
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def send_work_message(self,msg):
        self.queue.put(msg)

    def run(self):
        try:
            self._run()
        except Exception as e:
            logger.error('Exception: working thread got error!!!', exc_info=True)

    def _run(self):
        while True:
            print('\n...Waiting for new msg...\n')
            msg = self.queue.get()
            print('Receiving a new msg')
            print('=========================')
            print('content: ' + str(msg))

            if len(msg) == 2:
                print('msg id: ' + str(msg[0]))
                print('msg data: ' + str(msg[1]))
                if msg[0] == 0:
                    print('working thread handle msg: ' + str(msg[0]))
                    self.signal_to_ui.emit(str(msg[0]), 'signal_0')
                    print('emit signal back msg id: ' + str(msg[0]))

                if msg[0] == 1:
                    print('working thread handle msg: ' + str(msg[0]))
                    self.signal_to_ui.emit(str(msg[0]), 'signal_1')
                    print('emit signal back msg id: ' + str(msg[0]))

                if msg[0] == 2:
                    print('working thread handle msg: ' + str(msg[0]))
                    self.signal_to_ui.emit(str(msg[0]), 'signal_2')
                    print('emit signal back msg id: ' + str(msg[0]))

            self.queue.task_done()
            print('=========================')

