import os.path

from PyQt5.QtGui import QPixmap

from about_ui_qt5 import *
import config_ui_qt5 as cfg_ui_dialog
from utility.software_mgr import *
from utility.kworkthread import *
from utility.kmisc import *
from PyQt5.QtCore import QEvent

import pandas as pd
import numpy as np

class KAppBase(object):
    NetList_Table = r'Netlist comparision table.xlsx'
    def __init__(self, ui, MainWindow, app):
        self.ui = ui
        self.main_window = MainWindow
        self.app = app
        #self.splash_check()

        self.main_window.setWindowTitle('NetlistAutoMapper v0.3.1')

        self.kwork_thread = KWorkThread()
        self.kwork_thread.start()
        self.kwork_thread.signal_to_main_ui.connect(self.work_thread_signal_handler)

        self.ui_mgr = UI_Mgr(MainWindow)
        #self.ui_mgr.splash_check()
        self.software_mgr = Software_Mgr('NetlistAutoMapper', 'NetlistAutoMapper', MainWindow)
        self.software_mgr.check_software_version_background(self.ui_mgr)
        self.table_mgr = Table_Mgr(self)
        self.config_dialog_mgr = Config_Dialog_Mgr(self)
        self.button_mgr = Button_Mgr(self)
        self.icon_mgr = Icon_Mgr(ui, MainWindow)
        self.about_dialog_mgr = about_dialog_mgr(ui)

        self.config_dialog_mgr.sig_cfg_ui_2_main_ui.connect(self.config_dialog_sig_handler)

        self.ui.actionTool_Log.triggered['bool'].connect(self.open_log_folder)
        self.app.aboutToQuit.connect(self.closeApplication)

        pass

    def closeApplication(self):
        # 在程序关闭时执行的操作
        self.kwork_thread.send_work_message([8, self.table_mgr.multiArray, self.config_dialog_mgr.folder_path, self.currentSheetName])

        elapsed_time = 0
        start_time = time.time()
        while not self.kwork_thread.finished:
            elapsed_time = time.time() - start_time
            logger.info('elapsed_time: %f', elapsed_time)
            if elapsed_time >= 1:
                print("Timeout reached. close app.")
                break
            time.sleep(0.1)  # 等待一段时间后再检查

        logger.info('final elapsed_time: %f', elapsed_time)

        # 在这里添加你想要执行的操作，例如保存数据、清理资源等
        self.app.quit()

    def __del__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def config_dialog_sig_handler(self, param_1):
        logger.info('[main thread] main windows received child signal ' + param_1)
        xlsx_path = param_1
        logger.info('xlsx_path: ' + xlsx_path)
        self.kwork_thread.send_work_message([3, xlsx_path])

    def open_log_folder(self):
        logger.info(KLogger.debug_log_path_full)
        cmd = 'explorer /select,' + KLogger.debug_log_path_full
        os.system(cmd)

    def work_thread_signal_handler(self, param_1, param_2, param_3):

        logger.info('[main thread] ui slots received signal id: ' + param_1)
        logger.info('[main thread] ui slots received signal data: ' + param_2)

        self.id = param_1
        self.data = param_2
        self.data2 = param_3

        status_bar_string = self.data

        status_bar_string = ' ui enqueue->thread dequeue, emit->ui slots get ' + status_bar_string

        # self.main_window.statusBar().showMessage(status_bar_string, 10000)

        if self.id == '0':
            pass
        if self.id == '1':
            pass
        if self.id == '2':
            logger.info('handle complete')
            self.ui.pushButton.setEnabled(True)
            self.ui.pushButton_2.setEnabled(True)
            self.ui.pushButton_2.setText('Generate')
            self.ui.pushButton_2.setStyleSheet("color: black")
            self.main_window.statusBar().showMessage('')

            if str(self.data2) == '0':
                QMessageBox.information(self.main_window, 'Warning', 'Invalid dcfx format, please select correct dcfx')
                self.config_dialog_mgr.exec()
                return

            elif str(self.data2) == '2':
                QMessageBox.information(self.main_window, 'Warning', self.table_mgr.dcfx_path + ' is not available.\nPlease check configuration folder')
                self.config_dialog_mgr.exec()
                return

            else:
                self.main_window.statusBar().showMessage('New file generated successfully.', 10000)

        if self.id == '3':

            sheetNames = self.data2
            self.ui.comboBox_3.clear()
            for name in sheetNames:
                self.ui.comboBox_3.addItem(name)

            #self.table_mgr.set_signal_connect()

            if len(sheetNames) > 1:
                self.currentSheetName = sheetNames[0]
            else:
                self.currentSheetName = ''
                # Pending fix
                #QMessageBox.information(self.main_window, 'Warning', 'Invalid xlsx format, please select correct xlsx')
                #self.config_dialog_mgr.exec()

            self.kwork_thread.send_work_message([6, self.currentSheetName])

            pass

        if self.id == '6':
            # update table with Excel content
            df = self.data2
            self.table_mgr.df = df
            self.table_mgr.init_table_default()
            #self.table_mgr.init_table_reference()

            self.kwork_thread.send_work_message([7, self.config_dialog_mgr.folder_path, self.currentSheetName])
            pass

        if self.id == '7':
            self.multiArray = self.data2
            self.update_cus_col()
            pass

    def update_cus_col(self):
        for row_idx, row in enumerate(self.multiArray):
            try:
                col_3_value = row[2]
                col_5_value = row[4]

                # 在表格中插入内容
                self.ui.tableWidget.setItem(row_idx, 2, QTableWidgetItem(col_3_value))
                self.ui.tableWidget.setItem(row_idx, 4, QTableWidgetItem(col_5_value))

            except Exception as e:
                logger.error('pyi_splash close error', exc_info=True)
                pass

    def splash_check(self):
        # splash support close pic start
        import importlib
        if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
            try:
                import pyi_splash
                # no idea why this text is not displayed, check it if free time slot
                pyi_splash.update_text('UI Loaded ...')
                pyi_splash.close()
            except Exception as e:
                logger.error('pyi_splash close error', exc_info=True)

class UI_Mgr:
    def __init__(self, main_window):
        self.main_window = main_window
        # self.main_window.statusBar().showMessage("https://vmio.vip")
        # creating a label widget
        self.label_in_status_bar = QLabel("Label Status Bar")
        self.label_in_status_bar.setText("<A href='https://NetlistAutoMapper.html'>https://NetlistAutoMapper.html</a>")
        self.label_in_status_bar.setOpenExternalLinks(True)
        # adding label to status bar
        self.main_window.statusBar().addPermanentWidget(self.label_in_status_bar)

    def splash_check(self):
        # splash support close pic start
        import importlib
        if '_PYIBoot_SPLASH' in os.environ and importlib.util.find_spec("pyi_splash"):
            try:
                import pyi_splash
                # no idea why this text is not displayed, check it if free time slot
                pyi_splash.update_text('UI Loaded ...')
                pyi_splash.close()
            except Exception as e:
                logger.error('pyi_splash close error', exc_info=True)
        # splash support close pic end

class Button_Mgr:
    def __init__(self, kappbase):
        self.kappbase = kappbase
        self.ui = kappbase.ui
        self.main_window = kappbase.main_window
        self.kwork_thread = kappbase.kwork_thread
        self.config_dialog_mgr = kappbase.config_dialog_mgr
        self.table_mgr = kappbase.table_mgr
        self.set_signal_connect()
        #self.ui.pushButton.setEnabled(False)

    def set_signal_connect(self):
        self.ui.pushButton.clicked.connect(lambda: self.on_button_clicked_read(255, 255, 255))
        self.ui.pushButton_2.clicked.connect(lambda: self.on_button_clicked_modifier(255, 255, 255))
        pass

    def on_button_clicked_read(self, a, b, c):
        function_enter()
        #self.kwork_thread.send_work_message([1, 'data_1'])
        function_exit()
        self.config_dialog_mgr.exec()
        pass

    def save_dcfx_file(self):
        file_dialog_saved_file_path = QFileDialog.getSaveFileName(None, 'Save File', '', 'DCFX files(*.dcfx)')
        print('saved file dialog file: ' + str(file_dialog_saved_file_path[0]))
        saved_file_path = file_dialog_saved_file_path[0]
        print('saved file (selected): ' + str(saved_file_path))

        if len(saved_file_path) == 0:
            print('No saved file is selected, do nothing \n')
            return ""
        else:
            print('loaded_profile_ini_config is Not None')
            return saved_file_path

    def on_button_clicked_modifier(self, a, b, c):

        orig_file_path = ''
        saved_file_path = self.save_dcfx_file()
        if saved_file_path == '':
            logger.info('cancelled, do nothing, return')
            return

        if not self.config_dialog_mgr.child.checkBox_3.isChecked():
            orig_file_name = self.table_mgr.dcfx_path + '.dcfx'
            folder_path = self.config_dialog_mgr.child.plainTextEdit_3.toPlainText()
            if folder_path == '':
                orig_file_path = os.path.join(os.getcwd(), orig_file_name)
            else:
                orig_file_path = os.path.join(folder_path + '/', orig_file_name)
            pass

        else:
            if not self.config_dialog_mgr.dcfx_path or not self.config_dialog_mgr.xlsx_path:
                logger.info('dcfx or xlsx is null')
                if not self.config_dialog_mgr.dcfx_path and not self.config_dialog_mgr.xlsx_path:
                    QMessageBox.information(self.main_window, 'Warning', 'Please configure xlsx/dcfx path.')
                elif not self.config_dialog_mgr.dcfx_path:
                    QMessageBox.information(self.main_window, 'Warning','Please configure dcfx path.')
                elif not self.config_dialog_mgr.xlsx_path:
                    QMessageBox.information(self.main_window, 'Warning','Please configure xlsx path.')
                self.config_dialog_mgr.exec()
                pass
            else:
                orig_file_path = self.config_dialog_mgr.dcfx_path

        if self.table_mgr.df is None:
            logger.info('df is none')
            return
        if self.table_mgr.df.empty:
            QMessageBox.information(self.main_window, 'Warning', 'Invalid xlsx format, please select correct xlsx')
            self.config_dialog_mgr.exec()
            return
        rvp_cus = {}
        type = []
        type_add = 0
        for row in range(self.ui.tableWidget.rowCount()):
            #if row == 0:
            #    continue
            v_header = self.ui.tableWidget.item(row, 0).text()
            print('v_header ' + str(row) + ' :' + v_header)

            for col in range(self.ui.tableWidget.columnCount()):
                value = self.ui.tableWidget.item(row, col).text()
                if col == 1 or col == 3:
                    rvp = self.ui.tableWidget.item(row, col).text()
                    cus = self.ui.tableWidget.item(row,col + 1).text()
                    if (rvp not in rvp_cus) and (rvp != '' or cus != ''):
                        if ('High power rails' in v_header) or (v_header == '' and type_add == 1):
                            type.append(1)
                            type_add = 1
                        elif ('Low power rails' in v_header) or (v_header == '' and type_add == 2):
                            type.append(2)
                            type_add = 2
                        else:
                            type.append(0)
                        rvp_cus[rvp] = cus

                    pass
                #logger.info('row:' + str(row) + ',  col:' + str(col) + '\n' + value)

        for idx, (key, value) in enumerate(rvp_cus.items()):
            print(key, ': ', value, type[idx])

        case_sensitive = self.ui.checkBox.isChecked()
        logger.info('case_sensitive: ' + str(case_sensitive))
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_2.setText('Processing...')
        self.main_window.statusBar().showMessage('Processing...', 10000)
        self.ui.pushButton_2.setStyleSheet("color: red")

        self.kwork_thread.send_work_message([2, [rvp_cus, type], case_sensitive, orig_file_path, saved_file_path])

        pass


class Config_Dialog_Mgr(QDialog):
    xlsx_path = ''
    dcfx_path = ''
    xlsx_path_old = ''
    dcfx_path_old = ''
    folder_path = ''
    folder_path_old = ''
    sig_cfg_ui_2_main_ui = pyqtSignal(str)
    def __init__(self, kappbase):
        QDialog.__init__(self)
        self.kappbase = kappbase
        self.kwork_thread = kappbase.kwork_thread
        self.ui = kappbase.ui
        self.table_mgr = kappbase.table_mgr
        self.child=cfg_ui_dialog.Ui_Dialog()#子窗口的实例化
        self.child.setupUi(self)
        self.setWindowTitle('Configure')
        #self.child.label.setText("NetlistAutoMapper (v0.2.1, Build 1)")

        self.ui.actionConfigure.triggered['bool'].connect(self.exec)
        self.child.buttonBox.accepted.connect(self.ok_pressed)
        self.child.buttonBox.rejected.connect(self.cancel_pressed)
        self.child.pushButton.clicked.connect(self.pushButton_on_click)
        self.child.pushButton_2.clicked.connect(self.pushButton_2_on_click)
        self.child.pushButton_3.clicked.connect(self.pushButton_3_on_click)

        self.child.checkBox_3.stateChanged.connect(self.checkBox_3_stateChanged)
        # Disabled first, improve it in the future.
        self.child.checkBox_3.setEnabled(False)

        self.child.pushButton.setEnabled(False)
        self.child.pushButton_2.setEnabled(False)

        self.child.plainTextEdit.setEnabled(False)
        self.child.plainTextEdit_2.setEnabled(False)
        self.child.plainTextEdit.setReadOnly(True)
        self.child.plainTextEdit_2.setReadOnly(True)
        # self.child.plainTextEdit_3.setReadOnly(True)
        self.child.checkBox.setVisible(False)
        self.child.checkBox_2.setVisible(False)

        self.kwork_thread.sig_to_config_dialog.connect(self.config_dialog_signal_handler)
        # startup, auto load and check ini
        self.kwork_thread.send_work_message([4, 'data_4'])

    def checkBox_3_stateChanged(self):
        if self.child.checkBox_3.isChecked():
            self.child.plainTextEdit.setEnabled(True)
            self.child.pushButton.setEnabled(True)

            self.child.plainTextEdit_2.setEnabled(True)
            self.child.pushButton_2.setEnabled(True)

            self.child.plainTextEdit_3.setEnabled(False)
            self.child.pushButton_3.setEnabled(False)
            pass
        else:
            self.child.plainTextEdit.setEnabled(False)
            self.child.pushButton.setEnabled(False)

            self.child.plainTextEdit_2.setEnabled(False)
            self.child.pushButton_2.setEnabled(False)

            self.child.plainTextEdit_3.setEnabled(True)
            self.child.pushButton_3.setEnabled(True)
            pass

    def event(self, event):
        #logger.info('SubWindow got event type: '+ str(event.type()))
        if event.type() == QEvent.Show:
            logger.info("child dialog is shown!")
        return super().event(event)

    def config_dialog_signal_handler(self, param_1, param_2, param_3):
        logger.info('config_dialog_signal_handler: \n' + param_1 + '\n' + param_2 + '\n' + param_3)
        self.xlsx_path = self.xlsx_path_old = param_1
        self.dcfx_path = self.dcfx_path_old = param_2
        self.folder_path = self.folder_path_old = param_3
        self.child.plainTextEdit.setPlainText(param_1)
        self.child.plainTextEdit_2.setPlainText(param_2)
        self.child.plainTextEdit_3.setPlainText(param_3)

        if self.folder_path == '':
            logger.info("folder path is empty in ini, check local dir")
            if os.path.exists(self.kappbase.NetList_Table):
                logger.info("folder path is empty in ini, table file is present")
                xlsx_path = os.path.join(os.getcwd(), self.kappbase.NetList_Table)
            else:
                logger.info("folder path is empty in ini, table file is NOT present")
                QMessageBox.information(self.kappbase.main_window, 'Warning', 'Netlist comparision table.xlsx not found')
                self.kappbase.config_dialog_mgr.exec()
                return
        else:
            xlsx_path = os.path.join(self.folder_path + '/', self.kappbase.NetList_Table)

        if os.path.exists(xlsx_path):
            logger.info("load xlsx")
            self.kwork_thread.send_work_message([3, xlsx_path])
        else:
            QMessageBox.information(self.kappbase.main_window, 'Warning', 'Netlist comparision table.xlsx not found.\nPlease check configuration folder.')
            self.kappbase.config_dialog_mgr.exec()
            logger.info('configured xlsx path does not exist')
        pass

    def cancel_pressed(self):
        logger.info('cancel_pressed')
        if self.xlsx_path_old != self.child.plainTextEdit.toPlainText():
            self.child.plainTextEdit.setPlainText(self.xlsx_path_old)
        if self.dcfx_path_old != self.child.plainTextEdit_2.toPlainText():
            self.child.plainTextEdit_2.setPlainText(self.dcfx_path_old)
        if self.folder_path_old != self.child.plainTextEdit_3.toPlainText():
            self.child.plainTextEdit_3.setPlainText(self.folder_path_old)
        pass
    def ok_pressed(self):

        # if folder is set to empty, Excel also should be reset to empty
        if self.folder_path == '':
            self.child.plainTextEdit.setPlainText('')

        self.xlsx_path = self.xlsx_path_old = self.child.plainTextEdit.toPlainText()
        self.dcfx_path = self.dcfx_path_old = self.child.plainTextEdit_2.toPlainText()
        self.folder_path = self.folder_path_old = self.child.plainTextEdit_3.toPlainText()

        if self.folder_path == '':
            new_xlsx_path = self.kappbase.NetList_Table
        else:
            new_xlsx_path = os.path.join(self.folder_path + '/' + self.kappbase.NetList_Table)

        if os.path.exists(new_xlsx_path):
            self.sig_cfg_ui_2_main_ui.emit(new_xlsx_path)
        else:
            QMessageBox.information(self.kappbase.main_window, 'Warning', 'Netlist comparision table.xlsx not found')
            # Won't take effect, as it is in OK_pressed handler.
            # self.kappbase.config_dialog_mgr.exec()
            self.sig_cfg_ui_2_main_ui.emit('')

        # save to ini
        if self.child.checkBox_3.isChecked():
            self.kwork_thread.send_work_message([5, self.xlsx_path, self.dcfx_path, self.folder_path])
        else:
            self.kwork_thread.send_work_message([5, '', '', self.folder_path])
        pass
        '''
        if self.xlsx_path:
            self.sig_cfg_ui_2_main_ui.emit(self.xlsx_path)
        else:
            logger.info('ok button: xlsx_path is null')
        if self.dcfx_path:
            self.kwork_thread.send_work_message([5, self.xlsx_path, self.dcfx_path])
        else:
            logger.info('ok button: dcfx_path is null')
        '''
    def pushButton_on_click(self):
        logger.info('pushButton_on_click')
        #self.dcfx_path = self.child.plainTextEdit_2.toPlainText()
        self.load_xlsx_file()

    def pushButton_2_on_click(self):
        logger.info('pushButton_2_on_click')
        self.load_dcfx_file()

    def pushButton_3_on_click(self):
        logger.info('pushButton_3_on_click')
        self.load_xlsx_folder()

    def load_dcfx_file(self):
        opened_file_path = ''
        file_dialog_opened_file_path = QFileDialog.getOpenFileName(None, 'Select File', '', "DCFX Files (*.dcfx);;All files (*.*)")
        logger.info('opened file dialog file: ' + str(file_dialog_opened_file_path[0]))
        opened_file_path = file_dialog_opened_file_path[0]
        self.dcfx_path = opened_file_path
        logger.info('opened file: ' + str(opened_file_path))

        if len(opened_file_path) == 0:
            logger.info('No file is selected, do nothing \n')
            return
        else:
            self.child.plainTextEdit_2.setPlainText(opened_file_path)

            pass
            last_profile_name = opened_file_path
            # LoadProfile(opened_file_path)
            # load_ini_profile(opened_file_path, 'menu')
    def load_xlsx_file(self):
        opened_file_path = ''
        file_dialog_opened_file_path = QFileDialog.getOpenFileName(None, 'Select File', '', "Excel Files (*.xlsx *.xls);;All files (*.*)")
        logger.info('opened file dialog file: ' + str(file_dialog_opened_file_path[0]))
        opened_file_path = file_dialog_opened_file_path[0]
        self.xlsx_path = opened_file_path
        logger.info('opened file: ' + str(opened_file_path))

        if len(opened_file_path) == 0:
            logger.info('No file is selected, do nothing \n')
            return
        else:
            self.child.plainTextEdit.setPlainText(opened_file_path)

            pass
            last_profile_name = opened_file_path
            # LoadProfile(opened_file_path)
            # load_ini_profile(opened_file_path, 'menu')

    def load_xlsx_folder(self):
        self.folder_path = QFileDialog.getExistingDirectory(None, 'Select Folder')
        logger.info('opened file dialog folder: ' + self.folder_path)
        self.xlsx_path = os.path.join(self.folder_path + '/', self.kappbase.NetList_Table)

        if len(self.folder_path) == 0:
            logger.info('No Folder is selected, do nothing \n')
            return
        else:
            self.child.plainTextEdit_3.setPlainText(self.folder_path)
            self.child.plainTextEdit.setPlainText(self.xlsx_path)

        pass

class about_dialog_mgr(QDialog):
    def __init__(self, ui):
        QDialog.__init__(self)
        self.ui = ui
        self.child=Ui_Dialog()#子窗口的实例化
        self.child.setupUi(self)
        self.setWindowTitle('About NetlistAutoMapper')
        self.child.label.setText("NetlistAutoMapper (v0.3.1, Build 1)")
        self.child.label_2.setText("liukezhao@gmail.com")
        self.child.label_3.setText("<A href='https://NetlistAutoMapper.html'>https://NetlistAutoMapper.html</a>")
        self.child.label_3.setOpenExternalLinks(True)
        self.child.label_3.setToolTip("https:/NetlistAutoMapper.html")

        filename_about_icon = resource_path(os.path.join("icon", "logo_about.png"))
        pixmap = QPixmap(filename_about_icon)
        self.child.label_4.setPixmap(pixmap)  # 在label上显示图片
        self.child.label_4.setScaledContents (True)  # 让图片自适应label大小

        self.ui.actionAbout.triggered['bool'].connect(self.show)
        self.child.buttonBox.accepted.connect(self.accept)
class Icon_Mgr:
    def __init__(self, ui, main_window):
        self.ui = ui
        self.main_window = main_window
        self.ui_init_icon()

    def ui_init_icon(self):
        filename_main_icon = resource_path(os.path.join("icon", "logo_main.png"))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(filename_main_icon), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.main_window.setWindowIcon(icon)

        '''
        rw_logo_icon = resource_path(os.path.join("icon", "rw_logo.png"))
        pixmap = QPixmap(rw_logo_icon)
        self.ui.label_logo_rw.setPixmap(pixmap)  # 在label上显示图片
        self.ui.label_logo_rw.setScaledContents (True)  # 让图片自适应label大小
        '''


class Table_Mgr:
    def __init__(self, kappbase):
        self.kappbase = kappbase
        self.ui = kappbase.ui
        self.main_window = kappbase.main_window
        self.kwork_thread = kappbase.kwork_thread
        self.df = None

        self.dcfx_path = ''

        self.ignoreOnce = True

        self.combobox_set_signal_connect()
        self.multiArray = []

        #self.init_table()
        #self.test_excel()

        #self.init_table_default()
        #self.kwork_thread.send_work_message([3, 'data_3'])
        self.ui.tableWidget.itemChanged.connect(self.itemChanged)

    def itemChanged(self, item):
        row = item.row()
        column = item.column()

        #print('changed row: ' + str(row))
        #print('changed column: ' + str(column))

        # 确保多维数组的大小和 TableWidget 一致
        '''
        if row >= len(self.multiArray):
            self.multiArray.append([""] * self.ui.tableWidget.columnCount())
        elif column >= len(self.multiArray[row]):
            self.multiArray[row].extend([""] * (column - len(self.ui.multiArray[row]) + 1))
        '''

        # 获取修改后的值
        new_value = item.text()
        new_value = new_value.replace("\n", "")

        # 更新多维数组中对应位置的值
        self.multiArray[row][column] = new_value
        # print("Multi-dimensional Array after change:", self.multiArray)

    def combobox_set_signal_connect(self):
        self.ui.comboBox_3.currentIndexChanged.connect(self.combobox_selectionChange)
    def combobox_selectionChange(self, i):

        #打印被选中下拉框的内容
        print('current index', i, 'selection changed', self.ui.comboBox_3.currentText())
        self.dcfx_path = self.ui.comboBox_3.currentText()
        self.kappbase.currentSheetName = self.ui.comboBox_3.currentText()
        if self.ignoreOnce != True:
            self.kwork_thread.send_work_message([8, self.kappbase.table_mgr.multiArray, self.kappbase.config_dialog_mgr.folder_path, self.lastSheetName])
            self.kappbase.table_mgr.multiArray = []
            self.kwork_thread.send_work_message([6, self.dcfx_path])
        else:
            self.ignoreOnce = False
        pass

        self.lastSheetName = self.kappbase.currentSheetName

    def init_table(self):
        nRows = 10
        nColumns = 3
        self.ui.tableWidget.setRowCount(nRows)
        self.ui.tableWidget.setColumnCount(nColumns)

        self.ui.tableWidget.setHorizontalHeaderLabels(['Catalogue (LNL RVP)', 'Net name (LNL RVP)', 'Net name (Customization)'])

        for row in range(self.ui.tableWidget.rowCount()):
            for col in range(self.ui.tableWidget.columnCount()):
                if col == 2:
                    continue
                item = QTableWidgetItem(str('M.2_Bt_Usb2_R_Dpx39'))
                self.ui.tableWidget.setItem(row, col, item)

        self.ui.tableWidget.setSpan(1,0,5,1)

        self.ui.tableWidget.resizeColumnsToContents()

        self.df1 = pd.read_excel(r'c:\00_MyWorkspace\002_Documents\CNV\CNVi\Allegro\sample-1.xlsx', sheet_name=0)
        self.df2 = pd.read_excel(r'c:\00_MyWorkspace\002_Documents\CNV\CNVi\Allegro\sample-4.xlsx', sheet_name=0)

        pass

    # This is a good reference, it will show original table without any change.
    def init_table_reference(self, selected_columns=[]):

        nRows = len(self.df.index)
        nColumns = len(selected_columns) or len(self.df.columns)
        self.ui.tableWidget.setRowCount(nRows)
        self.ui.tableWidget.setColumnCount(nColumns)

        # Display an empty table
        if self.df.empty:
            self.ui.tableWidget.clearContents()
            return

        self.ui.tableWidget.setHorizontalHeaderLabels(selected_columns or self.df.columns)
        self.ui.tableWidget.setVerticalHeaderLabels(self.df.index.astype(str))

        for row in range(self.ui.tableWidget.rowCount()):
            for col in range(self.ui.tableWidget.columnCount()):
                item = QTableWidgetItem(str(self.df.iat[row, col]))
                self.ui.tableWidget.setItem(row, col, item)
        # Enable sorting on the table
        self.ui.tableWidget.setSortingEnabled(True)
        # Enable column moving by drag and drop
        self.ui.tableWidget.horizontalHeader().setSectionsMovable(True)

    def init_table_default(self, selected_columns=[]):
        #self.df = pd.read_excel(r'LNL+T4+2230+PCIe4+CNVio3.xlsx', sheet_name='Netname list', header=1)
        logger.info('init_table_default enter')
        # Display an empty table
        if self.df.empty:
            logger.info('self.df.empty, return')
            #self.ui.tableWidget.clearContents()
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.horizontalHeader().setVisible(False)
            return
        else:
            self.ui.tableWidget.horizontalHeader().setVisible(True)

        # does not work this way
        #self.ui.tableWidget.horizontalHeader().setStyleSheet("background-color: blue")
        #self.ui.tableWidget.verticalHeader().setStyleSheet("background-color: brown")

        stylesheet = "::section{Background-color:rgb(120,225,255)}"
        self.ui.tableWidget.horizontalHeader().setStyleSheet(stylesheet)

        self.ui.tableWidget.clearContents()

        #self.df = self.df.drop(self.df.columns[0], axis=1)
        nRows = len(self.df.index)
        nColumns = len(selected_columns) or len(self.df.columns)

        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        logger.info(self.df)

        columns = selected_columns or self.df.columns.values

        delCols = []
        for col in range(nColumns):
            if col == 0:
                continue
            item_str = columns[col]
            if 'Net Names on RVP' not in item_str and 'Net Names on customer design' not in item_str:
                delCols.append(col)

        for idx, col in enumerate(delCols):
            self.df = self.df.drop(self.df.columns[col - idx], axis=1)

        logger.info(self.df)

        self.ui.tableWidget.setRowCount(nRows)
        # self.ui.tableWidget.setColumnCount(nColumns)
        self.ui.tableWidget.setColumnCount(5)

        columns = selected_columns or self.df.columns.values

        for idx, col in enumerate(columns):
            logger.info(col)
            if 'Unnamed' in col:
                columns[idx] = ''

        col_catalogue = int(np.where(columns == 'Catalogue')[0])

        self.ui.tableWidget.setHorizontalHeaderLabels(selected_columns or columns)
        self.ui.tableWidget.setVerticalHeaderLabels(self.df.index.astype(str))

        span_row_cnt = 1
        start_row = 1

        t1 = self.ui.tableWidget.columnCount()
        t2 = self.ui.tableWidget.rowCount()

        self.multiArray = [[None] * t1 for _ in range(t2)]

        for row in range(self.ui.tableWidget.rowCount()):
            for col in range(self.ui.tableWidget.columnCount()):
                item_str = str(self.df.iat[row, col])
                if item_str == "nan":
                    item_str = ""

                if col == col_catalogue:
                    if item_str != "":
                        start_row = row
                        span_row_cnt = 1
                    else:
                        span_row_cnt += 1
                        self.ui.tableWidget.setSpan(start_row, col_catalogue, span_row_cnt, 1)

                item = QTableWidgetItem(item_str)
                if col == 0 or col == 1 or col == 3:
                    # also work
                    # item = QTableWidgetItem(item_str, flags=Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                self.ui.tableWidget.setItem(row, col, item)
                if col == 0:
                    self.ui.tableWidget.item(row, col).setBackground(QtGui.QColor(235, 235, 150))

        # Enable sorting on the table
        # self.ui.tableWidget.setSortingEnabled(True)
        # Enable column moving by drag and drop
        # self.ui.tableWidget.horizontalHeader().setSectionsMovable(True)

        self.ui.tableWidget.resizeColumnsToContents()
        logger.info('auto load complete')
        logger.info('init_table_default exit')

    def test_excel(self):
        import openpyxl

        # 读取XLSX文件
        workbook = openpyxl.load_workbook(r'c:\00_MyWorkspace\002_Documents\CNV\CNVi\Allegro\sample-1.xlsx')
        sheet = workbook.active

        workbook2 = openpyxl.load_workbook(r'c:\00_MyWorkspace\002_Documents\CNV\CNVi\Allegro\sample-3.xlsx')

        # 获取单元格的值
        cell_value = sheet['A1'].value
        pass
