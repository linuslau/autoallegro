
from utility.klogger import *
from utility.kfile import *
from utility.kxlsx import *
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
logger = klogger.getlogger()

class KWorkThread(QThread):
    NetList_Table = r'Netlist comparision table.xlsx'
    signal_to_main_ui = pyqtSignal(str, str, object)
    sig_to_config_dialog = pyqtSignal(str, str, str)
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
        #import debugpy
        #debugpy.debug_this_thread()
        while True:
            logger.info('\n[working thread]...Waiting for new msg...\n')
            msg = self.queue.get()
            logger.info('Receiving a new msg')
            logger.info('=========================')
            logger.info('content: ' + str(msg))

            if len(msg) != 0:
                logger.info('msg id: ' + str(msg[0]))
                logger.info('msg data: ' + str(msg[1]))
                if msg[0] == 0:
                    logger.info('working thread handle msg: ' + str(msg[0]))
                    self.signal_to_main_ui.emit(str(msg[0]), 'signal_0', None)
                    logger.info('emit signal back msg id: ' + str(msg[0]))

                if msg[0] == 1:
                    logger.info('working thread handle msg: ' + str(msg[0]))
                    self.signal_to_main_ui.emit(str(msg[0]), 'signal_1', None)
                    logger.info('emit signal back msg id: ' + str(msg[0]))

                if msg[0] == 2:
                    try:
                        logger.info('working thread handle msg: ' + str(msg[0]))

                        file_org = msg[3]
                        now = datetime.datetime.now()
                        current_time = now.strftime("%Y-%m-%d_%H-%M-%S")

                        file_to_save = msg[4]
                        if file_to_save != '':
                            file_mod = file_to_save
                        else:
                            file_mod = os.path.splitext(file_org)[0] + '_' + current_time + os.path.splitext(file_org)[1]

                        if file_org != file_mod:
                            shutil.copy(file_org, file_mod)
                        else:
                            logger.info('file are the same, do not do copy')

                        rvp_cus = msg[1][0]
                        types = msg[1][1]

                        rvp_cus_replace = []
                        rvp_cus_g_5v = []
                        rvp_cus_l_5v = []

                        rvp_cus_g_5v_start_idx = types.index(1)
                        rvp_cus_l_5v_start_idx = types.index(2)

                        rvp_cus_replace = dict(list(rvp_cus.items())[:rvp_cus_g_5v_start_idx - 1])
                        rvp_cus_g_5v = dict(list(rvp_cus.items())[rvp_cus_g_5v_start_idx : rvp_cus_l_5v_start_idx - 1])
                        rvp_cus_l_5v = dict(list(rvp_cus.items())[rvp_cus_l_5v_start_idx : len(rvp_cus)])

                        delete = [key for key in rvp_cus_replace if key == '' or rvp_cus_replace[key] == '']
                        for key in delete:
                            del rvp_cus_replace[key]

                        delete = [key for key in rvp_cus_g_5v if key == '' or rvp_cus_g_5v[key] == '']
                        for key in delete:
                            del rvp_cus_g_5v[key]

                        delete = [key for key in rvp_cus_l_5v if key == '' or rvp_cus_l_5v[key] == '']
                        for key in delete:
                            del rvp_cus_l_5v[key]

                        checkWords = rvp_cus_replace.keys()
                        repWords = rvp_cus_replace.values()

                        kfile = KFile(file_mod)

                        case_sensitive = msg[2]
                        logger.info('case_sensitive: ' + str(case_sensitive))
                        if case_sensitive:
                            logger.info('case_sensitive, yes')
                            kfile.replace(checkWords, repWords, True)
                        else:
                            logger.info('case_sensitive, no')
                            kfile.replace(checkWords, repWords)

                        addWordsG5V = rvp_cus_g_5v.values()
                        addWordsL5V = rvp_cus_l_5v.values()
                        logger.info('>5V: %s', list(addWordsG5V))
                        logger.info('<5V: %s', list(addWordsL5V))
                        kfile.add_netnames_vs_5V(addWordsG5V, addWordsL5V)

                        self.signal_to_main_ui.emit(str(msg[0]), 'signal_2', 1)
                        logger.info('emit signal back msg id: ' + str(msg[0]))
                    except Exception as e:
                        logger.info('Exception: ' + str(e))
                        self.signal_to_main_ui.emit(str(msg[0]), 'signal_2', 0)
                        logger.info('emit signal back msg id: ' + str(msg[0]))

                if msg[0] == 3:
                    self.file_name = msg[1]
                    sheetNames = self.get_all_sheets(self.file_name)
                    # skip 1st sheet per requirement
                    sheetNames = sheetNames[1:]

                    self.signal_to_main_ui.emit(str(msg[0]), 'signal_3', sheetNames)

                if msg[0] == 4:
                    folder_path, xlsx_path, dcfx_path = self.get_folder_xlsx_dcfx_from_ini()
                    self.sig_to_config_dialog.emit(xlsx_path, dcfx_path, folder_path)

                if msg[0] == 5:
                    logger.info('msg = 5, call write_to_ini')
                    ini_file = './config.ini'
                    xlsx_path = msg[1]
                    dcfx_path = msg[2]
                    folder_path = msg[3]

                    self.write_to_ini(ini_file, xlsx_path, dcfx_path, folder_path)
                    pass

                if msg[0] == 6:
                    sheetName = msg[1]
                    df = self.get_sheet_df(self.file_name, sheetName)
                    self.signal_to_main_ui.emit(str(msg[0]), 'signal_6', df)

            self.queue.task_done()
            logger.info('=========================')

    def create_default_ini(self, file_path):
        logger.info('create_default_ini enter')
        config = configparser.ConfigParser()
        config['file_path'] = {
            'folder': '',
            'xlsx': '',
            'dcfx': ''
        }

        with open(file_path, 'w') as configfile:
            config.write(configfile)

        logger.info('create_default_ini exit')

    def write_to_ini(self, file_path, xlsx_value, dcfx_value, folder_path):
        logger.info('write_to_ini enter')
        config = configparser.ConfigParser()
        config.read(file_path)

        # 写入新的值，如果已存在，则覆盖
        config.set('file_path', 'folder', folder_path)
        config.set('file_path', 'xlsx', xlsx_value)
        config.set('file_path', 'dcfx', dcfx_value)

        with open(file_path, 'w') as configfile:
            config.write(configfile)
        logger.info('write_to_ini exit')

    def get_folder_xlsx_dcfx_from_ini(self):

        ini_file = './config.ini'
        folder_path = ''
        xlsx_path = ''
        dcfx_path = ''

        if not os.path.exists(ini_file):
            logger.info('config.ini exist no, create a new ini')
            self.create_default_ini(ini_file)
            logger.info(f"Created {ini_file} with default configuration.")
        else:
            logger.info('config.ini exist yes')
            config = configparser.ConfigParser()
            config.read("config.ini")

            folder_path = config.get("file_path", "folder")
            xlsx_path = config.get("file_path", "xlsx")
            dcfx_path = config.get("file_path", "dcfx")

        return folder_path, xlsx_path, dcfx_path

    def get_all_sheets(self, file):
        sheetnames = ''
        if os.path.exists(file):
            logger.info('xlsx exist yes')
            kxlsx = KXlsx(file)
            sheetnames = kxlsx.get_all_sheets('wb')
            pass
        else:
            logger.info('xlsx exist no')
            pass

        return sheetnames

    def get_sheet_df(self, file_name, sheetName):
        df = None
        if os.path.exists(file_name) and sheetName != '':
            logger.info('xlsx exist yes')
            try:
                #df = pd.read_excel(file_name, sheet_name=sheetName, header=1)
                df = pd.read_excel(file_name, sheet_name=sheetName)
                pd.set_option('display.max_columns', None)
                pd.set_option('display.width', None)
                logger.info(df)
                return df
            except Exception as e:
                logger.info('Exception: ' + str(e))
                df = pd.DataFrame()
                return df
        else:
            logger.info('xlsx exist no')
            df = pd.DataFrame()
            return df
            pass
