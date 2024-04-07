from main_ui_qt5 import *
# from wew_about_ui_qt5 import *
from utility.software_mgr import *
from utility.klogger import KLogger
from utility.kappbase import *

klogger = KLogger()
logger = klogger.getlog()

if __name__ == '__main__':
    logger.info('Hello, Kezhao! Hello GenericSW!')
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow() # 创建窗体对象
    ui = Ui_MainWindow() # 创建PyQt设计的窗体对象
    ui.setupUi(MainWindow) # 调用PyQt窗体的方法对窗体对象进行初始化设置
    MainWindow.show() # 显示窗体
    kapp_base = KAppBase(ui,MainWindow)
    sys.exit(app.exec_()) # 程序关闭时退出进程
