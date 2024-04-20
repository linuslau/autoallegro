# from busybox_registry_rw import *
from utility.run_shell import *
from utility.ktime import *
from utility.klogger import KLogger
from utility.kappregistry import *


import webbrowser
import requests
import threading

from PyQt5.QtWidgets import *

klogger = KLogger()
logger = klogger.getlogger()

class Software_Mgr:
    proxiesY = {
        "http": "http://xxx:yyy",
        "https": "http://xxx:yyy",
    }

    def __init__(self, project_name, app_name, main_window):
        self.main_window = main_window
        self.project_name = project_name
        self.app_name = app_name
        self.app_exe_path = ''
        pass

    def check_software_version(self, *args):
        ui_mgr = args[0]
        if self.software_need_upgrade():
            logger.info('software_need_upgrade: Yes, exit program immediately')
            ui_mgr.splash_check()

            os._exit(1)
        else:
            logger.info('software_need_upgrade: No, continue\n\n')
    def check_software_version_background(self, ui_mgr):
        try:
            t1 = threading.Thread(target=self.check_software_version, args=(ui_mgr,))
            t1.setDaemon(True)
            t1.start()
        except Exception as e:
            logger.info('Exception: unable to start thread')
            logger.error('Exception: unable to start thread', exc_info=True)
    def software_need_upgrade(self):
        need_update = 0

        kapp_registry = KAppRegistry('GenericSW')
        if kapp_registry.registry_rw_is_version_check_disabled():
            logger.info('software check registry disabled, continue with no check')
        else:
            logger.info('software check registry NOT disabled, continue check version')
            # first check if there is a new version
            if 1 == self.there_is_a_new_version():
                logger.info('there is a new version, exit\n')
                need_update = 1
            else:
                # secondly, check app itself exceed or not
                logger.info('there is NO new version, continue \n')
                if self.is_software_expired():
                    logger.info('software is expired, exit !!!')
                    need_update = 1
                else:
                    logger.info('software is NOT expired, continue')
                    need_update = 0

        logger.info('software_need_upgrade: ' + str(need_update))
        return need_update

    def there_is_a_new_version(self):
        latest_release_time = ''
        lastest_release_download_url = ''

        logger.info('enter there_is_a_new_version\n')

        if self.is_xxxxx_network() == 1:
            logger.info('\n\n!!!! xxxxx network Yes !!!!\n\n')
            try:
                base_url = 'http://sourceforge.net/projects/' + self.project_name + '/best_release.json'
                response = requests.get(f"{base_url}", proxies=self.proxiesY, timeout=2)
                app_web = response.json()
                if app_web['release'] is not None:
                    latest_release_time = app_web['release']['date']
                    lastest_release_download_url = app_web['release']['url']

            except Exception as ex:
                logger.error('Exception: requests.get URL', exc_info=True)

        else:
            logger.info('\n\n!!!! xxxxx network NO !!!!\n\n')
            try:
                base_url = 'http://sourceforge.net/projects/' + self.project_name + '/best_release.json'
                response = requests.get(f"{base_url}", timeout=2)
                app_web = response.json()
                if app_web['release'] is not None:
                    latest_release_time = app_web['release']['date']
                    lastest_release_download_url = app_web['release']['url']

            except Exception as ex:
                logger.error('Exception: requests.get URL', exc_info=True)

        if latest_release_time == '':
            logger.info('latest_release_time is NULL, return 0 \n')
            return 0
        else:
            logger.info('latest_release_time is: ' + str(latest_release_time))
            self.app_exe_path = sys.argv[0]
            create_time = os.path.getmtime(os.path.abspath(self.app_exe_path))
            logger.info('check file: ' + self.app_exe_path)
            create_time_localtime = time.localtime(create_time)
            logger.info('check file create_time: ' + str(create_time_localtime))

            y = int(latest_release_time[0:4])
            mo = int(latest_release_time[5:7])
            d = int(latest_release_time[8:10])
            h = int(latest_release_time[11:13])
            mi = int(latest_release_time[14:16])
            s = int(latest_release_time[17:19])
            latest_release_time_datetime = datetime.datetime(y, mo, d, h, mi, s)

            create_time_datetime = datetime.datetime(create_time_localtime.tm_year, create_time_localtime.tm_mon,
                                                     create_time_localtime.tm_mday, create_time_localtime.tm_hour,
                                                     create_time_localtime.tm_min, create_time_localtime.tm_sec)

            logger.info('latest_release_time_datetime: ' + str(latest_release_time_datetime))
            logger.info('create_time_datetime: ' + str(create_time_datetime))

            # as latest_release_time_datetime in sourceforge is UTC time...
            create_time_datetime_utc = local2utc(create_time_datetime)
            delta_day = (latest_release_time_datetime - create_time_datetime_utc).days
            logger.info('Network Check Delta_day: ' + str(delta_day))

            if delta_day > 1:

                webbrowser.open_new_tab(lastest_release_download_url)

                result = QMessageBox.question(self.main_window, 'Notice',
                                              'Latest ' + self.app_name + ' version downloaded.\n'
                                              'Press "Yes" to check the change of new release.',
                                              QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                if result == QMessageBox.Yes:
                    webbrowser.open_new_tab('https://vmio.vip/genericsw.html')
                else:
                    pass

                return 1

        logger.info('exit there_is_a_new_version, return 0 \n')
        return 0

    def is_software_expired(self):
        utc_time_now = datetime.datetime.utcfromtimestamp(time.time())
        utc_time_filename = resource_path(os.path.join("dependency", "utc_time.txt"))
        with open(utc_time_filename, 'r') as r:
            build_utc_time = r.readline()
        y = int(build_utc_time[0:4])
        mo = int(build_utc_time[5:7])
        d = int(build_utc_time[8:10])
        h = int(build_utc_time[11:13])
        mi = int(build_utc_time[14:16])
        s = int(build_utc_time[17:19])

        utc_time_build_software = datetime.datetime(y, mo, d, h, mi, s)
        delta_day = (utc_time_now - utc_time_build_software).days

        logger.info('utc_time_now: ' + str(utc_time_now))
        logger.info('create_time_localtime_datetime_utc: ' + str(utc_time_build_software))

        expired_time_localtime_datetime = utc_time_build_software + datetime.timedelta(days=60)

        logger.info('Software expiration check: \n')
        logger.info('Local time - Build time, Delta_day: ' + str(delta_day))
        if utc_time_now >= expired_time_localtime_datetime:
            logger.info('software survived for 30 days, stop it \n')
            QMessageBox.information(self.main_window, 'Warning',
                                    self.app_name + ' has expired on ' + datetime.datetime.strftime(expired_time_localtime_datetime, "%Y/%m/%d") + '.' + "<br>Visit <A href='https://vmio.vip/um.html'>https://vmio.vip/um.html</a>" + ' for latest version.')
            # msg_box.exec_()
            return 1
        else:
            logger.info('software survived less than specified days (30), continue \n')
            return 0

    def is_software_expired_based_on_modified_name(self):

        utc_time_now = datetime.datetime.utcfromtimestamp(time.time())
        utc_time_filename = resource_path(os.path.join("dependency", "utc_time.txt"))

        create_time = os.path.getmtime(os.path.abspath(self.app_exe_path))
        logger.info('check file: ' + self.app_exe_path)
        create_time_localtime = time.localtime(create_time)
        logger.info('check file create_time: ' + str(create_time_localtime))

        create_time_localtime_datetime = datetime.datetime(create_time_localtime.tm_year, create_time_localtime.tm_mon,
                                                 create_time_localtime.tm_mday, create_time_localtime.tm_hour,
                                                 create_time_localtime.tm_min, create_time_localtime.tm_sec)

        create_time_localtime_datetime_utc = local2utc(create_time_localtime_datetime)

        expired_time_localtime_datetime = create_time_localtime_datetime + datetime.timedelta(days=50)

        delta_day = (utc_time_now - create_time_localtime_datetime_utc).days

        logger.info('utc_time_now: ' + str(utc_time_now))
        logger.info('create_time_localtime_datetime_utc: ' + str(create_time_localtime_datetime_utc))

        logger.info('Software expiration check: \n')
        logger.info('Local time - Build time, Delta_day: ' + str(delta_day))
        if utc_time_now >= expired_time_localtime_datetime:
            logger.info('software survived for 30 days, stop it \n')
            QMessageBox.information(self.main_window, 'Warning',
                                    self.app_name + ' has expired on ' + datetime.datetime.strftime(expired_time_localtime_datetime, "%Y/%m/%d") + '.' + "<br>Visit <A href='https://vmio.vip/genericsw.html'>https://vmio.vip/genericsw.html</a>" + ' for latest version.')
            # msg_box.exec_()
            return 1
        else:
            logger.info('software survived less than specified days (30), continue \n')
            return 0

    def is_xxxxx_network(self):
        cmd = "ipconfig"
        run_shell = Run_Shell()
        ipconfig_result = run_shell.execCmd(cmd)
        del run_shell
        for line in ipconfig_result.splitlines():
            logger.info(str(line))
            if line.find('.xxxxx.com') != -1:
                return 1
        return 0
