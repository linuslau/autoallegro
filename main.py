from main_ui_qt5 import *
# from wew_about_ui_qt5 import *
from utility.software_mgr import *
from utility.klogger import KLogger
from utility.kappbase import *
from PyQt5.QtCore import Qt, QTimer

klogger = KLogger()
logger = klogger.getlogger()

if __name__ == '__main__':
    try:
        logger.info('Hello, Kezhao! Hello GenericSW!')
        app = QtWidgets.QApplication(sys.argv)

        # 创建并显示 Splash Screen
        splash_pix = QPixmap('./_internal/icon/logo_splash.png')  # 使用自己的图片路径
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setMask(splash_pix.mask())
        splash.show()

        MainWindow = QtWidgets.QMainWindow() # 创建窗体对象

        #QTimer.singleShot(2000, splash.close)  # 设置定时器，在2秒后关闭 Splash Screen

        ui = Ui_MainWindow() # 创建PyQt设计的窗体对象
        ui.setupUi(MainWindow) # 调用PyQt窗体的方法对窗体对象进行初始化设置
        splash.close()
        MainWindow.show() # 显示窗体
        kapp_base = KAppBase(ui, MainWindow, app)
        sys.exit(app.exec_()) # 程序关闭时退出进程
    except Exception as e:
        logger.error('Exception: main UI thread got error!!!', exc_info=True)
