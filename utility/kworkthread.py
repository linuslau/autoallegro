
from utility.klogger import *
from utility.kfile import *
import shutil
import datetime
import re
import pandas as pd
import numpy as np

from threading import Thread, Event
from queue import Queue
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDateTime, QObject

klogger = KLogger()
logger = klogger.getlog()

class KWorkThread(QThread):
    signal_to_ui = pyqtSignal(str, str, object)
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
            print('\n[working thread]...Waiting for new msg...\n')
            msg = self.queue.get()
            print('Receiving a new msg')
            print('=========================')
            print('content: ' + str(msg))

            if len(msg) == 2 or len(msg) == 3:
                print('msg id: ' + str(msg[0]))
                print('msg data: ' + str(msg[1]))
                if msg[0] == 0:
                    print('working thread handle msg: ' + str(msg[0]))
                    self.signal_to_ui.emit(str(msg[0]), 'signal_0', None)
                    print('emit signal back msg id: ' + str(msg[0]))

                if msg[0] == 1:
                    print('working thread handle msg: ' + str(msg[0]))
                    self.signal_to_ui.emit(str(msg[0]), 'signal_1', None)
                    print('emit signal back msg id: ' + str(msg[0]))

                if msg[0] == 2:
                    print('working thread handle msg: ' + str(msg[0]))

                    file_org = r'.\LNL+T4+2230+PCIe4+CNVio3.dcfx'
                    now = datetime.datetime.now()
                    current_time = now.strftime("%Y-%m-%d_%H-%M-%S")

                    file_mod = os.path.splitext(file_org)[0] + '_' + current_time + os.path.splitext(file_org)[1]

                    shutil.copy(file_org, file_mod)

                    rvp_cus = msg[1]

                    delete = [key for key in rvp_cus if key == '' or rvp_cus[key] == '']

                    for key in delete:
                        del rvp_cus[key]

                    checkWords = rvp_cus.keys()
                    repWords = rvp_cus.values()

                    kfile = KFile(file_mod)
                    case_sensitive = msg[2]
                    print('case_sensitive: ' + str(case_sensitive))
                    if case_sensitive:
                        print('case_sensitive, yes')
                        kfile.replace(checkWords, repWords, True)
                    else:
                        print('case_sensitive, no')
                        kfile.replace(checkWords, repWords)

                    self.signal_to_ui.emit(str(msg[0]), 'signal_2', None)
                    print('emit signal back msg id: ' + str(msg[0]))

                if msg[0] == 3:
                    print('working thread handle msg: ' + str(msg[0]))
                    df = pd.read_excel(r'LNL+T4+2230+PCIe4+CNVio3.xlsx', sheet_name='Netname list', header=1)
                    self.signal_to_ui.emit(str(msg[0]), 'signal_3', df)
                    print('emit signal back msg id: ' + str(msg[0]))

            self.queue.task_done()
            print('=========================')

