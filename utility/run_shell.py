import subprocess
import os

from utility.kmisc import *
from utility.klogger import KLogger

klogger = KLogger()
logger = klogger.getlogger()
class Run_Powershell:
    def __init__(self):
        pass

    def run(self, cmd):
        completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
        logger.info('')
        logger.info("Powershell execution result: \n" + str(completed))
        logger.info('')
        return completed


class CommandException(Exception):
    pass

class Run_Shell:
    def __init__(self):
        pass

    def run(self,command):
        exitcode, output = subprocess.getstatusoutput(command)
        if exitcode != 0:
            raise CommandException(output)

        return output

    def execCmd(self, cmd):
        r = os.popen(cmd)
        text = r.read()
        r.close()
        return text


if __name__ == '__main__':

    run_ps = Run_Powershell()

    logger.info('===> test correct syntax:')
    hello_command = "Write-Host 'Hello Wolrd!'"
    hello_info = run_ps.run(hello_command)
    if hello_info.returncode != 0:
        logger.info("An error occured: %s", hello_info.stderr)
    else:
        logger.info("Hello command executed successfully!")

    logger.info("-----------------------------------------------------------------------------------------------")

    logger.info('===> test bad syntax:')

    bad_syntax_command = "Write-Hst 'Incorrect syntax command!'"
    bad_syntax_info = run_ps.run(bad_syntax_command)
    if bad_syntax_info.returncode != 0:
        logger.info("An error occured: %s", bad_syntax_info.stderr)
    else:
        logger.info("Bad syntax command executed successfully!")

    '''
    logger.info("-----------------------------------------------------------------------------------------------")
    logger.info('===> test get pcie topology:')

    pcie_topology_cmd = "(gwmi Win32_Bus -Filter 'DeviceID like \"PCI%\"').GetRelated('Win32_PnPEntity').GetDeviceProperties('DEVPKEY_Device_LocationInfo').deviceProperties | ft data,DeviceID"
    pcie_topology_info = run_ps.run(pcie_topology_cmd)
    if pcie_topology_info.returncode != 0:
        logger.info("pcie_topology_cmd An error occured: %s", pcie_topology_info.stderr)
    else:
        logger.info("pcie_topology_cmd executed successfully!" + str(pcie_topology_info.stdout))
    '''

    logger.info("-----------------------------------------------------------------------------------------------")
    logger.info('===> test get pcie topology:')
    pcie_topology_cmd_shell = "wmic path win32_pnpentity where \"deviceid like '%PCI%'\" get name,deviceid"
    run_shell = Run_Shell()
    pcie_topology_cmd_shell_info = run_shell.run_command(pcie_topology_cmd_shell)
    logger.info(pcie_topology_cmd_shell_info)


    logger.info("-----------------------------------------------------------------------------------------------")
    logger.info('===> test get pcie topology:')
    pcie_topology_lspci = resource_path(os.path.join("..\dependency\pcie", "lspci.exe -t -vv -nn"))
    logger.info('running_exe: ' + str(pcie_topology_lspci))
    run_shell = Run_Shell()
    pcie_topology_lspci_info = run_shell.run_command(pcie_topology_lspci)
    logger.info(pcie_topology_lspci_info)
