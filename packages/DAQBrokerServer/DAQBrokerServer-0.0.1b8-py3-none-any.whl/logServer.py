import zmq
import os
import traceback
import logging
import datetime
from datetime import datetime
from supportFuncs import *


def logServer(port, base_dir, logFilename="logFile.log"):
    """ Logging server process, This process creates a local listening port that receives requests for event logging.

    :param port: (Integer) network port to listen for event logging requests
    :param base_dir: (String) path of the executable being called. This is for the use of a frozen function
    :param logFilename: (String) name of logFile. Defaults to ``logFile.log``

    .. warning::

            This is a long running process and blocks execution of the main task, it should therefore be called on a separate process.
    """
    logging.basicConfig(filename=os.path.join(base_dir, logFilename), level=logging.DEBUG, format='')
    logging.info(datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S.%f") +
                 " [LOGGER][INFO][logServer] : started logging server")
    context = zmq.Context()
    theSocket = context.socket(zmq.ROUTER)
    logLvls = {'info': logging.INFO, 'error': logging.ERROR, 'warning': logging.warning, 'debug': logging.debug}
    theSocket.bind("tcp://127.0.0.1:" + str(port))
    while True:
        #  Wait for next request from client
        message = False
        try:
            message = theSocket.recv_json()
            logReq = message
            if 'req' in logReq:
                if logReq['req'] == 'LOG':
                    if not (logReq['type'] == 'ERROR'):
                        if 'method' in logReq:
                            logMessage = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S.%f") + \
                                ' [' + logReq['process'] + '][' + logReq['method'] + '][' + logReq['type'] + '] : ' + logReq['message']
                        else:
                            logMessage = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S.%f") + \
                                ' [' + logReq['process'] + '][' + logReq['type'] + '] : ' + logReq['message']
                    else:
                        logMessage = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S.%f") + \
                            ' [' + logReq['process'] + '][' + logReq['type'] + '][' + logReq['filename'] + '][' + logReq['lineno'] + '][' + logReq['funname'] + '] : ' + logReq['line']
                    logging.info(logMessage)
            #Check file size for maximum size - default 10 MB
            statinfo = os.stat(os.path.join(base_dir, logFilename))
            if statinfo.st_size >= 10000000:
                with open(os.path.join(base_dir, logFilename), 'w'):
                    pass
        except Exception as e:
            if message:
                _, _, tb = sys.exc_info()
                tbResult = traceback.format_list(traceback.extract_tb(tb)[-1:])[-1]
                filename = tbResult.split(',')[0].replace('File', '').replace('"', '')
                lineno = tbResult.split(',')[1].replace('line', '')
                funname = tbResult.split(',')[2].replace('\n', '').replace(' in ', '')
                logMessage = datetime.utcnow().strftime("%Y/%m/%d %H:%M:%S.%f") + \
                    ' [LOGGER][ERROR][' + filename + '+][' + lineno + '][' + funname + '] : ' + str(e)
                logging.info(logMessage)
