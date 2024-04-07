from PyQt5.QtGui import QPixmap

from about_ui_qt5 import *
from utility.software_mgr import *
from utility.kworkthread import *
from utility.kmisc import *

class KAppBase(object):
    pass
    def __init__(self, ui, MainWindow):
        self.ui = ui
        self.mainwindow = MainWindow
        self.splash_check()

        self.mainwindow.setWindowTitle('GenericSW v0.1')

        self.kwork_thread = KWorkThread()
        self.kwork_thread.start()
        self.kwork_thread.signal_to_ui.connect(self.work_thread_signal_handler)

        self.ui_mgr = UI_Mgr(MainWindow)
        self.ui_mgr.splash_check()
        self.software_mgr = Software_Mgr('genericsw', 'GenericSW', MainWindow)
        self.software_mgr.check_software_version_background(self.ui_mgr)
        self.button_mgr = Button_Mgr(ui, MainWindow, self.kwork_thread)
        self.icon_mgr = Icon_Mgr(ui, MainWindow)
        self.about_window_mgr = About_Window_Mgr(ui)

        pass

    def __del__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def work_thread_signal_handler(self, param_1, param_2):

        print('ui slots received signal id: ' + param_1)
        print('ui slots received signal data: ' + param_2)

        self.id = param_1
        self.data = param_2

        status_bar_string = self.data

        status_bar_string = ' ui enqueue->thread dequeue, emit->ui slots get ' + status_bar_string

        self.mainwindow.statusBar().showMessage(status_bar_string, 10000)

        if self.id == 0:
            pass
        if self.id == 1:
            pass
        if self.id == 2:
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
        self.label_in_status_bar.setText("<A href='https://vmio.vip/genericsw.html'>https://vmio.vip/genericsw.html</a>")
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
    def __init__(self, ui, main_window, kwork_thread):
        self.ui = ui
        self.main_window = main_window
        self.kwork_thread = kwork_thread
        self.set_signal_connect()

    def set_signal_connect(self):
        self.ui.pushButton.clicked.connect(lambda: self.on_button_clicked_read(255, 255, 255))
        self.ui.pushButton_2.clicked.connect(lambda: self.on_button_clicked_modifier(255, 255, 255))
        pass

    def on_button_clicked_read(self, a, b, c):
        function_enter()
        self.kwork_thread.send_work_message([1, 'data_1'])
        function_exit()
        pass
    def on_button_clicked_modifier(self, a, b, c):
        self.kwork_thread.send_work_message([2, 'data_2'])
        pass

class About_Window_Mgr(QDialog):
    def __init__(self, ui):
        QDialog.__init__(self)
        self.ui = ui
        self.child=Ui_Dialog()#子窗口的实例化
        self.child.setupUi(self)
        self.setWindowTitle('About GenericSW')
        self.child.label.setText("GenericSW (v0.1, Build 1)")
        self.child.label_2.setText("liukezhao@gmail.com")
        self.child.label_3.setText("<A href='https://vmio.vip/genericsw.html'>https://vmio.vip/genericsw.html</a>")
        self.child.label_3.setOpenExternalLinks(True)
        self.child.label_3.setToolTip("https://vmio.vip/genericsw.html")

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