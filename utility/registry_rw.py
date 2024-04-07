#Python3 version of hugo24's snippet
import winreg
import os
from utility.klogger import KLogger

klogger = KLogger()
logger = klogger.getlog()

# reference start
REG_PATH = r"Control Panel\Mouse"
def set_reg(name, value):
    try:
        winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0, 
                                       winreg.KEY_WRITE)
        winreg.SetValueEx(registry_key, name, 0, winreg.REG_SZ, value)
        winreg.CloseKey(registry_key)
        return True
    except WindowsError:
        logger.error('set_reg()', exc_info=True)
        return False

def get_reg(name):
    try:
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH, 0,
                                       winreg.KEY_READ)
        value, regtype = winreg.QueryValueEx(registry_key, name)
        winreg.CloseKey(registry_key)
        return value
    except WindowsError:
        logger.error('get_reg()', exc_info=True)
        return None

#Example MouseSensitivity
#Read value 
logger.info (get_reg('MouseSensitivity'))

#Set Value 1/20 (will just write the value to reg, the changed mouse val requires a win re-log to apply*)
set_reg('MouseSensitivity', str(10))

#*For instant apply of SystemParameters like the mouse speed on-write, you can use win32gui/SPI
#http://docs.activestate.com/activepython/3.4/pywin32/win32gui__SystemParametersInfo_meth.html
# reference end

# reference start
def write(path, value, root=winreg.HKEY_CURRENT_USER, regtype=None):
    path, name = os.path.split(path)
    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE|winreg.KEY_READ) as key:
        with winreg.suppress(FileNotFoundError):
            regtype = regtype or winreg.QueryValueEx(key, name)[1]
        winreg.SetValueEx(key, name, 0, regtype or winreg.REG_DWORD if isinstance(value, int) else winreg.EG_SZ, str(value) if regtype==winreg.REG_SZ else value)

def write(path, value, root=winreg.HKEY_CURRENT_USER):
    path, name = os.path.split(path)
    with winreg.OpenKey(root, path, 0, winreg.KEY_WRITE) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)

def read(path, root=winreg.HKEY_CURRENT_USER):
    path, name = os.path.split(path)
    with winreg.suppress(FileNotFoundError), winreg.OpenKey(root, path) as key:
        return winreg.QueryValueEx(key, name)[0]
# reference start

class KRegistry(object):
    def __init__(self, restore_state=False):
        self.m_backup = {}
        self.m_restore_state = restore_state

    def get_key(self, hkey, subkey, access, create_if_doesnt_exist=True):
        created_key = False
        registry_key = None
        try:
            registry_key = winreg.OpenKey(hkey, subkey, 0, access)
        except WindowsError:
            try:
                if create_if_doesnt_exist:
                    registry_key = winreg.CreateKey(hkey, subkey)
                    if registry_key not in self.m_backup:
                        self.m_backup[registry_key] = ({}, (hkey, subkey))
                else:
                    registry_key = None
            except WindowsError:
                if registry_key:
                    self.close_key(registry_key)
                raise Exception('Registry does not exist and could not be created.')
                logger.error('Registry does not exist and could not be created.', exc_info=True)
            logger.error('winreg.OpenKey', exc_info=True)
        return registry_key   

    def close_key(self, registry_key):
        closed = False
        if registry_key:
            try:
                winreg.CloseKey(registry_key)
                closed = True
            except:
                closed = False
                logger.error('winreg.CloseKey', exc_info=True)
        return closed          

    def get_reg_value(self, hkey, subkey, name):
        value = None
        registry_key = self.get_key(hkey, subkey, winreg.KEY_READ, False)
        if registry_key:
            try:
                value, _ = winreg.QueryValueEx(registry_key, name)
            except WindowsError:
                value = None
                logger.error('winreg.QueryValueEx', exc_info=True)
            finally:
                self.close_key(registry_key)
        return value

    def set_reg_value(self, hkey, subkey, name, type, value):
        registry_key = self.get_key(hkey, subkey, winreg.KEY_WRITE, True)
        backed_up = False
        was_set = False
        if registry_key:
            if self.m_restore_state:
                if registry_key not in self.m_backup:
                    self.m_backup[registry_key] = ({}, None)
                existing_value = self.get_reg_value(hkey, subkey, name)
                if existing_value:
                    self.m_backup[registry_key][0][name] = (existing_value, type, False)
                else:
                    self.m_backup[registry_key][0][name] = (None, None, True)
                backed_up = True                
            try:
                winreg.SetValueEx(registry_key, name, 0, type, value)
                was_set = True
            except WindowsError:
                was_set = False
                logger.error('winreg.SetValueEx', exc_info=True)
            finally:
                if not backed_up:
                    self.close_key(registry_key)
        return was_set

    def restore_state(self):
        if self.m_restore_state:
            for registry_key, data in self.m_backup.iteritems():
                backup_dict, key_info = data
                try:
                    for name, backup_data in backup_dict.iteritems():
                        value, type, was_created = backup_data
                        if was_created:
                            logger.info(registry_key, name)
                            winreg.DeleteValue(registry_key, name)
                        else:
                            winreg.SetValueEx(registry_key, name, 0, type, value)
                    if key_info:
                        hkey, subkey = key_info
                        winreg.DeleteKey(hkey, subkey)
                except:
                    raise Exception('Could not restore value')
                    logger.error('Could not restore value', exc_info=True)
                self.close_key(registry_key)

    def __del__(self):
        if self.m_restore_state:
            self.restore_state()