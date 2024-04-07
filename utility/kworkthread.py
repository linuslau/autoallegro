
from utility.klogger import *
from utility.kfile import *
import shutil
import datetime
import re
import pandas as pd
import numpy as np
import os.path
import configparser

from threading import Thread, Event
from queue import Queue
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QDateTime, QObject

klogger = KLogger()
logger = klogger.getlog()

class KWorkThread(QThread):
    signal_to_ui = pyqtSignal(str, str, object)
    signal_to_config_dialog = pyqtSignal(str,str)
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

            if len(msg) == 2 or len(msg) == 3 or len(msg) == 4:
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
                    try:
                        print('working thread handle msg: ' + str(msg[0]))

                        file_org = msg[3]
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

                        self.signal_to_ui.emit(str(msg[0]), 'signal_2', 1)
                        print('emit signal back msg id: ' + str(msg[0]))
                    except Exception as e:
                        print('Exception: ' + str(e))
                        self.signal_to_ui.emit(str(msg[0]), 'signal_2', 0)
                        print('emit signal back msg id: ' + str(msg[0]))

                if msg[0] == 3:
                    print('working thread handle msg: ' + str(msg[0]))

                    if os.path.exists(msg[1]):
                        try:
                            df = pd.read_excel(msg[1], sheet_name='Netname list', header=1)
                        except Exception as e:
                            print('Exception: ' + str(e))
                            df = pd.DataFrame()
                    else:
                        df = pd.DataFrame()
                        pass
                    self.signal_to_ui.emit(str(msg[0]), 'signal_3', df)
                    print('emit signal back msg id: ' + str(msg[0]))

                if msg[0] == 4:

                    ini_file = './config.ini'
                    xlsx_path = ''
                    dcfx_path = ''

                    if not os.path.exists(ini_file):
                        self.create_default_ini(ini_file)
                        print(f"Created {ini_file} with default configuration.")
                    else:
                        config = configparser.ConfigParser()
                        config.read("config.ini")

                        xlsx_path = config.get("file_path", "xlsx")
                        dcfx_path = config.get("file_path", "dcfx")

                    self.signal_to_config_dialog.emit(xlsx_path, dcfx_path)

                if msg[0] == 5:
                    ini_file = './config.ini'
                    xlsx_path = ''
                    dcfx_path = ''
                    xlsx_path = msg[1]
                    dcfx_path = msg[2]
                    self.write_to_ini(ini_file, xlsx_path, dcfx_path)
                    pass

            self.queue.task_done()
            print('=========================')

    def create_default_ini(self, file_path):
        config = configparser.ConfigParser()
        config['file_path'] = {
            'xlsx': '',
            'dcfx': ''
        }

        with open(file_path, 'w') as configfile:
            config.write(configfile)

    def write_to_ini(self, file_path, xlsx_value, dcfx_value):
        config = configparser.ConfigParser()
        config.read(file_path)

        # 写入新的值，如果已存在，则覆盖
        config.set('file_path', 'xlsx', xlsx_value)
        config.set('file_path', 'dcfx', dcfx_value)

        with open(file_path, 'w') as configfile:
            config.write(configfile)
