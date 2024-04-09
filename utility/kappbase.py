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
    pass
    def __init__(self, ui, MainWindow):
        self.ui = ui
        self.mainwindow = MainWindow
        self.splash_check()

        self.mainwindow.setWindowTitle('AutoAllegro v0.2')

        self.kwork_thread = KWorkThread()
        self.kwork_thread.start()
        self.kwork_thread.signal_to_ui.connect(self.work_thread_signal_handler)

        self.ui_mgr = UI_Mgr(MainWindow)
        self.ui_mgr.splash_check()
        self.software_mgr = Software_Mgr('autoallegro', 'AutoAllegro', MainWindow)
        self.software_mgr.check_software_version_background(self.ui_mgr)
        self.table_mgr = Table_Mgr(ui, MainWindow, self.kwork_thread)
        self.config_dialog_mgr = Config_Dialog_Mgr(ui, self.kwork_thread, self.table_mgr)
        self.button_mgr = Button_Mgr(ui, MainWindow, self.kwork_thread, self.config_dialog_mgr, self.table_mgr)
        self.icon_mgr = Icon_Mgr(ui, MainWindow)
        self.about_dialog_mgr = about_dialog_mgr(ui)
        self.config_dialog_mgr.signal_child_2_parent.connect(self.child_message_handler)

        pass

    def __del__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def child_message_handler(self, param_1):
        logger.info('[main thread] main windows received child signal ' + param_1)
        xlsx_path = param_1
        logger.info('xlsx_path: ' + xlsx_path)
        self.kwork_thread.send_work_message([3, xlsx_path])
    def work_thread_signal_handler(self, param_1, param_2, param_3):

        logger.info('[main thread] ui slots received signal id: ' + param_1)
        logger.info('[main thread] ui slots received signal data: ' + param_2)

        self.id = param_1
        self.data = param_2
        self.data2 = param_3

        status_bar_string = self.data

        status_bar_string = ' ui enqueue->thread dequeue, emit->ui slots get ' + status_bar_string

        self.mainwindow.statusBar().showMessage(status_bar_string, 10000)

        if self.id == '0':
            pass
        if self.id == '1':
            pass
        if self.id == '2':
            logger.info('handle complete')
            self.ui.pushButton_2.setEnabled(True)
            self.ui.pushButton_2.setText('Write')
            self.ui.pushButton_2.setStyleSheet("color: black")

            if str(self.data2) == '0':
                QMessageBox.information(self.mainwindow, 'Warning', 'Invalid dcfx format, please select correct dcfx')
                self.config_dialog_mgr.exec()
                return

        if self.id == '3':
            self.table_mgr.df = self.data2
            self.table_mgr.init_table_default()
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
        self.label_in_status_bar.setText("<A href='https://autoallegro.html'>https://autoallegro.html</a>")
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
    def __init__(self, ui, main_window, kwork_thread, config_dialog_mgr, table_mgr):
        self.ui = ui
        self.main_window = main_window
        self.kwork_thread = kwork_thread
        self.config_dialog_mgr = config_dialog_mgr
        self.table_mgr = table_mgr
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
    def on_button_clicked_modifier(self, a, b, c):

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
            if self.table_mgr.df is None:
                logger.info('df is none')
                return
            if self.table_mgr.df.empty:
                QMessageBox.information(self.main_window, 'Warning', 'Invalid xlsx format, please select correct xlsx')
                self.config_dialog_mgr.exec()
                return
            rvp_cus = {}
            for row in range(self.ui.tableWidget.rowCount()):
                for col in range(self.ui.tableWidget.columnCount()):
                    if row == 0:
                        continue
                    value = self.ui.tableWidget.item(row, col).text()
                    if col == 1 or col == 3:
                        rvp_cus[self.ui.tableWidget.item(row, col).text()] = self.ui.tableWidget.item(row,
                                                                                                      col + 1).text()
                    logger.info('row:' + str(row) + ',  col:' + str(col) + '\n' + value)

            case_sensitive = self.ui.checkBox.isChecked()
            logger.info('case_sensitive: ' + str(case_sensitive))
            self.ui.pushButton_2.setEnabled(False)
            self.ui.pushButton_2.setText('Processing...')
            self.ui.pushButton_2.setStyleSheet("color: red")
            self.kwork_thread.send_work_message([2, rvp_cus, case_sensitive, self.config_dialog_mgr.dcfx_path])

        pass


class Config_Dialog_Mgr(QDialog):
    xlsx_path = ''
    dcfx_path = ''
    xlsx_path_old = ''
    dcfx_path_old = ''
    signal_child_2_parent = pyqtSignal(str)
    def __init__(self, ui, kwork_thread, table_mgr):
        QDialog.__init__(self)
        self.kwork_thread = kwork_thread
        self.ui = ui
        self.table_mgr = table_mgr
        self.child=cfg_ui_dialog.Ui_Dialog()#子窗口的实例化
        self.child.setupUi(self)
        self.setWindowTitle('Configure')
        #self.child.label.setText("AutoAllegro (v0.2, Build 1)")

        self.ui.actionConfigure.triggered['bool'].connect(self.exec)
        self.child.buttonBox.accepted.connect(self.ok_pressed)
        self.child.buttonBox.rejected.connect(self.cancel_pressed)
        self.child.pushButton.clicked.connect(self.pushButton_on_click)
        self.child.pushButton_2.clicked.connect(self.pushButton_2_on_click)

        self.kwork_thread.signal_to_config_dialog.connect(self.emit_handler)
        self.kwork_thread.send_work_message([4, 'data_4'])

    def event(self, event):
        #logger.info('SubWindow got event type: '+ str(event.type()))
        if event.type() == QEvent.Show:
            logger.info("child dialog is shown!")
        return super().event(event)

    def emit_handler(self, param_1, param_2):
        logger.info('emit_handler: \n' + param_1 + '\n' + param_2)
        self.xlsx_path = self.xlsx_path_old = param_1
        self.dcfx_path = self.dcfx_path_old = param_2
        self.child.plainTextEdit.setPlainText(param_1)
        self.child.plainTextEdit_2.setPlainText(param_2)
        #self.table_mgr.init_table_default()
        if os.path.exists(self.xlsx_path):
            logger.info("auto load xlsx")
            self.kwork_thread.send_work_message([3, self.xlsx_path])
        else:
            logger.info('configured xlsx path does not exist')
        pass

    def cancel_pressed(self):
        logger.info('cancel_pressed')
        if self.xlsx_path_old != self.child.plainTextEdit.toPlainText():
            self.child.plainTextEdit.setPlainText(self.xlsx_path_old)
        if self.dcfx_path_old != self.child.plainTextEdit_2.toPlainText():
            self.child.plainTextEdit_2.setPlainText(self.dcfx_path_old)
        pass
    def ok_pressed(self):
        self.xlsx_path = self.xlsx_path_old = self.child.plainTextEdit.toPlainText()
        self.dcfx_path = self.dcfx_path_old = self.child.plainTextEdit_2.toPlainText()
        self.signal_child_2_parent.emit(self.xlsx_path)
        self.kwork_thread.send_work_message([5, self.xlsx_path, self.dcfx_path])
        '''
        if self.xlsx_path:
            self.signal_child_2_parent.emit(self.xlsx_path)
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

    def load_dcfx_file(self):
        opened_file_path = ''
        file_dialog_opened_file_path = QFileDialog.getOpenFileName(None, 'Select File', os.getcwd(), "Excel Files (*.dcfx);;All files (*.*)")
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
        file_dialog_opened_file_path = QFileDialog.getOpenFileName(None, 'Select File', os.getcwd(), "Excel Files (*.xlsx *.xls);;All files (*.*)")
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

class about_dialog_mgr(QDialog):
    def __init__(self, ui):
        QDialog.__init__(self)
        self.ui = ui
        self.child=Ui_Dialog()#子窗口的实例化
        self.child.setupUi(self)
        self.setWindowTitle('About AutoAllegro')
        self.child.label.setText("AutoAllegro (v0.2, Build 1)")
        self.child.label_2.setText("liukezhao@gmail.com")
        self.child.label_3.setText("<A href='https://autoallegro.html'>https://autoallegro.html</a>")
        self.child.label_3.setOpenExternalLinks(True)
        self.child.label_3.setToolTip("https:/autoallegro.html")

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
    def __init__(self, ui, main_window, kwork_thread):
        self.ui = ui
        self.main_window = main_window
        self.kwork_thread = kwork_thread
        self.df = None
        #self.init_table()
        #self.test_excel()

        #self.init_table_default()
        #self.kwork_thread.send_work_message([3, 'data_3'])

        self.ui.comboBox_3.addItem('LNL+T4+2230+PCIe4+CNVio3')

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

    def init_table_default(self, selected_columns=[]):
        #self.df = pd.read_excel(r'LNL+T4+2230+PCIe4+CNVio3.xlsx', sheet_name='Netname list', header=1)

        # Display an empty table
        if self.df.empty:
            #self.ui.tableWidget.clearContents()
            self.ui.tableWidget.clear()
            self.ui.tableWidget.setRowCount(0)
            self.ui.tableWidget.horizontalHeader().setVisible(False)
            return

        self.ui.tableWidget.clearContents()

        self.df = self.df.drop(self.df.columns[0], axis=1)
        nRows = len(self.df.index)
        nColumns = len(selected_columns) or len(self.df.columns)

        delCols = []
        for col in range(nColumns):
            if col == 0:
                continue
            item_str = str(self.df.iat[0, col])
            if item_str != 'Net Names on RVP' and item_str != 'Net Names on customer design':
                delCols.append(col)
        for idx, col in enumerate(delCols):
            self.df = self.df.drop(self.df.columns[col - idx], axis=1)

        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
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
                self.ui.tableWidget.setItem(row, col, item)
        # Enable sorting on the table
        # self.ui.tableWidget.setSortingEnabled(True)
        # Enable column moving by drag and drop
        self.ui.tableWidget.horizontalHeader().setSectionsMovable(True)

        self.ui.tableWidget.resizeColumnsToContents()




    def test_excel(self):
        import openpyxl

        # 读取XLSX文件
        workbook = openpyxl.load_workbook(r'c:\00_MyWorkspace\002_Documents\CNV\CNVi\Allegro\sample-1.xlsx')
        sheet = workbook.active

        workbook2 = openpyxl.load_workbook(r'c:\00_MyWorkspace\002_Documents\CNV\CNVi\Allegro\sample-3.xlsx')

        # 获取单元格的值
        cell_value = sheet['A1'].value
        pass
