import platform
import os
import sqlite3
import string
import random
from subprocess import call
from subprocess import check_output
from supportFuncs import *


base_dir = '.'
if getattr(sys, 'frozen', False):
    base_dir = os.path.join(sys._MEIPASS)

def startBackup(path, backupInfo, localPath):
    """ Backup server main process. This process is responsible for gathering data files from remote DAQBroker clients and ensuring they are at their most recent versions. This process starts an `rsync`_ daemon instance specifically tailored for DAQBroker's needs.

    .. _rsync: https://rsync.samba.org/?

    :param path: (String) path of the current backups folder
    :param backupInfo: (`multiporcessing.Manager().list`_) process-shared dict with relevant backup information

    :returns: ``False`` in case a problem occurs

    .. warning::

            This is a long running process and blocks execution of the main task, it should therefore be called on a separate process.

    .. _multiporcessing.Manager().list: https://docs.python.org/2/library/multiprocessing.html#sharing-state-between-processes

    """
    allchar = string.ascii_letters + string.digits
    backupInfo["user"] = "daqbroker"
    backupInfo["pass"] = "".join(random.choice(allchar) for x in range(random.randint(8, 12)))
    backupInfo["port"] = 9999
    daqbrokerSettings.setupLocalVars(localPath)
    scoped = daqbrokerSettings.getScoped()
    session = scoped()
    globals = session.query(
        daqbrokerSettings.Global).filter_by(
        clock=session.query(
            func.max(
                daqbrokerSettings.Global.clock))).first()
    if not globals:
        globals = type('globalVar', (object,), {
            'clock': time.time(),
            'version': '0.1',
            'backupfolder': 'backups',
            'importfolder': 'uploads',
            'addonfolder': 'addons',
            'ntp': None,
            'remarks': {}})
    if(platform.system() == 'Windows'):  # Running on windows machine
        os.chdir(path)
        command = os.path.join("rsync --daemon --port=9999 --config=rsyncd.conf --no-detach --log-file=logFile.log")
        secretsFilePath = ''
        rsyncConfig = open('rsyncd.conf', 'w')
    else:
        command = os.path.join(
            "rsync --daemon --port=" +
            backupInfo["port"] +
            " --config=" +
            os.path.join(
                path,
                "rsyncd.conf") +
            " --no-detach --log-file=" +
            os.path.join(
                path,
                "logFile.log"))
        rsyncConfig = open(os.path.join(path, "rsyncd.conf"), 'w')
        secretsFilePath = path
    #print(os.path.join(base_dir, globals.backupfolder))
    if os.path.isabs(globals.backupfolder):
        backupFolder = convertFilePath(globals.backupfolder)
    else:
        backupFolder = convertFilePath(os.path.join(base_dir, globals.backupfolder))
    #print("THEFOLDER", backupFolder)
    if not os.path.isdir(os.path.join(base_dir, globals.backupfolder)):
        os.makedirs(os.path.join(base_dir, globals.backupfolder))
    secretsFileLocation = os.path.join(secretsFilePath, 'rsyncd.secrets')
    if backupFolder:
        secretsfh = open(secretsFileLocation, 'w')
        secretsfh.write(backupInfo["user"] + ':' + backupInfo["pass"])
        secretsfh.close()
        rsyncConfig.write("use chroot = false\n")
        rsyncConfig.write("log file = rsyncd.log\n")
        rsyncConfig.write("lock file = rsyncd.lock\n")
        rsyncConfig.write("[daqbroker]\n")
        rsyncConfig.write("   path = " + backupFolder + "\n")
        rsyncConfig.write("   comment = DAQBroker backup server\n")
        rsyncConfig.write("   strict modes = no\n")
        rsyncConfig.write("   auth users = daqbroker\n")
        rsyncConfig.write("   secrets file = " + secretsFileLocation + "\n")
        rsyncConfig.write("   read only = false\n")
        rsyncConfig.write("   list = false\n")
        rsyncConfig.write("   fake super = yes\n")
        #rsyncConfig.write("   use chroot = true\n")
        rsyncConfig.close()
        #command=os.path.join("rsync --daemon --port=9999 --config=rsyncd.conf --no-detach --log-file=logFile.log")
        call(command.split(' '))
    else:
        return False


def convertFilePath(path):
    """ Auxiliary function, used only in the case the opearating system is windows. Converts Windows style paths to their `cygpath`_ equivalent

    :param path: (String) path to be changed

    :returns: (String) cygpath-style path

    .. _cygpath: https://cygwin.com/cygwin-ug-net/cygpath.html

    """
    if(os.name == 'nt'):
        #tentative = check_output(['cygpath', path]).decode().strip('\n')
        if os.path.isabs(path):
            mainPath = check_output(['cygpath', path])
        else:
            mainPath = check_output(['cygpath', os.path.join(base_dir, path)])
        return mainPath.decode().strip('\n')
    else:
        return path
