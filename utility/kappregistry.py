from utility.registry_rw import *
from utility.klogger import KLogger

klogger = KLogger()
logger = klogger.getlogger()

class KAppRegistry(object):
    pass
    def __init__(self, app_name):
        self.app_name = app_name
        pass

    def __del__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    #    @staticmethod
    def registry_rw_is_version_check_disabled(self, value_name='Disable_Version_Check'):
        key = self.app_name
        logger.info('check Disable_Version_Check')
        version_check_disabled = 0
        kregistry = KRegistry()
        version_check_disabled = kregistry.get_reg_value(winreg.HKEY_LOCAL_MACHINE, 'Software\\' + key, value_name)
        del kregistry
        return version_check_disabled